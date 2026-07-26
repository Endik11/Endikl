from __future__ import annotations

from typing import Protocol

import pygame

from .session import GameSession


class MatchRuntime(Protocol):
    def start_match(self, session: GameSession) -> None: ...

    def handle_match_event(self, event: pygame.event.Event) -> None: ...

    def update_match(self, dt: float) -> None: ...

    def draw_match(self, surface: pygame.Surface) -> None: ...

    def pause_match(self) -> None: ...

    def stop_match(self) -> None: ...

    def update_pause(self, dt: float) -> None: ...

    def draw_pause(self, surface: pygame.Surface) -> None: ...

    def update_result(self, dt: float) -> None: ...

    def draw_result(self, surface: pygame.Surface) -> None: ...


class NullMatchRuntime:
    """Safe runtime used by isolated screen tests and menu-only tools."""

    def start_match(self, session: GameSession) -> None:
        if not session.ready_for_match:
            raise ValueError("Cannot start a match before mode, fighters, and arena are selected")

    def handle_match_event(self, event: pygame.event.Event) -> None:
        return None

    def update_match(self, dt: float) -> None:
        return None

    def draw_match(self, surface: pygame.Surface) -> None:
        surface.fill((8, 9, 12))

    def pause_match(self) -> None:
        return None

    def stop_match(self) -> None:
        return None

    def update_pause(self, dt: float) -> None:
        return None

    def draw_pause(self, surface: pygame.Surface) -> None:
        self.draw_match(surface)

    def update_result(self, dt: float) -> None:
        return None

    def draw_result(self, surface: pygame.Surface) -> None:
        self.draw_match(surface)
