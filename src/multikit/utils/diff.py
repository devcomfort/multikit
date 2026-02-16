"""Diff utilities: colored unified diff and interactive overwrite prompt."""

from __future__ import annotations

import difflib
import sys

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"


def generate_diff(
    old_content: str,
    new_content: str,
    old_label: str = "local",
    new_label: str = "remote",
) -> list[str]:
    """Generate unified diff lines between two strings.

    Returns list of diff lines (empty if no differences).
    """
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)

    return list(
        difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=old_label,
            tofile=new_label,
            n=3,
        )
    )


def print_colored_diff(diff_lines: list[str]) -> None:
    """Print diff lines with ANSI colors."""
    for line in diff_lines:
        if line.startswith("---") or line.startswith("+++"):
            sys.stdout.write(f"{BOLD}{line}{RESET}")
        elif line.startswith("@@"):
            sys.stdout.write(f"{CYAN}{line}{RESET}")
        elif line.startswith("-"):
            sys.stdout.write(f"{RED}{line}{RESET}")
        elif line.startswith("+"):
            sys.stdout.write(f"{GREEN}{line}{RESET}")
        else:
            sys.stdout.write(line)
    # Ensure trailing newline
    if diff_lines and not diff_lines[-1].endswith("\n"):
        sys.stdout.write("\n")


def show_diff(
    old_content: str,
    new_content: str,
    filename: str,
) -> bool:
    """Show colored diff for a file. Returns True if there are differences."""
    diff_lines = generate_diff(
        old_content,
        new_content,
        old_label=f"local/{filename}",
        new_label=f"remote/{filename}",
    )
    if not diff_lines:
        return False
    print_colored_diff(diff_lines)
    return True


def prompt_overwrite(filename: str) -> str:
    """Prompt user for overwrite decision on a single file.

    Returns one of: 'y' (yes), 'n' (no), 'a' (all), 's' (skip all)
    """
    valid = {"y", "n", "a", "s"}
    while True:
        try:
            answer = (
                input(f"  Overwrite {filename}? [y(es)/n(o)/a(ll)/s(kip all)]: ")
                .strip()
                .lower()
            )
        except (EOFError, KeyboardInterrupt):
            print()
            return "s"

        if answer in valid:
            return answer
        if answer in ("yes",):
            return "y"
        if answer in ("no",):
            return "n"
        if answer in ("all",):
            return "a"
        if answer in ("skip", "skip all"):
            return "s"
        print(f"  Invalid choice '{answer}'. Please enter y, n, a, or s.")
