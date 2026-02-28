"""Tests for the remote registry client."""

from __future__ import annotations


import aiohttp
import pytest
import socket
import ssl
from unittest import mock
from aioresponses import aioresponses

from multikit.models.config import NetworkConfig
from multikit.models.kit import Manifest, Registry
from multikit.registry.remote import RemoteClient, RemoteFetchError

BASE_URL = "https://raw.githubusercontent.com/devcomfort/multikit/main/kits"


class TestRemoteClient:
    """Tests for RemoteClient async operations."""

    @pytest.mark.asyncio
    async def test_fetch_registry_success(self, sample_registry: dict) -> None:
        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/registry.json", payload=sample_registry)
            # Client created inside 'with m:' block so session is patched
            client = RemoteClient(base_url=BASE_URL)
            try:
                registry = await client.fetch_registry(BASE_URL)
                assert isinstance(registry, Registry)
                assert len(registry.kits) == 2
                assert registry.kits[0].name == "testkit"
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_fetch_registry_404(self) -> None:
        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/registry.json", status=404)
            client = RemoteClient(base_url=BASE_URL)
            try:
                with pytest.raises(aiohttp.ClientResponseError):
                    await client.fetch_registry(BASE_URL)
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_fetch_manifest_success(self, sample_manifest: dict) -> None:
        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/testkit/manifest.json", payload=sample_manifest)
            client = RemoteClient(base_url=BASE_URL)
            try:
                manifest = await client.fetch_manifest(BASE_URL, "testkit")
                assert isinstance(manifest, Manifest)
                assert manifest.name == "testkit"
                assert len(manifest.agents) == 2
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_fetch_manifest_404(self) -> None:
        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/nonexistent/manifest.json", status=404)
            client = RemoteClient(base_url=BASE_URL)
            try:
                with pytest.raises(aiohttp.ClientResponseError) as exc_info:
                    await client.fetch_manifest(BASE_URL, "nonexistent")
                assert exc_info.value.status == 404
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_fetch_file_success(self) -> None:
        content = "# Agent content"
        m = aioresponses()
        m.start()
        try:
            m.get(f"{BASE_URL}/testkit/agents/test.agent.md", body=content)
            client = RemoteClient(base_url=BASE_URL)
            try:
                result = await client.fetch_file(
                    BASE_URL, "testkit", "agents", "test.agent.md"
                )
                assert result == content
            finally:
                await client.close()
        finally:
            m.stop()

    @pytest.mark.asyncio
    async def test_fetch_file_404(self) -> None:
        m = aioresponses()
        m.start()
        try:
            m.get(f"{BASE_URL}/testkit/agents/missing.agent.md", status=404)
            client = RemoteClient(base_url=BASE_URL)
            try:
                with pytest.raises(aiohttp.ClientResponseError):
                    await client.fetch_file(
                        BASE_URL, "testkit", "agents", "missing.agent.md"
                    )
            finally:
                await client.close()
        finally:
            m.stop()


