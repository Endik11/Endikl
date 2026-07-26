from __future__ import annotations

import json
import platform
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.save import SAVE_VERSION
from game.version import BUILD_CHANNEL, VERSION


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def collected_test_count() -> int:
    try:
        output = subprocess.check_output([sys.executable, "-m", "pytest", "--collect-only", "-q"], cwd=ROOT, text=True)
        match = re.search(r"(\d+) tests? collected", output)
        return int(match.group(1)) if match else 0
    except (OSError, subprocess.CalledProcessError):
        return 0


def write_windows_version_info() -> None:
    numbers = [int(part) for part in VERSION.split(".")]
    numbers.extend([0] * (4 - len(numbers)))
    numeric = ", ".join(str(part) for part in numbers[:4])
    text = f"""VSVersionInfo(ffi=FixedFileInfo(filevers=({numeric}), prodvers=({numeric}), mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)), kids=[StringFileInfo([StringTable('040904B0', [StringStruct('FileDescription', 'Shadow Realm: Arena'), StringStruct('ProductName', 'Shadow Realm: Arena'), StringStruct('ProductVersion', '{VERSION}'), StringStruct('FileVersion', '{VERSION}'), StringStruct('CompanyName', 'Endik11'), StringStruct('OriginalFilename', 'ShadowRealmArena.exe'), StringStruct('Copyright', 'Copyright (c) 2026 Endik11')])]), VarFileInfo([VarStruct('Translation', [1033, 1200])])])\n"""
    (ROOT / "build_version_info.txt").write_text(text, encoding="utf-8")


def build_manifest(test_count: int = 0) -> dict[str, object]:
    defaults = json.loads((ROOT / "data/defaults.json").read_text(encoding="utf-8"))
    return {
        "version": VERSION,
        "build_channel": BUILD_CHANNEL,
        "build_date_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "pygame_version": pygame.version.ver,
        "commit": git_commit(),
        "data_version": defaults.get("content_version", 1),
        "save_version": SAVE_VERSION,
        "supported_platforms": ["windows-x64"],
        "asset_audit_status": "UNKNOWN assets excluded",
        "test_count": test_count,
        "build_type": "one-folder",
    }


def main() -> None:
    manifest = build_manifest(collected_test_count())
    (ROOT / "release_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    write_windows_version_info()
    subprocess.run([sys.executable, "-m", "PyInstaller", "--noconfirm", "--clean", "Endikl.spec"], cwd=ROOT, check=True)
    name = f"ShadowRealmArena-{VERSION}-windows-x64"
    archive = shutil.make_archive(str(ROOT / "dist" / name), "zip", ROOT / "dist", name)
    print(f"release={ROOT / 'dist' / name}")
    print(f"archive={archive}")


if __name__ == "__main__":
    main()
