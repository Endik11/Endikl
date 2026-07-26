from __future__ import annotations

import pygame

from ..shop import ShopScreen as LegacyShopScreen
from .base_screen import BaseScreen


class ShopScreen(BaseScreen):
    def __init__(self, context=None) -> None:
        super().__init__(context)
        self.legacy = LegacyShopScreen()
        self.fonts = None
        self.time = 0.0

    def __getattr__(self, name):
        return getattr(self.legacy, name)

    def update(self, dt_or_pressed, profile=None, save_manager=None, events=None):
        if isinstance(dt_or_pressed, dict):
            return self.legacy.update(dt_or_pressed, profile, save_manager, events)
        self.time += float(dt_or_pressed)
        translated_events = []
        for event in self._consume_events():
            if event.type == pygame.MOUSEBUTTONDOWN:
                position = self.context.display.screen_to_virtual(event.pos)
                if position is None:
                    continue
                event = pygame.event.Event(event.type, {**event.dict, "pos": position})
            translated_events.append(event)
        action = self.legacy.update(
            self.context.input.pressed_for("p1"),
            self.context.saves.profile,
            self.context.saves,
            translated_events,
        )
        if action == "back":
            self.context.state_manager.go_back()
        return None

    def draw(self, surface, fonts=None, t=None, profile=None) -> None:
        self.legacy.draw(
            surface,
            fonts or self.fonts,
            self.time if t is None else t,
            profile or self.context.saves.profile,
        )

