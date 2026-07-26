from __future__ import annotations

import pygame

from ..content_registry import get_default_registry
from ..enums import GameState
from ..settings import COLORS, VIRTUAL_WIDTH
from .base_screen import BaseScreen
from .ui_helpers import accept_pressed, back_pressed, draw_arena_preview, draw_background, draw_text


class ArenaSelectScreen(BaseScreen):
    def __init__(self, arena_key: str = "neon_foundry", context=None) -> None:
        super().__init__(context)
        registry = getattr(context, "content", None) or get_default_registry()
        self.keys = list(registry.arenas)
        self.index = self.keys.index(arena_key) if arena_key in self.keys else 0
        self.fonts = None
        self.time = 0.0
        self._starting = False

    @property
    def arena_key(self) -> str:
        return self.keys[self.index]

    def enter(self, payload: dict | None = None) -> None:
        super().enter(payload)
        self._starting = False
        if self.context is not None:
            self.keys = list(self._registry().arenas)
        if self.context is not None and self.context.session.selected_arena in self.keys:
            self.index = self.keys.index(self.context.session.selected_arena)

    def update(self, dt_or_pressed, events=None):
        if isinstance(dt_or_pressed, dict):
            return self._legacy_update(dt_or_pressed, events or [])
        self.time += float(dt_or_pressed)
        action = self._legacy_update(
            self.context.input.pressed_for("p1"),
            self._consume_events(),
        )
        if action == "fight":
            self._start_selected_match()
        elif action == "back":
            self.context.state_manager.go_back()
        return None

    def _legacy_update(self, pressed: dict[str, bool], events):
        for event in events:
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue
            position = event.pos if self.context is None else self.context.display.screen_to_virtual(event.pos)
            if position is None:
                continue
            if pygame.Rect(150, 218, 980, 360).collidepoint(position):
                return "fight"
            if pygame.Rect(120, 610, 120, 40).collidepoint(position):
                self.index = (self.index - 1) % len(self.keys)
            elif pygame.Rect(1040, 610, 120, 40).collidepoint(position):
                self.index = (self.index + 1) % len(self.keys)
        if pressed.get("left"):
            self.index = (self.index - 1) % len(self.keys)
        if pressed.get("right"):
            self.index = (self.index + 1) % len(self.keys)
        if accept_pressed(pressed):
            return "fight"
        if back_pressed(pressed):
            return "back"
        return None

    def _start_selected_match(self) -> None:
        if self._starting:
            return
        session = self.context.session
        if (
            not session.fighters_selected
            or session.selected_mode is None
            or not self._registry().has_fighter(session.player_one_fighter)
            or not self._registry().has_fighter(session.player_two_fighter)
        ):
            return
        session.selected_arena = self.arena_key
        if not session.ready_for_match:
            return
        self._starting = True
        self.context.saves.profile.selected_arena = self.arena_key
        self.context.saves.save()
        self.context.match_runtime.start_match(session)
        self.context.audio.play_ui()
        self.context.state_manager.request_change(GameState.FIGHT)

    def draw(self, surface, fonts=None, t=None) -> None:
        fonts = fonts or self.fonts
        if fonts is None:
            return
        draw_background(surface, self.time if t is None else t)
        localization = getattr(self.context, "localization", None)
        title = localization.get("screen.arena_select.title") if localization is not None else "Выбор арены"
        draw_text(surface, fonts["title"], title, (90, 70), COLORS["white"])
        registry = self._registry()
        arena = registry.get_arena(self.arena_key)
        draw_arena_preview(surface, arena, pygame.Rect(150, 218, 980, 360), self.time if t is None else t)
        draw_text(surface, fonts["menu"], arena.name, (VIRTUAL_WIDTH // 2, 610), COLORS["gold"], center=True)
        draw_text(surface, fonts["body"], arena.subtitle, (VIRTUAL_WIDTH // 2, 650), COLORS["white"], center=True)

    def _registry(self):
        return getattr(self.context, "content", None) or get_default_registry()