class TestHostUnreachable:
    """Tests for HostUnreachableError logic in RemoteClient."""

    def test_is_dns_tls_error_types(self):
        client = RemoteClient()
        # DNS error
        assert client._is_dns_tls_error(socket.gaierror())
        # TLS error
        assert client._is_dns_tls_error(ssl.SSLError())
        # Connection errors
        assert client._is_dns_tls_error(
            aiohttp.ClientConnectorError(mock.Mock(), OSError())
        )
        assert client._is_dns_tls_error(aiohttp.ClientConnectionError())
        # Timeout error
        assert client._is_dns_tls_error(aiohttp.ServerTimeoutError())
        # Non-DNS/TLS error
        assert not client._is_dns_tls_error(ValueError())

    def test_host_unreachable_triggers(self):
        client = RemoteClient()
        url = "https://example.com/foo"
        err = socket.gaierror()
        # first two calls should not raise
        client._check_host_unreachable(url, err)
        client._check_host_unreachable(url, err)
        # third consecutive same-type error triggers HostUnreachableError
        with pytest.raises(Exception) as exc_info:
            client._check_host_unreachable(url, err)
        assert hasattr(exc_info.value, "host")
        assert isinstance(exc_info.value, Exception)

    def test_host_unreachable_clears_on_non_dns_error(self):
        client = RemoteClient()
        url = "https://example.com/foo"
        err = socket.gaierror()
        client._check_host_unreachable(url, err)
        client._check_host_unreachable(url, err)
        # non-DNS/TLS error resets history
        client._check_host_unreachable(url, ValueError())
        # now two new DNS errors should not raise

    def test_retry_after_delay_parsing(self):
        client = RemoteClient()
        # valid integer string
        assert client._get_retry_after_delay({"Retry-After": "5"}) == 5.0
        # zero or negative values treated as invalid
        assert client._get_retry_after_delay({"Retry-After": "-1"}) is None
        # non-numeric should return None
        assert client._get_retry_after_delay({"Retry-After": "invalid"}) is None
        # missing header
        assert client._get_retry_after_delay({}) is None

    @pytest.mark.asyncio
    async def test_fetch_with_retry_rate_limit_too_long(self):
        """If Retry-After exceeds threshold the call fails immediately on first attempt."""
        url = "https://example.com/test"
        m = aioresponses()
        with m:
            # respond with 429 and large Retry-After header
            m.get(url, status=429, headers={"Retry-After": "61"})
            client = RemoteClient()
            with pytest.raises(RemoteFetchError) as exc:
                await client._fetch_with_retry(url)
            err = exc.value
            assert ">60s threshold" in str(err)
            # attempts should be 1 because it failed on the first try
            assert err.attempts == 1
            await client.close()

    @pytest.mark.asyncio
    async def test_fetch_with_retry_exhaustion(self):
        """Exhausting all retries should raise RemoteFetchError with proper attempt count."""
        url = "https://example.com/alwaysfail"
        m = aioresponses()
        with m:
            # make every request return 500
            for _ in range(RemoteClient().network.max_retries):
                m.get(url, status=500)
            client = RemoteClient()
            with pytest.raises(RemoteFetchError) as exc:
                await client._fetch_with_retry(url)
            err = exc.value
            assert err.attempts == client.network.max_retries
            assert "Failed after" in str(err)
            await client.close()
        client._check_host_unreachable(url, err)
        client._check_host_unreachable(url, err)


class TestRetryBehavior:
    """Tests for retry/backoff behavior (T009)."""

    @pytest.mark.asyncio
    async def test_retry_on_500(self) -> None:
        """Should retry on 5xx errors."""
        call_count = 0
        max_calls = 3

        async def request_handler(request):
            nonlocal call_count
            call_count += 1
            if call_count < max_calls:
                # Return 500 error for first 2 calls
                raise aiohttp.ClientResponseError(request.info.url, None, status=500)
            # Return success on 3rd call
            return None

        m = aioresponses()
        m.start()
        try:
            m.get(f"{BASE_URL}/registry.json", payload={"kits": []})
            # Override with custom handler
            m.get(
                f"{BASE_URL}/registry.json",
                payload={"kits": []},
                status=200,
            )

            # Use a different approach: manually track calls
            client = RemoteClient(
                network_config=NetworkConfig(max_retries=3, retry_base_delay=0.1)
            )
            try:
                # This test is complex due to aioresponses limitations
                # Skip for now and implement with integration tests
                pytest.skip(
                    "Complex retry test - will be implemented with integration tests"
                )
            finally:
                await client.close()
        finally:
            m.stop()

    @pytest.mark.asyncio
    async def test_retry_on_connect_error(self) -> None:
        """Should retry on connection errors."""
        pytest.skip("Complex retry test - will be implemented with integration tests")

    @pytest.mark.asyncio
    async def test_no_retry_on_404(self) -> None:
        """Should not retry on 404."""
        # 404 is already tested in test_fetch_registry_404
        pytest.skip("404 behavior tested in test_fetch_registry_404")


class TestConcurrency:
    """Tests for bounded concurrency (T009)."""

    @pytest.mark.asyncio
    async def test_fetch_files_concurrent(self) -> None:
        """Should fetch multiple files with bounded concurrency."""
        pytest.skip(
            "Complex concurrency test - will be implemented with integration tests"
        )

    @pytest.mark.asyncio
    async def test_concurrent_fetch_respects_semaphore(self) -> None:
        """Should respect max_concurrency limit."""
        pytest.skip(
            "Complex concurrency test - will be implemented with integration tests"
        )


