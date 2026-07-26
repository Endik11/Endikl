from __future__ import annotations

from dataclasses import dataclass

from .debug import log_event
from .enums import GameState, parse_game_state
from .screens.base_screen import BaseScreen


@dataclass(slots=True)
class _PendingChange:
    state: GameState
    payload: dict | None
    remember_current: bool


class StateManager:
    def __init__(self) -> None:
        self._screens: dict[GameState, BaseScreen] = {}
        self._current_state: GameState | None = None
        self._history: list[GameState] = []
        self._pending: _PendingChange | None = None
        self._applying = False

    def register(
        self,
        state: GameState,
        screen: BaseScreen,
        *,
        replace: bool = False,
    ) -> None:
        state = parse_game_state(state)
        if state in self._screens and not replace:
            raise ValueError(f"Screen already registered for {state.name}")
        self._screens[state] = screen

    def request_change(
        self,
        state: GameState,
        payload: dict | None = None,
        remember_current: bool = True,
    ) -> None:
        state = parse_game_state(state)
        if state not in self._screens:
            raise KeyError(f"No screen registered for {state.name}")
        if self._applying:
            raise RuntimeError("Recursive state changes are not allowed")
        if self._pending is not None:
            raise RuntimeError("A state change is already pending")
        self._pending = _PendingChange(state, payload, remember_current)

    def apply_pending_change(self) -> bool:
        if self._pending is None:
            return False
        if self._applying:
            raise RuntimeError("Recursive state changes are not allowed")

        pending = self._pending
        self._pending = None
        previous = self._current_state
        self._applying = True
        try:
            if previous is not None:
                self._screens[previous].exit()
                if pending.remember_current and previous != pending.state:
                    self._history.append(previous)
            self._current_state = pending.state
            self._screens[pending.state].enter(pending.payload)
        finally:
            self._applying = False
        log_event(
            "state_transition from=%s to=%s",
            previous.name if previous else None,
            pending.state.name,
        )
        return True

    def go_back(self) -> bool:
        if self._applying or self._pending is not None or not self._history:
            return False
        state = self._history.pop()
        self.request_change(state, remember_current=False)
        return True

    def clear_history(self) -> None:
        self._history.clear()

    @property
    def current_state(self) -> GameState:
        if self._current_state is None:
            raise RuntimeError("StateManager has no active state")
        return self._current_state

    @property
    def current_screen(self) -> BaseScreen:
        return self._screens[self.current_state]

    @property
    def has_pending_change(self) -> bool:
        return self._pending is not None

    @property
    def history(self) -> tuple[GameState, ...]:
        return tuple(self._history)

