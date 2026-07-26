import json
from unittest.mock import patch

from game.crash_context import CrashContext
from game.crash_reporter import build_report, handle_unhandled_exception, sanitize_text, write_crash_report


def captured_exception():
    try:
        try:
            raise ValueError("ошибка")
        except ValueError as exc:
            raise RuntimeError("outer") from exc
    except RuntimeError as exc:
        return exc


def test_report_handles_nested_unicode_exception(tmp_path):
    path = write_crash_report(captured_exception(), CrashContext(game_state="FIGHT"), tmp_path)
    report = json.loads(path.read_text(encoding="utf-8"))
    assert report["context"]["game_state"] == "FIGHT"
    assert "ValueError" in report["traceback"] and "RuntimeError" in report["traceback"]


def test_sensitive_paths_are_redacted():
    assert "apani" not in sanitize_text(r"C:\Users\apani\Documents\secret.txt")
    assert "player" not in sanitize_text("/home/player/secret.txt")


def test_write_failure_does_not_escape(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    assert write_crash_report(RuntimeError("x"), directory=blocker / "child") is None


def test_handler_always_quits_pygame():
    with patch("game.crash_reporter.write_crash_report", return_value=None), patch("game.crash_reporter.pygame.quit") as quit_game:
        assert handle_unhandled_exception(RuntimeError("x")) is None
        quit_game.assert_called_once()
