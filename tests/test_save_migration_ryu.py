from __future__ import annotations

import json

from game.save import SAVE_VERSION, SaveManager, migrate_profile_data


def legacy_profile() -> dict[str, object]:
    return {
        "version": 1,
        "selected_fighter": "ryu",
        "unlocked_fighters": ["kael", "ryu", "ren_kaido"],
        "favorite_fighter": "ryu",
        "player_one_fighter": "ryu",
        "player_two_fighter": "sable",
        "purchased_items": ["ryu"],
        "fighter_stats": {
            "ryu": {"wins": 3, "losses": 2, "draws": 1, "damage": 100, "best_combo": 4, "updated_at": "2025-01-01"},
            "ren_kaido": {"wins": 2, "losses": 1, "draws": 2, "damage": 80, "best_combo": 7, "updated_at": "2026-01-01"},
        },
        "arcade_progress": {"fighter": "ryu", "ryu": {"floor": 2}},
        "story_progress": {"owner": "ryu"},
        "tournament_progress": {"fighters": ["ryu", "ren_kaido"]},
    }


def test_migration_updates_nested_ids_and_merges_stats() -> None:
    migrated, changed = migrate_profile_data(legacy_profile())
    assert changed and migrated["version"] == SAVE_VERSION
    assert migrated["selected_fighter"] == "ren_kaido"
    assert migrated["unlocked_fighters"] == ["kael", "ren_kaido"]
    assert migrated["favorite_fighter"] == "ren_kaido"
    assert migrated["player_one_fighter"] == "ren_kaido"
    assert migrated["arcade_progress"]["fighter"] == "ren_kaido"
    assert migrated["story_progress"]["owner"] == "ren_kaido"
    assert migrated["tournament_progress"]["fighters"] == ["ren_kaido"]
    stats = migrated["fighter_stats"]["ren_kaido"]
    assert stats["wins"] == 5 and stats["losses"] == 3 and stats["draws"] == 3
    assert stats["damage"] == 180 and stats["best_combo"] == 7
    assert stats["updated_at"] == "2026-01-01"
    again, changed_again = migrate_profile_data(migrated)
    assert not changed_again and again == migrated


def test_manager_creates_backup_and_does_not_repeat_migration(tmp_path) -> None:
    path = tmp_path / "profile.json"
    path.write_text(json.dumps(legacy_profile()), encoding="utf-8")
    manager = SaveManager(path, fighter_keys={"kael", "sable", "ren_kaido"}, arena_keys={"neon_foundry"})
    profile = manager.load()
    backup = path.with_suffix(path.suffix + ".v1.bak")
    assert backup.is_file()
    assert profile.version == SAVE_VERSION
    assert profile.selected_fighter == "ren_kaido"
    backup_text = backup.read_text(encoding="utf-8")
    manager.load()
    assert backup.read_text(encoding="utf-8") == backup_text
