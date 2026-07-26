from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from game.version import VERSION

UNKNOWN = set(json.loads((ROOT / "release_excludes.json").read_text(encoding="utf-8"))["unknown_assets"])


def verify_tree(release: Path) -> list[str]:
    errors: list[str] = []
    exe = release / f"ShadowRealmArena-{VERSION}-windows-x64.exe"
    required = [exe, release / "data", release / "release_manifest.json"]
    for path in required:
        if not path.exists():
            errors.append(f"missing: {path.name}")
    relative = {path.relative_to(release).as_posix() for path in release.rglob("*")}
    forbidden_parts = {"tests", "saves", "logs", "crashes", ".git", ".pytest_cache", "__pycache__"}
    for path in relative:
        if set(Path(path).parts) & forbidden_parts or path.endswith((".bak", ".tmp", ".log")):
            errors.append(f"forbidden: {path}")
    if relative & UNKNOWN:
        errors.append("unknown assets included")
    manifest_path = release / "release_manifest.json"
    if manifest_path.exists() and json.loads(manifest_path.read_text(encoding="utf-8"))["version"] != VERSION:
        errors.append("manifest version mismatch")
    return errors


def smoke_test(release: Path, seconds: float = 5.0) -> list[str]:
    exe = release / f"ShadowRealmArena-{VERSION}-windows-x64.exe"
    if not exe.exists():
        return ["executable unavailable for smoke test"]
    with tempfile.TemporaryDirectory() as directory:
        env = dict(os.environ, SDL_VIDEODRIVER="dummy", SDL_AUDIODRIVER="dummy", SHADOW_REALM_USER_DATA=directory)
        process = subprocess.Popen([str(exe)], cwd=release, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            return_code = process.wait(timeout=seconds)
            if return_code != 0:
                output = process.stderr.read().decode("utf-8", "replace")[-1000:]
                return [f"executable exited {return_code}: {output}"]
        except subprocess.TimeoutExpired:
            process.terminate()
            process.wait(timeout=5)
        profile = Path(directory) / "saves/profile.json"
        if not profile.exists():
            return ["profile was not created outside bundle"]
        json.loads(profile.read_text(encoding="utf-8"))
    return []


def main() -> None:
    release = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "dist" / f"ShadowRealmArena-{VERSION}-windows-x64"
    errors = verify_tree(release)
    if not errors:
        errors.extend(smoke_test(release))
    if errors:
        print("\n".join(errors), file=sys.stderr)
        raise SystemExit(1)
    print(f"verified={release}")


if __name__ == "__main__":
    main()
