from __future__ import annotations

import pygame

import game.engine as engine_module
from game.engine import GameEngine
from game.enums import GameState
from game.save import SaveManager
from game.settings import SettingsManager


def test_game_engine_starts_and_stops_headlessly(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(
        engine_module,
        "SettingsManager",
        lambda: SettingsManager(tmp_path / "settings.json"),
    )
    monkeypatch.setattr(
        engine_module,
        "SaveManager",
        lambda **kwargs: SaveManager(tmp_path / "profile.json", **kwargs),
    )

    game = GameEngine()
    assert game.state is GameState.MAIN_MENU
    assert game.screen.get_size() == (1280, 720)

    pygame.event.post(pygame.event.Event(pygame.QUIT))
    game.run()

    assert not pygame.get_init()
