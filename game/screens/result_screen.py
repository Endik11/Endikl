from __future__ import annotations

import pygame

from .base_screen import BaseScreen


class ResultScreen(BaseScreen):
    def handle_event(self, event: pygame.event.Event) -> None:
        self.context.match_runtime.handle_match_event(event)

    def update(self, dt: float) -> None:
        self.context.match_runtime.update_result(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self.context.match_runtime.draw_result(surface)

    def can_go_back(self) -> bool:
        return False

