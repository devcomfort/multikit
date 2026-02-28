"""Remote registry client — fetches kits from raw.githubusercontent.com."""

from __future__ import annotations

import asyncio
import random
import socket
import ssl
from collections import defaultdict
from urllib.parse import urlparse

import aiohttp

from multikit.models.config import NetworkConfig
from multikit.models.kit import Manifest, Registry

USER_AGENT = "multikit/0.1.0"


class RemoteFetchError(Exception):
    """Raised when remote fetch fails after all retries."""

    def __init__(self, message: str, url: str, attempts: int):
        super().__init__(message)
        self.url = url
        self.attempts = attempts


class HostUnreachableError(Exception):
    """Raised when a host is determined to be unreachable after consecutive errors."""

    def __init__(self, host: str, error_type: str, consecutive_failures: int):
        super().__init__(
            f"Host {host} unreachable: {error_type} ({consecutive_failures} consecutive failures)"
        )
        self.host = host
        self.error_type = error_type
        self.consecutive_failures = consecutive_failures


class RemoteClient:
    """Async HTTP client with retry/backoff and bounded concurrency."""

    # Track consecutive DNS/TLS errors per host for early termination
    _host_error_tracker: dict[str, list[tuple[str, Exception]]] = defaultdict(list)

    def __init__(
        self,
        network_config: NetworkConfig | None = None,
        base_url: str | None = None,
        session: aiohttp.ClientSession | None = None,
    ):
        self.network = network_config or NetworkConfig()
        self.base_url = base_url
        self._session: aiohttp.ClientSession | None = session
        self._external_session = session is not None
        # Per-instance error tracking
        self._host_errors: dict[str, list[tuple[str, Exception]]] = defaultdict(list)

    async def close(self) -> None:
        """Close the session if we created it."""
        if self._session and not self._session.closed and not self._external_session:
            await self._session.close()

    def _get_host(self, url: str) -> str:
        """Extract host from URL."""
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _is_dns_tls_error(self, error: Exception) -> bool:
        """Check if error is DNS/TLS related (connection-level)."""
        # aiohttp connection errors (includes DNS, TLS, connection refused, etc.)
        if isinstance(error, aiohttp.ClientConnectorError):
            return True
        # aiohttp ClientConnectionError (includes DNS, TLS, connection refused, etc.)
        if isinstance(error, aiohttp.ClientConnectionError):
            return True
        # DNS errors
        if isinstance(error, socket.gaierror):
            return True
        # SSL/TLS errors
        if isinstance(error, ssl.SSLError):
            return True
        # Connection timeout
        if isinstance(error, aiohttp.ServerTimeoutError):
            return True
        return False

    def _check_host_unreachable(self, url: str, error: Exception) -> bool:
        """Check if host should be marked unreachable due to consecutive DNS/TLS errors.

        Returns True if host is unreachable and should trigger early termination.
        """
        if not self._is_dns_tls_error(error):
            # Clear error history for non-DNS/TLS errors
            host = self._get_host(url)
            self._host_errors[host] = []
            return False

        host = self._get_host(url)
        error_type = type(error).__name__

        # Add this error to the host's error history
        self._host_errors[host].append((error_type, error))

        # Keep only recent errors (last 3)
        if len(self._host_errors[host]) > 3:
            self._host_errors[host] = self._host_errors[host][-3:]

        # Check if we have 3 consecutive errors of the same type
        recent_errors = (
            self._host_errors[host][-3:] if len(self._host_errors[host]) >= 3 else []
        )
        if len(recent_errors) == 3:
            error_types = [et for et, _ in recent_errors]
            if error_types.count(error_types[0]) == 3:
                # 3 consecutive errors of the same type - mark host as unreachable
                raise HostUnreachableError(host, error_types[0], 3)

        return False

    def _clear_host_errors(self, url: str) -> None:
        """Clear error history for a host after successful request."""
        host = self._get_host(url)
        self._host_errors[host] = []

    def _get_retry_after_delay(self, headers: dict) -> float | None:
        """Extract Retry-After header value as seconds.

        Returns None if header not present or invalid.
        """
        retry_after = headers.get("Retry-After")
        if not retry_after:
            return None

        try:
            # Retry-After can be seconds (int) or HTTP-date
            # For simplicity, we handle seconds only
            delay = float(retry_after)
            return delay if delay >= 0 else None
        except (ValueError, TypeError):
            return None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Lazy session creation."""
        if self._session is not None and not self._session.closed:
            return self._session

        # Create new session only if not provided externally
        if not self._external_session:
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            connector = aiohttp.TCPConnector(
                limit=self.network.max_concurrency,
                force_close=True,
            )
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers={"User-Agent": USER_AGENT},
            )

        if self._session is None:
            raise RuntimeError("No session available and cannot create one")

        return self._session

    async def _fetch_with_retry(
        self, url: str, method: str = "GET", **kwargs
    ) -> aiohttp.ClientResponse:
        """Fetch URL with exponential backoff + jitter."""
        last_error: Exception | None = None

        for attempt in range(self.network.max_retries):
            try:
                session = await self._get_session()
                # Don't use async with - return response directly
                resp = await session.request(method, url, **kwargs)

                # Handle 429 with Retry-After header
                if resp.status == 429:
                    retry_after = self._get_retry_after_delay(dict(resp.headers))
                    if retry_after is not None:
                        if retry_after > 60:
                            # Retry-After > 60s: immediate failure
                            await resp.release()
                            raise RemoteFetchError(
                                f"Rate limited with Retry-After={retry_after}s (>60s threshold)",
                                url,
                                attempt + 1,
                            )
                        # Wait for Retry-After duration before retry
                        await resp.release()
                        if attempt < self.network.max_retries - 1:
                            await asyncio.sleep(retry_after)
                        continue
                    # No valid Retry-After, treat as regular 429
                    await resp.release()
                    if attempt < self.network.max_retries - 1:
                        delay = self._calculate_delay(attempt)
                        await asyncio.sleep(delay)
                    continue

                # Check for other error statuses
                if resp.status >= 400:
                    # Release the response
                    await resp.release()
                    # Raise error to be caught by except block
                    raise aiohttp.ClientResponseError(
                        request_info=resp.request_info,
                        history=resp.history,
                        status=resp.status,
                        message=str(resp.reason) if resp.reason else "",
                        headers=resp.headers,
                    )

                # Success
                self._clear_host_errors(url)
                return resp

            except HostUnreachableError:
                # Re-raise immediately - don't retry
                raise
            except (aiohttp.ClientError, socket.gaierror, ssl.SSLError) as e:
                last_error = e

                # Check for DNS/TLS consecutive errors -> early termination
                self._check_host_unreachable(url, e)

                # Don't retry on 4xx (except 429)
                if (
                    isinstance(e, aiohttp.ClientResponseError)
                    and 400 <= e.status < 500
                    and e.status != 429
                ):
                    # Re-raise 4xx errors immediately without retry
                    raise

                # Retry with backoff for 5xx and connection errors
                if attempt < self.network.max_retries - 1:
                    delay = self._calculate_delay(attempt)
                    await asyncio.sleep(delay)

        error_message = str(last_error) if last_error else "Unknown error"
        raise RemoteFetchError(
            f"Failed after {self.network.max_retries} attempts: {error_message}",
            url,
            self.network.max_retries,
        )

    def _calculate_delay(self, attempt: int) -> float:
        """Calculate exponential backoff delay with jitter."""
        base_delay = self.network.retry_base_delay
        max_delay = self.network.retry_max_delay
        exponent = min(attempt, 3)  # Cap at 2^3 = 8x base
        delay = base_delay * (2**exponent)
        # Add jitter (±20%)
        jitter = delay * 0.2 * (2 * random.random() - 1)
        result = min(delay + jitter, max_delay)
        return float(result)

    async def fetch_registry(self, registry_url: str) -> Registry:
        """Fetch registry.json from remote."""
        url = f"{registry_url}/registry.json"
        resp = await self._fetch_with_retry(url)
        # raise_for_status() is now handled in _fetch_with_retry
        data = await resp.json()
        return Registry.model_validate(data)

    async def fetch_manifest(self, registry_url: str, kit_name: str) -> Manifest:
        """Fetch manifest.json for a specific kit."""
        url = f"{registry_url}/{kit_name}/manifest.json"
        resp = await self._fetch_with_retry(url)
        # raise_for_status() is now handled in _fetch_with_retry
        data = await resp.json()
        return Manifest.model_validate(data)

    async def fetch_file(
        self, registry_url: str, kit_name: str, subdir: str, filename: str
    ) -> str:
        """Fetch a single file content from remote."""
        url = f"{registry_url}/{kit_name}/{subdir}/{filename}"
        resp = await self._fetch_with_retry(url)
        # raise_for_status() is now handled in _fetch_with_retry
        return await resp.text()

    async def fetch_files_concurrent(
        self,
        registry_url: str,
        kit_name: str,
        files: list[tuple[str, str]],
    ) -> dict[tuple[str, str], str]:
        """Fetch multiple files with bounded concurrency.

        Args:
            registry_url: Base URL
            kit_name: Kit name
            files: List of (subdir, filename) pairs

        Returns:
            Dict mapping (subdir, filename) -> content
        """
        semaphore = asyncio.Semaphore(self.network.max_concurrency)

        async def fetch_one(subdir: str, filename: str) -> tuple[tuple[str, str], str]:
            async with semaphore:
                content = await self.fetch_file(
                    registry_url, kit_name, subdir, filename
                )
                return ((subdir, filename), content)

        tasks = [fetch_one(subdir, filename) for subdir, filename in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results, raising on first error
        fetched: dict[tuple[str, str], str] = {}
        for result in results:
            if isinstance(result, BaseException) and not isinstance(result, bool):
                if isinstance(result, Exception):
                    raise result
                raise RuntimeError(f"Unexpected exception type: {type(result)}")
            key, content = result
            fetched[key] = content

        return fetched


# Module-level async functions for backward compatibility
async def fetch_registry(registry_url: str) -> Registry:
    """Fetch registry.json from remote."""
    client = RemoteClient()
    try:
        return await client.fetch_registry(registry_url)
    finally:
        await client.close()


async def fetch_manifest(registry_url: str, kit_name: str) -> Manifest:
    """Fetch manifest.json for a specific kit."""
    client = RemoteClient()
    try:
        return await client.fetch_manifest(registry_url, kit_name)
    finally:
        await client.close()


async def fetch_file(
    registry_url: str, kit_name: str, subdir: str, filename: str
) -> str:
    """Fetch a single file content from remote."""
    client = RemoteClient()
    try:
        return await client.fetch_file(registry_url, kit_name, subdir, filename)
    finally:
        await client.close()