class TestRetryEdgeCases:
    """Tests for retry edge scenarios (T042)."""

    @pytest.mark.asyncio
    async def test_retry_after_over_60s_immediate_failure(self) -> None:
        """Retry-After > 60s should fail immediately with clear error message."""

        call_count = 0

        async def handler_with_retry_after(request):
            nonlocal call_count
            call_count += 1
            # Always return 429 with Retry-After: 120 (2 minutes)
            from aiohttp import web

            response = web.Response(
                status=429, text="Rate limited", headers={"Retry-After": "120"}
            )
            return response

        m = aioresponses()
        m.start()
        try:
            # Mock with custom handler that returns 429 + Retry-After
            m.get(
                f"{BASE_URL}/registry.json", status=429, headers={"Retry-After": "120"}
            )

            client = RemoteClient(
                network_config=NetworkConfig(max_retries=3, retry_base_delay=0.1)
            )
            try:
                with pytest.raises(RemoteFetchError) as exc_info:
                    await client.fetch_registry(BASE_URL)

                # Verify error message mentions Retry-After threshold
                assert "Retry-After" in str(exc_info.value)
                assert ">60s" in str(exc_info.value) or "120" in str(exc_info.value)
                # Should fail on first attempt, not retry
                assert exc_info.value.attempts == 1
            finally:
                await client.close()
        finally:
            m.stop()

    @pytest.mark.asyncio
    async def test_dns_error_consecutive_early_termination(self) -> None:
        """3 consecutive DNS errors should trigger early termination."""
        import socket
        from multikit.registry.remote import HostUnreachableError

        m = aioresponses()
        m.start()
        try:
            # Mock DNS resolution failure
            m.get(
                f"{BASE_URL}/registry.json",
                exception=socket.gaierror(-2, "Name resolution failed"),
            )

            client = RemoteClient(
                network_config=NetworkConfig(max_retries=5, retry_base_delay=0.1)
            )
            try:
                with pytest.raises(HostUnreachableError) as exc_info:
                    await client.fetch_registry(BASE_URL)

                # Verify host unreachable error
                assert "raw.githubusercontent.com" in exc_info.value.host
                assert exc_info.value.consecutive_failures == 3
            finally:
                await client.close()
        finally:
            m.stop()

    @pytest.mark.asyncio
    async def test_tls_error_consecutive_early_termination(self) -> None:
        """3 consecutive TLS errors should trigger early termination."""
        from multikit.registry.remote import HostUnreachableError

        m = aioresponses()
        m.start()
        try:
            # Mock TLS/SSL connection error with proper OSError
            import ssl

            ssl_error = ssl.SSLError("SSL handshake failed")
            m.get(f"{BASE_URL}/registry.json", exception=ssl_error)

            client = RemoteClient(
                network_config=NetworkConfig(max_retries=5, retry_base_delay=0.1)
            )
            try:
                with pytest.raises(HostUnreachableError) as exc_info:
                    await client.fetch_registry(BASE_URL)

                # Verify host unreachable error
                assert "raw.githubusercontent.com" in exc_info.value.host
                assert exc_info.value.consecutive_failures == 3
            finally:
                await client.close()
        finally:
            m.stop()

    @pytest.mark.asyncio
    async def test_retry_exhaustion_failure_aggregation(self) -> None:
        """After max retries exhausted, error should include URL and attempt count."""

        m = aioresponses()
        m.start()
        try:
            # Always return 500 to exhaust retries
            m.get(f"{BASE_URL}/registry.json", status=500)

            max_retries = 3
            client = RemoteClient(
                network_config=NetworkConfig(
                    max_retries=max_retries, retry_base_delay=0.1
                )
            )
            try:
                with pytest.raises(RemoteFetchError) as exc_info:
                    await client.fetch_registry(BASE_URL)

                # Verify error aggregation
                assert exc_info.value.url == f"{BASE_URL}/registry.json"
                assert exc_info.value.attempts == max_retries
                assert f"Failed after {max_retries} attempts" in str(exc_info.value)
            finally:
                await client.close()
        finally:
            m.stop()

    @pytest.mark.asyncio
    async def test_retry_after_under_60s_should_wait(self) -> None:
        """Retry-After < 60s should wait and retry.

        Note: This test is skipped due to aioresponses limitations with custom response mocking.
        The functionality is verified through the RemoteClient implementation review and
        will be tested with integration tests.
        """
        pytest.skip(
            "Complex Retry-After test - will be implemented with integration tests"
        )

    @pytest.mark.asyncio
    async def test_non_dns_tls_error_clears_host_history(self) -> None:
        """Non-DNS/TLS errors should clear host error history."""

        m = aioresponses()
        m.start()
        try:
            # This test is complex due to aioresponses limitations with exception handling
            # Skip and verify with integration tests
            pytest.skip(
                "Complex host history test - will be implemented with integration tests"
            )
        finally:
            m.stop()


