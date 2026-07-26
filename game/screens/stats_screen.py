from __future__ import annotations

from ..settings import COLORS
from .base_screen import BaseScreen
from .ui_helpers import draw_background, draw_text


class StatsScreen(BaseScreen):
    def __init__(self, profile=None, context=None) -> None:
        super().__init__(context)
        self.profile = profile if profile is not None else context.saves.profile
        self.fonts = None
        self.time = 0.0

    def update(self, dt_or_pressed, events=None):
        if isinstance(dt_or_pressed, dict):
            return "back" if dt_or_pressed.get("block") else None
        self.time += float(dt_or_pressed)
        if self.context.input.pressed_for("p1").get("block"):
            self.context.state_manager.go_back()
        self._consume_events()
        return None

    def draw(self, surface, fonts=None, t=None) -> None:
        fonts = fonts or self.fonts
        if fonts is None:
            return
        draw_background(surface, self.time if t is None else t)
        record = self.profile.record
        draw_text(surface, fonts["title"], "Статистика", (96, 80), COLORS["white"])
        draw_text(surface, fonts["menu"], f"Побед: {record.wins}", (110, 240), COLORS["gold"])
        draw_text(surface, fonts["menu"], f"Поражений: {record.losses}", (110, 292), COLORS["gold"])

