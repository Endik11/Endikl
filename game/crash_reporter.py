from __future__ import annotations

import json
import platform
import re
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

import pygame

from .crash_context import CrashContext
from .user_data_manager import get_user_data_manager
from .version import BUILD_CHANNEL, GAME_NAME, VERSION


_PATH_PATTERN = re.compile(r'(?i)(?:[a-z]:\\|/Users/|/home/)[^\s"\']+')


def sanitize_text(value: str) -> str:
    return _PATH_PATTERN.sub("<redacted-path>", value)


def build_report(exc: BaseException, context: CrashContext | None = None) -> dict[str, object]:
    context = context or CrashContext()
    trace = "".join(traceback.format_exception(type(exc), exc, exc.__traceback__))
    return {
        "game": GAME_NAME,
        "version": VERSION,
        "build_channel": BUILD_CHANNEL,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "os": platform.system(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "pygame": pygame.version.ver,
        "context": context.safe_dict(),
        "traceback": sanitize_text(trace),
    }


def write_crash_report(exc: BaseException, context: CrashContext | None = None, directory: Path | None = None) -> Path | None:
    try:
        directory = Path(directory or get_user_data_manager().paths.crashes)
        directory.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        path = directory / f"crash-{VERSION}-{stamp}.json"
        path.write_text(json.dumps(build_report(exc, context), ensure_ascii=False, indent=2), encoding="utf-8")
        return path
    except Exception:
        return None


def handle_unhandled_exception(exc: BaseException, context: CrashContext | None = None) -> Path | None:
    path = write_crash_report(exc, context)
    try:
        pygame.quit()
    except Exception:
        pass
    message = f"{GAME_NAME} stopped after an unexpected error."
    if path:
        message += f" Crash report: {path}"
    print(message, file=sys.stderr)
    return path