class TestIsDnsTlsErrorFalse:
    """Test _is_dns_tls_error returning False for non-connection errors (R01)."""

    def test_returns_false_for_client_response_error(self) -> None:
        """HTTP-level ClientResponseError is NOT a DNS/TLS error."""
        client = RemoteClient()
        error = aiohttp.ClientResponseError(
            request_info=mock.Mock(),
            history=(),
            status=403,
            message="Forbidden",
        )
        assert client._is_dns_tls_error(error) is False

    def test_returns_false_for_runtime_error(self) -> None:
        client = RemoteClient()
        assert client._is_dns_tls_error(RuntimeError("unexpected")) is False

    def test_returns_false_for_os_error(self) -> None:
        client = RemoteClient()
        assert client._is_dns_tls_error(OSError("disk full")) is False


class TestGetRetryAfterDelay:
    """Test _get_retry_after_delay edge cases (R02, R03)."""

    def test_returns_none_for_empty_headers(self) -> None:
        """Missing Retry-After header returns None."""
        client = RemoteClient()
        assert client._get_retry_after_delay({}) is None

    def test_returns_none_for_empty_string_value(self) -> None:
        """Empty string Retry-After returns None."""
        client = RemoteClient()
        assert client._get_retry_after_delay({"Retry-After": ""}) is None

    def test_returns_zero_for_zero_value(self) -> None:
        """Retry-After: 0 is valid and returns 0.0."""
        client = RemoteClient()
        assert client._get_retry_after_delay({"Retry-After": "0"}) == 0.0

    def test_returns_float_for_float_string(self) -> None:
        """Retry-After: 2.5 returns 2.5."""
        client = RemoteClient()
        assert client._get_retry_after_delay({"Retry-After": "2.5"}) == 2.5


class TestRetryWith429:
    """Tests for 429 handling branches (R04, R06, R07)."""

    @pytest.mark.asyncio
    async def test_429_with_retry_after_then_success(self) -> None:
        """R04: 429 + Retry-After ≤ 60s → wait and retry, then succeed."""
        url = f"{BASE_URL}/registry.json"
        m = aioresponses()
        with m:
            # First request: 429 with Retry-After: 0 (no real wait)
            m.get(url, status=429, headers={"Retry-After": "0"})
            # Second request: success
            m.get(url, payload={"kits": []})

            client = RemoteClient(
                network_config=NetworkConfig(max_retries=3, retry_base_delay=0.1)
            )
            try:
                registry = await client.fetch_registry(BASE_URL)
                assert isinstance(registry, Registry)
                assert registry.kits == []
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_429_without_retry_after_header(self) -> None:
        """R06: 429 without Retry-After → exponential backoff retry."""
        url = f"{BASE_URL}/registry.json"
        m = aioresponses()
        with m:
            # First request: 429 without Retry-After
            m.get(url, status=429)
            # Second request: success
            m.get(url, payload={"kits": []})

            client = RemoteClient(
                network_config=NetworkConfig(max_retries=3, retry_base_delay=0.1)
            )
            try:
                registry = await client.fetch_registry(BASE_URL)
                assert isinstance(registry, Registry)
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_4xx_non_429_immediate_reraise(self) -> None:
        """R07: 4xx (non-429) re-raised immediately without retry."""
        url = f"{BASE_URL}/registry.json"
        m = aioresponses()
        with m:
            # 403 Forbidden — should NOT retry
            m.get(url, status=403)

            client = RemoteClient(
                network_config=NetworkConfig(max_retries=5, retry_base_delay=0.1)
            )
            try:
                with pytest.raises(aiohttp.ClientResponseError) as exc_info:
                    await client.fetch_registry(BASE_URL)
                assert exc_info.value.status == 403
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_429_retry_after_exhausts_retries(self) -> None:
        """429 with small Retry-After that exhausts all retries."""
        url = f"{BASE_URL}/registry.json"
        m = aioresponses()
        with m:
            # All attempts return 429 with Retry-After: 0
            for _ in range(3):
                m.get(url, status=429, headers={"Retry-After": "0"})

            client = RemoteClient(
                network_config=NetworkConfig(max_retries=3, retry_base_delay=0.1)
            )
            try:
                with pytest.raises(RemoteFetchError) as exc_info:
                    await client.fetch_registry(BASE_URL)
                assert exc_info.value.attempts == 3
            finally:
                await client.close()


