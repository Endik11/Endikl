from __future__ import annotations

from types import SimpleNamespace

from game.content_registry import ContentRegistry, get_default_registry
from game.enums import GameState, MatchMode
from game.screens.arena_select_screen import ArenaSelectScreen
from game.screens.base_screen import BaseScreen
from game.screens.character_select_screen import CharacterSelectScreen
from game.session import GameSession
from game.state_manager import StateManager


class InputStub:
    def __init__(self) -> None:
        self.values = {"p1": {}, "p2": {}}

    def pressed_for(self, player: str) -> dict[str, bool]:
        return self.values[player]


class RuntimeStub:
    def __init__(self) -> None:
        self.starts = []

    def start_match(self, session: GameSession) -> None:
        self.starts.append((session.player_one_fighter, session.player_two_fighter, session.selected_arena))


class SaveStub:
    def __init__(self) -> None:
        self.profile = SimpleNamespace(selected_fighter="kael", selected_arena="neon_foundry")
        self.save_count = 0

    def save(self) -> None:
        self.save_count += 1


class DisplayStub:
    def screen_to_virtual(self, position):
        return position


class AudioStub:
    def play_ui(self) -> None:
        return None


def test_local_character_to_arena_to_fight_starts_once() -> None:
    manager = StateManager()
    session = GameSession(selected_mode=MatchMode.LOCAL_VS)
    input_stub = InputStub()
    runtime = RuntimeStub()
    context = SimpleNamespace(
        state_manager=manager,
        session=session,
        input=input_stub,
        match_runtime=runtime,
        saves=SaveStub(),
        display=DisplayStub(),
        audio=AudioStub(),
        content=get_default_registry(),
    )
    character = CharacterSelectScreen(context=context)
    arena = ArenaSelectScreen(context=context)
    manager.register(GameState.MAIN_MENU, BaseScreen(context))
    manager.register(GameState.CHARACTER_SELECT, character)
    manager.register(GameState.ARENA_SELECT, arena)
    manager.register(GameState.FIGHT, BaseScreen(context))
    manager.request_change(GameState.MAIN_MENU, remember_current=False)
    manager.apply_pending_change()
    manager.request_change(GameState.CHARACTER_SELECT)
    manager.apply_pending_change()

    input_stub.values = {
        "p1": {"light_punch": True},
        "p2": {"light_punch": True},
    }
    character.update(0.016)
    assert runtime.starts == []
    manager.apply_pending_change()
    assert manager.current_state is GameState.ARENA_SELECT
    assert session.player_one_fighter and session.player_two_fighter

    input_stub.values = {"p1": {"light_punch": True}, "p2": {}}
    arena.update(0.016)
    assert len(runtime.starts) == 1
    manager.apply_pending_change()
    assert manager.current_state is GameState.FIGHT
    arena._start_selected_match()
    assert len(runtime.starts) == 1


def test_selection_screens_use_registry_content() -> None:
    registry = get_default_registry()
    context = SimpleNamespace(content=registry)
    character = CharacterSelectScreen(context=context)
    arena = ArenaSelectScreen(context=context)
    assert "ryu" not in character.keys
    assert "ren_kaido" in character.keys
    assert character.keys == list(registry.fighters)
    assert arena.keys == list(registry.arenas)
    assert arena.keys == [item.id for item in registry.arenas.values()]


def test_unknown_fighter_id_does_not_start_match() -> None:
    registry = get_default_registry()
    runtime = RuntimeStub()
    session = GameSession(
        selected_mode=MatchMode.LOCAL_VS,
        player_one_fighter="missing_fighter",
        player_two_fighter="sable",
    )
    context = SimpleNamespace(
        content=registry,
        session=session,
        match_runtime=runtime,
        saves=SaveStub(),
        audio=AudioStub(),
    )
    arena = ArenaSelectScreen(context=context)
    arena._start_selected_match()
    assert runtime.starts == []


def test_fallback_content_supports_selection_chain(tmp_path) -> None:
    registry = ContentRegistry(tmp_path / "missing-data")
    registry.load_all()
    session = GameSession(
        selected_mode=MatchMode.LOCAL_VS,
        player_one_fighter="aeris",
        player_two_fighter="toren",
    )
    runtime = RuntimeStub()
    manager = StateManager()
    context = SimpleNamespace(
        content=registry,
        session=session,
        match_runtime=runtime,
        saves=SaveStub(),
        audio=AudioStub(),
        state_manager=manager,
    )
    arena = ArenaSelectScreen(context=context)
    manager.register(GameState.ARENA_SELECT, arena)
    manager.register(GameState.FIGHT, BaseScreen(context))
    manager.request_change(GameState.ARENA_SELECT, remember_current=False)
    manager.apply_pending_change()
    arena._start_selected_match()
    manager.apply_pending_change()
    assert runtime.starts == [("aeris", "toren", "dawn_hall")]
    assert manager.current_state is GameState.FIGHT
    arena._start_selected_match()
    assert len(runtime.starts) == 1
