from __future__ import annotations

import pytest

from game.enums import GameState, parse_game_state
from game.screens.base_screen import BaseScreen
from game.state_manager import StateManager


class RecordingScreen(BaseScreen):
    def __init__(self, manager: StateManager | None = None) -> None:
        super().__init__()
        self.manager = manager
        self.calls: list[object] = []

    def enter(self, payload=None) -> None:
        self.calls.append(("enter", payload))

    def exit(self) -> None:
        self.calls.append("exit")


def test_deferred_transition_lifecycle_payload_and_back() -> None:
    manager = StateManager()
    menu = RecordingScreen()
    settings = RecordingScreen()
    manager.register(GameState.MAIN_MENU, menu)
    manager.register(GameState.SETTINGS, settings)

    manager.request_change("menu", {"source": "boot"}, remember_current=False)
    assert manager.has_pending_change
    assert manager.apply_pending_change()
    assert manager.current_state is GameState.MAIN_MENU
    assert menu.calls == [("enter", {"source": "boot"})]

    manager.request_change(GameState.SETTINGS, {"tab": "video"})
    assert manager.current_state is GameState.MAIN_MENU
    manager.apply_pending_change()
    assert menu.calls[-1] == "exit"
    assert settings.calls == [("enter", {"tab": "video"})]
    assert manager.history == (GameState.MAIN_MENU,)

    assert manager.go_back()
    manager.apply_pending_change()
    assert manager.current_state is GameState.MAIN_MENU
    assert manager.history == ()


def test_registration_and_invalid_states_are_strict() -> None:
    manager = StateManager()
    manager.register(GameState.MAIN_MENU, RecordingScreen())
    with pytest.raises(ValueError):
        manager.register(GameState.MAIN_MENU, RecordingScreen())
    with pytest.raises(KeyError):
        manager.request_change(GameState.FIGHT)
    with pytest.raises(ValueError):
        parse_game_state("not-a-real-state")


def test_recursive_transition_from_enter_is_rejected() -> None:
    manager = StateManager()

    class RecursiveScreen(RecordingScreen):
        def enter(self, payload=None) -> None:
            manager.request_change(GameState.MAIN_MENU)

    manager.register(GameState.MAIN_MENU, RecursiveScreen(manager))
    manager.request_change(GameState.MAIN_MENU)
    with pytest.raises(RuntimeError, match="Recursive"):
        manager.apply_pending_change()

