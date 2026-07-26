from __future__ import annotations

import json

from game.save import SAVE_VERSION, SaveManager
from game.settings import FPS, GameSettings, SettingsManager


def test_profile_load_repairs_invalid_keys_and_types(tmp_path) -> None:
    path = tmp_path / "profile.json"
    path.write_text(
        json.dumps(
            {
                "version": SAVE_VERSION,
                "selected_fighter": "missing_fighter",
                "selected_arena": "missing_arena",
                "unlocked_fighters": ["kael", 42, "missing_fighter", "kael"],
                "unlocked_arenas": "not-a-list",
                "currency": "250",
                "story_chapter": -4,
                "record": {"wins": "3", "losses": -2, "unknown": 99},
                "unknown_future_field": {"ignored": True},
            }
        ),
        encoding="utf-8",
    )

    profile = SaveManager(
        path,
        fighter_keys={"kael", "sable"},
        arena_keys={"neon_foundry", "storm_pier"},
    ).load()

    assert profile.selected_fighter == "kael"
    assert profile.selected_arena == "neon_foundry"
    assert profile.unlocked_fighters == ["kael"]
    assert profile.unlocked_arenas == ["neon_foundry", "storm_pier"]
    assert profile.currency == 250
    assert profile.story_chapter == 1
    assert profile.record.wins == 3
    assert profile.record.losses == 0


def test_profile_load_recovers_from_malformed_json(tmp_path) -> None:
    path = tmp_path / "profile.json"
    path.write_text("{broken", encoding="utf-8")

    profile = SaveManager(path).load()

    assert profile.selected_fighter == "kael"
    assert json.loads(path.read_text(encoding="utf-8"))["version"] == SAVE_VERSION


def test_settings_load_filters_unknown_fields_and_invalid_values(tmp_path) -> None:
    path = tmp_path / "settings.json"
    path.write_text(
        json.dumps(
            {
                "video": {
                    "width": "1920",
                    "height": -1,
                    "fps_limit": 17,
                    "ui_scale": 50,
                    "unknown": "ignored",
                },
                "audio": {"music_volume": "0.25", "mute": "yes"},
                "gameplay": {"difficulty": "impossible", "rounds_to_win": 99},
                "controls": {
                    "gamepad_enabled": False,
                    "keyboard": {"p1": {"left": "invalid"}},
                },
            }
        ),
        encoding="utf-8",
    )

    settings = SettingsManager(path).load()
    defaults = GameSettings()

    assert settings.video.width == 1920
    assert settings.video.height == defaults.video.height
    assert settings.video.fps_limit == FPS
    assert settings.video.ui_scale == 2.0
    assert settings.audio.music_volume == 0.25
    assert settings.audio.mute is defaults.audio.mute
    assert settings.gameplay.difficulty == defaults.gameplay.difficulty
    assert settings.gameplay.rounds_to_win == 5
    assert settings.controls.gamepad_enabled is False
    assert settings.controls.keyboard["p1"]["left"] == defaults.controls.keyboard["p1"]["left"]