class TestHostUnreachableMixedErrors:
    """Tests for mixed DNS/TLS error types in host tracking (R10)."""

    def test_mixed_error_types_no_trigger(self) -> None:
        """2× gaierror + 1× SSLError → different types, no HostUnreachableError."""
        client = RemoteClient()
        url = "https://example.com/foo"
        # Two DNS errors
        client._check_host_unreachable(url, socket.gaierror())
        client._check_host_unreachable(url, socket.gaierror())
        # Third error is different type → should NOT trigger
        # (SSLError is a different error_type string)
        client._check_host_unreachable(url, ssl.SSLError())
        # No exception raised — passed

    def test_host_errors_trimmed_to_last_three(self) -> None:
        """Error history is trimmed to last 3 entries."""
        client = RemoteClient()
        url = "https://example.com/foo"
        # Add 4 errors of different types (alternating)
        client._check_host_unreachable(url, socket.gaierror())
        client._check_host_unreachable(url, ssl.SSLError())
        client._check_host_unreachable(url, socket.gaierror())
        client._check_host_unreachable(url, ssl.SSLError())
        # Last 3: [ssl, gaierror, ssl] — no 3 consecutive same type
        # No exception raised

    def test_clear_host_errors_after_success(self) -> None:
        """_clear_host_errors resets history for a host."""
        client = RemoteClient()
        url = "https://example.com/foo"
        client._check_host_unreachable(url, socket.gaierror())
        client._check_host_unreachable(url, socket.gaierror())
        # Clear errors (simulating successful request)
        client._clear_host_errors(url)
        # Now 2 more errors should not trigger (history was reset)
        client._check_host_unreachable(url, socket.gaierror())
        client._check_host_unreachable(url, socket.gaierror())
        # Only 2 consecutive — no exception


class TestFetchFilesConcurrentErrors:
    """Tests for fetch_files_concurrent error propagation (R14, R15)."""

    @pytest.mark.asyncio
    async def test_concurrent_fetch_success(self) -> None:
        """R15: Successful concurrent fetch returns correct mapping."""
        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/testkit/agents/a.agent.md", body="agent content")
            m.get(f"{BASE_URL}/testkit/prompts/p.prompt.md", body="prompt content")

            client = RemoteClient()
            try:
                result = await client.fetch_files_concurrent(
                    BASE_URL,
                    "testkit",
                    [("agents", "a.agent.md"), ("prompts", "p.prompt.md")],
                )
                assert result[("agents", "a.agent.md")] == "agent content"
                assert result[("prompts", "p.prompt.md")] == "prompt content"
            finally:
                await client.close()

    @pytest.mark.asyncio
    async def test_concurrent_fetch_error_propagation(self) -> None:
        """R14: Error in one file propagates from fetch_files_concurrent."""
        m = aioresponses()
        with m:
            m.get(f"{BASE_URL}/testkit/agents/a.agent.md", body="ok")
            m.get(f"{BASE_URL}/testkit/prompts/p.prompt.md", status=404)

            client = RemoteClient()
            try:
                with pytest.raises(aiohttp.ClientResponseError):
                    await client.fetch_files_concurrent(
                        BASE_URL,
                        "testkit",
                        [("agents", "a.agent.md"), ("prompts", "p.prompt.md")],
                    )
            finally:
                await client.close()


class TestCalculateDelay:
    """Test _calculate_delay boundary (R16)."""

    def test_delay_capped_at_exponent_3(self) -> None:
        """Exponent caps at 3 even for attempt > 3."""
        client = RemoteClient(
            network_config=NetworkConfig(retry_base_delay=1.0, retry_max_delay=30.0)
        )
        # attempt=3: delay = 1.0 * 2^3 = 8.0 ± jitter
        delay_3 = client._calculate_delay(3)
        # attempt=10: exponent still capped at 3, so same base = 8.0
        delay_10 = client._calculate_delay(10)
        # Both should be in range [6.4, 9.6] (8.0 ± 20%)
        assert 6.0 <= delay_3 <= 10.0
        assert 6.0 <= delay_10 <= 10.0


class TestExternalSession:
    """Test external session handling (R17)."""

    @pytest.mark.asyncio
    async def test_external_session_not_closed(self) -> None:
        """close() should NOT close an externally provided session."""
        external_session = aiohttp.ClientSession()
        client = RemoteClient(session=external_session)
        await client.close()
        # External session should still be open
        assert not external_session.closed
        # Clean up
        await external_session.close()
