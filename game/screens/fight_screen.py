from __future__ import annotations

import pygame

from ..enums import GameState
from .base_screen import BaseScreen


class FightScreen(BaseScreen):
    def handle_event(self, event: pygame.event.Event) -> None:
        self.context.match_runtime.handle_match_event(event)

    def update(self, dt: float) -> None:
        p1 = self.context.input.pressed_for("p1")
        p2 = self.context.input.pressed_for("p2")
        if p1.get("pause") or p2.get("pause"):
            self.context.match_runtime.pause_match()
            self.context.state_manager.request_change(GameState.PAUSE)
            return
        self.context.match_runtime.update_match(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.context.match_runtime.draw_match(surface)

    def can_go_back(self) -> bool:
        return False

