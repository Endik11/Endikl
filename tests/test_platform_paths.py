import json
from pathlib import Path
from unittest.mock import patch

from game.platform_paths import resource_root, user_data_root
from game.user_data_manager import UserDataManager


def test_platform_user_paths():
    home = Path("/home/player")
    assert user_data_root(platform="win32", environ={"LOCALAPPDATA": "C:/Local"}, home=home) == Path("C:/Local/ShadowRealmArena")
    assert user_data_root(platform="linux", environ={}, home=home) == home / ".local/share/ShadowRealmArena"
    assert user_data_root(platform="darwin", environ={}, home=home) == home / "Library/Application Support/ShadowRealmArena"


def test_resource_root_uses_frozen_bundle(tmp_path):
    with patch("sys._MEIPASS", str(tmp_path), create=True):
        assert resource_root() == tmp_path.resolve()


def test_legacy_migration_is_validated_backed_up_and_idempotent(tmp_path):
    legacy, target = tmp_path / "project/saves", tmp_path / "user"
    legacy.mkdir(parents=True)
    (legacy / "profile.json").write_text(json.dumps({"version": 4}), encoding="utf-8")
    manager = UserDataManager(target, legacy)
    assert manager.migrate_legacy_saves()
    assert manager.paths.profile.exists()
    assert (target / "legacy-saves-backup/profile.json").exists()
    assert not manager.migrate_legacy_saves()


def test_user_directory_failure_is_safe(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x", encoding="utf-8")
    assert not UserDataManager(blocker / "child").ensure()
