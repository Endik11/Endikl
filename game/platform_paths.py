from __future__ import annotations

import os
import sys
from pathlib import Path

APP_DIR_NAME = "ShadowRealmArena"
SOURCE_ROOT = Path(__file__).resolve().parent.parent


def resource_root() -> Path:
    frozen_root = getattr(sys, "_MEIPASS", None)
    return Path(frozen_root).resolve() if frozen_root else SOURCE_ROOT


def user_data_root(*, platform: str | None = None, environ: dict[str, str] | None = None, home: Path | None = None) -> Path:
    override = os.environ.get("SHADOW_REALM_USER_DATA")
    if override:
        return Path(override).expanduser().resolve()
    platform, environ, home = platform or sys.platform, environ or os.environ, home or Path.home()
    if platform.startswith("win"):
        return Path(environ.get("LOCALAPPDATA", home / "AppData" / "Local")) / APP_DIR_NAME
    if platform == "darwin":
        return home / "Library" / "Application Support" / APP_DIR_NAME
    return Path(environ.get("XDG_DATA_HOME", home / ".local" / "share")) / APP_DIR_NAME


def data_path(*parts: str) -> Path:
    return resource_root().joinpath("data", *parts)


def asset_path(*parts: str) -> Path:
    return resource_root().joinpath("assets", *parts)
