from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path

from .platform_paths import SOURCE_ROOT, user_data_root


@dataclass(frozen=True)
class UserDataPaths:
    root: Path
    saves: Path
    logs: Path
    crashes: Path
    screenshots: Path
    settings: Path
    controls: Path
    profile: Path


class UserDataManager:
    MIGRATION_MARKER = ".legacy-saves-migrated-v1"

    def __init__(self, root: Path | None = None, legacy_root: Path | None = None) -> None:
        root = Path(root or user_data_root())
        self.paths = UserDataPaths(root, root / "saves", root / "logs", root / "crashes", root / "screenshots", root / "settings.json", root / "controls.json", root / "saves" / "profile.json")
        self.legacy_root = Path(legacy_root or SOURCE_ROOT / "saves")

    def ensure(self) -> bool:
        try:
            for path in (self.paths.root, self.paths.saves, self.paths.logs, self.paths.crashes, self.paths.screenshots):
                path.mkdir(parents=True, exist_ok=True)
        except OSError:
            return False
        return True

    def migrate_legacy_saves(self) -> bool:
        marker = self.paths.root / self.MIGRATION_MARKER
        if marker.exists() or not self.ensure():
            return False
        copied: list[str] = []
        if self.legacy_root.is_dir():
            backup = self.paths.root / "legacy-saves-backup"
            try:
                backup.mkdir(exist_ok=True)
                for source in self.legacy_root.glob("*.json"):
                    json.loads(source.read_text(encoding="utf-8"))
                    shutil.copy2(source, backup / source.name)
                    target = self.paths.profile if source.name == "profile.json" else self.paths.root / source.name
                    if not target.exists():
                        target.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(source, target)
                        copied.append(source.name)
            except (OSError, UnicodeError, json.JSONDecodeError):
                return False
        marker.write_text(json.dumps({"copied": copied}), encoding="utf-8")
        return bool(copied)


_DEFAULT_MANAGER: UserDataManager | None = None


def get_user_data_manager() -> UserDataManager:
    global _DEFAULT_MANAGER
    if _DEFAULT_MANAGER is None:
        _DEFAULT_MANAGER = UserDataManager()
    return _DEFAULT_MANAGER
