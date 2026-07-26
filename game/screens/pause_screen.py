from __future__ import annotations

import pygame

from ..enums import GameState
from .base_screen import BaseScreen


class PauseScreen(BaseScreen):
    options = ("Continue", "Settings", "Controls", "Restart match", "Character select", "Main menu")

    def enter(self, payload=None) -> None:
        self.selected = 0
        self.confirm_exit = False

    def handle_event(self, event: pygame.event.Event) -> None:
        self.context.match_runtime.handle_match_event(event)

    def update(self, dt: float) -> None:
        p1 = self.context.input.pressed_for("p1")
        p2 = self.context.input.pressed_for("p2")
        pressed = {key: p1.get(key) or p2.get(key) for key in set(p1) | set(p2)}
        if pressed.get("down"):
            self.selected = (self.selected + 1) % len(self.options)
        elif pressed.get("up"):
            self.selected = (self.selected - 1) % len(self.options)
        if p1.get("pause") or p2.get("pause"):
            self.context.match_runtime.pause_match()
            self.context.state_manager.go_back()
            return
        if pressed.get("light_punch") or pressed.get("heavy_punch"):
            self._activate()
            return
        self.context.match_runtime.update_pause(dt)

    def _activate(self) -> None:
        option = self.options[self.selected]
        if option == "Continue":
            self.context.match_runtime.pause_match()
            self.context.state_manager.go_back()
        elif option in {"Settings", "Controls"}:
            self.context.state_manager.request_change(GameState.SETTINGS)
        elif option == "Restart match":
            if self.context.session.ready_for_match:
                self.context.match_runtime.start_match(self.context.session)
            self.context.match_runtime.pause_match()
            self.context.state_manager.go_back()
        elif option == "Character select":
            self.context.match_runtime.stop_match()
            self.context.state_manager.request_change(GameState.CHARACTER_SELECT)
        elif option == "Main menu":
            if not self.confirm_exit:
                self.confirm_exit = True
                return
            self.context.match_runtime.stop_match()
            self.context.state_manager.request_change(GameState.MAIN_MENU)

    def draw(self, surface: pygame.Surface) -> None:
        self.context.match_runtime.draw_pause(surface)
        font = self.fonts["menu"] if self.fonts else pygame.font.Font(None, 32)
        small = self.fonts["small"] if self.fonts else pygame.font.Font(None, 22)
        panel = pygame.Rect(430, 150, 420, 380)
        overlay=getattr(self,"_overlay",None)
        if overlay is None or overlay.get_size()!=surface.get_size():overlay=pygame.Surface(surface.get_size(),pygame.SRCALPHA);self._overlay=overlay
        overlay.fill((0, 0, 0, 115));surface.blit(overlay, (0, 0))
        pygame.draw.rect(surface, (26, 30, 36), panel, border_radius=8)
        pygame.draw.rect(surface, (232, 181, 82), panel, 2, border_radius=8)
        for index, option in enumerate(self.options):
            color = (232, 181, 82) if index == self.selected else (238, 241, 244)
            label = option if option != "Main menu" or not self.confirm_exit else "Main menu?"
            surface.blit(font.render(label, True, color), (470, 190 + index * 48))
        surface.blit(small.render("Pause", True, (132, 141, 151)), (470, 162))

    def can_go_back(self) -> bool:
        return False
