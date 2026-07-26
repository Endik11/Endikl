from __future__ import annotations

import pygame

from ..enums import GameState
from .base_screen import BaseScreen


class PauseScreen(BaseScreen):
    def handle_event(self, event: pygame.event.Event) -> None:
        self.context.match_runtime.handle_match_event(event)

    def update(self, dt: float) -> None:
        p1 = self.context.input.pressed_for("p1")
        p2 = self.context.input.pressed_for("p2")
        if p1.get("pause") or p2.get("pause") or p1.get("block") or p2.get("block"):
            self.context.match_runtime.pause_match()
            self.context.state_manager.go_back()
            return
        self.context.match_runtime.update_pause(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.context.match_runtime.draw_pause(surface)

    def can_go_back(self) -> bool:
        return False
