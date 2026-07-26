import json
from pathlib import Path

from game.version import VERSION
from tools.build_release import build_manifest
from tools.verify_release import verify_tree


def test_manifest_uses_canonical_versions():
    manifest = build_manifest(150)
    assert manifest["version"] == VERSION
    assert manifest["save_version"] == 4
    assert manifest["test_count"] == 150


def test_release_verifier_accepts_clean_manifest_and_rejects_user_files(tmp_path):
    name = f"ShadowRealmArena-{VERSION}-windows-x64"
    (tmp_path / f"{name}.exe").write_bytes(b"binary")
    (tmp_path / "data").mkdir()
    (tmp_path / "release_manifest.json").write_text(json.dumps({"version": VERSION}), encoding="utf-8")
    assert verify_tree(tmp_path) == []
    (tmp_path / "saves").mkdir()
    assert any("forbidden" in error for error in verify_tree(tmp_path))
