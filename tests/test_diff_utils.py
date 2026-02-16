"""Tests for diff utility functions."""

from __future__ import annotations

from multikit.utils.diff import (
    generate_diff,
    print_colored_diff,
    prompt_overwrite,
    show_diff,
)


class TestGenerateDiff:
    """Tests for generate_diff."""

    def test_no_diff(self) -> None:
        result = generate_diff("same\n", "same\n")
        assert result == []

    def test_has_diff(self) -> None:
        result = generate_diff("old\n", "new\n")
        assert len(result) > 0
        assert any("-old" in line for line in result)
        assert any("+new" in line for line in result)

    def test_empty_to_content(self) -> None:
        result = generate_diff("", "new content\n")
        assert len(result) > 0

    def test_content_to_empty(self) -> None:
        result = generate_diff("old content\n", "")
        assert len(result) > 0

    def test_both_empty(self) -> None:
        result = generate_diff("", "")
        assert result == []

    def test_multiline_diff(self) -> None:
        old = "line1\nline2\nline3\n"
        new = "line1\nmodified\nline3\n"
        result = generate_diff(old, new)
        assert any("-line2" in line for line in result)
        assert any("+modified" in line for line in result)


class TestPrintColoredDiff:
    """Tests for print_colored_diff."""

    def test_prints_diff_lines(self, capsys) -> None:
        diff_lines = [
            "--- a/file\n",
            "+++ b/file\n",
            "@@ -1,1 +1,1 @@\n",
            "-old line\n",
            "+new line\n",
            " context\n",
        ]
        print_colored_diff(diff_lines)
        captured = capsys.readouterr()
        assert "old line" in captured.out
        assert "new line" in captured.out

    def test_empty_diff(self, capsys) -> None:
        print_colored_diff([])
        captured = capsys.readouterr()
        assert captured.out == ""


class TestShowDiff:
    """Tests for show_diff."""

    def test_show_diff_with_changes(self, capsys) -> None:
        result = show_diff("old\n", "new\n", "test.md")
        assert result is True
        captured = capsys.readouterr()
        assert "old" in captured.out
        assert "new" in captured.out

    def test_show_diff_no_changes(self, capsys) -> None:
        result = show_diff("same\n", "same\n", "test.md")
        assert result is False


class TestPromptOverwrite:
    """Tests for prompt_overwrite."""

    def test_answer_yes(self, monkeypatch) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "y")
        assert prompt_overwrite("file.md") == "y"

    def test_answer_no(self, monkeypatch) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "n")
        assert prompt_overwrite("file.md") == "n"

    def test_answer_all(self, monkeypatch) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "a")
        assert prompt_overwrite("file.md") == "a"

    def test_answer_skip(self, monkeypatch) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "s")
        assert prompt_overwrite("file.md") == "s"

    def test_answer_yes_word(self, monkeypatch) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "yes")
        assert prompt_overwrite("file.md") == "y"

    def test_answer_no_word(self, monkeypatch) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "no")
        assert prompt_overwrite("file.md") == "n"

    def test_answer_all_word(self, monkeypatch) -> None:
        monkeypatch.setattr("builtins.input", lambda _: "all")
        assert prompt_overwrite("file.md") == "a"

    def test_eof_returns_skip(self, monkeypatch) -> None:
        def raise_eof(_):
            raise EOFError()

        monkeypatch.setattr("builtins.input", raise_eof)
        assert prompt_overwrite("file.md") == "s"

    def test_keyboard_interrupt_returns_skip(self, monkeypatch) -> None:
        def raise_ki(_):
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", raise_ki)
        assert prompt_overwrite("file.md") == "s"

    def test_invalid_then_valid(self, monkeypatch) -> None:
        responses = iter(["invalid", "y"])
        monkeypatch.setattr("builtins.input", lambda _: next(responses))
        assert prompt_overwrite("file.md") == "y"
