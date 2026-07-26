from __future__ import annotations

from typing import Any

import pygame


class BaseScreen:
    """Lifecycle contract shared by all state-managed screens."""

    def __init__(self, context: Any | None = None) -> None:
        self.context = context
        self._events: list[pygame.event.Event] = []

    def enter(self, payload: dict | None = None) -> None:
        self._events.clear()

    def exit(self) -> None:
        self._events.clear()

    def handle_event(self, event: pygame.event.Event) -> None:
        self._events.append(event)

    def update(self, dt: float) -> None:
        self._events.clear()

    def draw(self, surface: pygame.Surface) -> None:
        return None

    def on_resize(self, size: tuple[int, int]) -> None:
        return None

    def can_go_back(self) -> bool:
        return True

    def request_back(self) -> None:
        if self.context is not None:
            self.context.state_manager.go_back()

    def _consume_events(self) -> list[pygame.event.Event]:
        events = self._events
        self._events = []
        return events

