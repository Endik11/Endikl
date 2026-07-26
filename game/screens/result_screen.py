from __future__ import annotations

import pygame

from ..enums import GameState
from .base_screen import BaseScreen


class ResultScreen(BaseScreen):
    options = ("Rematch", "Character select", "Main menu")

    def enter(self, payload=None) -> None:
        self.selected = 0

    def handle_event(self, event: pygame.event.Event) -> None:
        self.context.match_runtime.handle_match_event(event)

    def update(self, dt: float) -> None:
        pressed = self.context.input.pressed_for("p1")
        if pressed.get("down"):
            self.selected = (self.selected + 1) % len(self.options)
        elif pressed.get("up"):
            self.selected = (self.selected - 1) % len(self.options)
        elif pressed.get("light_punch") or pressed.get("heavy_punch"):
            self._activate()
            return
        self.context.match_runtime.update_result(dt)

    def _activate(self) -> None:
        option = self.options[self.selected]
        if option == "Rematch" and self.context.session.ready_for_match:
            self.context.match_runtime.start_match(self.context.session)
            self.context.state_manager.request_change(GameState.FIGHT)
        elif option == "Character select":
            self.context.match_runtime.stop_match()
            self.context.state_manager.request_change(GameState.CHARACTER_SELECT)
        elif option == "Main menu":
            self.context.match_runtime.stop_match()
            self.context.state_manager.request_change(GameState.MAIN_MENU)

    def draw(self, surface: pygame.Surface) -> None:
        self.context.match_runtime.draw_result(surface)
        result = self.context.session.last_match_result or {}
        font = self.fonts["menu"] if self.fonts else pygame.font.Font(None, 32)
        small = self.fonts["small"] if self.fonts else pygame.font.Font(None, 22)
        panel = pygame.Rect(420, 156, 440, 350)
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 105))
        surface.blit(overlay, (0, 0))
        pygame.draw.rect(surface, (26, 30, 36), panel, border_radius=8)
        pygame.draw.rect(surface, (232, 181, 82), panel, 2, border_radius=8)
        surface.blit(font.render(str(result.get("result", "Result")), True, (238, 241, 244)), (462, 192))
        details = ["Rounds resolved", "Damage and combo totals tracked by combat events", "No result statistics are mutated here"]
        for index, detail in enumerate(details):
            surface.blit(small.render(detail, True, (132, 141, 151)), (462, 242 + index * 24))
        for index, option in enumerate(self.options):
            color = (232, 181, 82) if index == self.selected else (238, 241, 244)
            surface.blit(font.render(option, True, color), (462, 330 + index * 42))

    def can_go_back(self) -> bool:
        return False

