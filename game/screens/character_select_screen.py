from __future__ import annotations

import pygame

from ..enums import GameState, MatchMode, parse_match_mode
from ..content_registry import get_default_registry
from ..settings import COLORS
from .base_screen import BaseScreen
from .ui_helpers import accept_pressed, back_pressed, draw_background, draw_text


class CharacterSelectScreen(BaseScreen):
    def __init__(
        self,
        mode: MatchMode | str = MatchMode.LOCAL_VS,
        p1_key: str = "kael",
        p2_key: str = "sable",
        context=None,
    ) -> None:
        super().__init__(context)
        self.mode = parse_match_mode(mode)
        registry = getattr(context, "content", None) or get_default_registry()
        self.keys = list(registry.fighters)
        self.p1_index = self.keys.index(p1_key) if p1_key in self.keys else 0
        self.p2_index = self.keys.index(p2_key) if p2_key in self.keys else min(1, len(self.keys) - 1)
        self.p1_confirmed = False
        self.p2_confirmed = False
        self.fonts = None
        self.time = 0.0

    @property
    def p1_key(self) -> str:
        return self.keys[self.p1_index]

    @property
    def p2_key(self) -> str:
        return self.keys[self.p2_index]

    def enter(self, payload: dict | None = None) -> None:
        super().enter(payload)
        if self.context is not None:
            self.keys = list(self._registry().fighters)
            if self.context.session.selected_mode is not None:
                self.mode = self.context.session.selected_mode
            if self.context.session.player_one_fighter in self.keys:
                self.p1_index = self.keys.index(self.context.session.player_one_fighter)
            if self.context.session.player_two_fighter in self.keys:
                self.p2_index = self.keys.index(self.context.session.player_two_fighter)
        self.p1_confirmed = False
        self.p2_confirmed = False

    def update(self, dt_or_p1, p2_pressed=None, events=None):
        if isinstance(dt_or_p1, dict):
            return self._legacy_update(dt_or_p1, p2_pressed or {}, events or [])
        self.time += float(dt_or_p1)
        action = self._legacy_update(
            self.context.input.pressed_for("p1"),
            self.context.input.pressed_for("p2"),
            self._consume_events(),
        )
        if action == "arena":
            self._commit_selection()
        elif action == "back":
            self.context.state_manager.go_back()
        return None

    def _legacy_update(self, p1: dict[str, bool], p2: dict[str, bool], events):
        for event in events:
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue
            position = event.pos if self.context is None else self.context.display.screen_to_virtual(event.pos)
            if position is None:
                continue
            if pygame.Rect(92, 220, 440, 330).collidepoint(position):
                self.p1_index = (self.p1_index + 1) % len(self.keys)
                self.p1_confirmed = False
            elif pygame.Rect(748, 220, 440, 330).collidepoint(position):
                self.p2_index = (self.p2_index + 1) % len(self.keys)
                self.p2_confirmed = False

        if p1.get("left"):
            self.p1_index = (self.p1_index - 1) % len(self.keys)
            self.p1_confirmed = False
        if p1.get("right"):
            self.p1_index = (self.p1_index + 1) % len(self.keys)
            self.p1_confirmed = False

        local = self.mode is MatchMode.LOCAL_VS
        if local:
            if p2.get("left"):
                self.p2_index = (self.p2_index - 1) % len(self.keys)
                self.p2_confirmed = False
            if p2.get("right"):
                self.p2_index = (self.p2_index + 1) % len(self.keys)
                self.p2_confirmed = False
        elif p1.get("down"):
            self.p2_index = (self.p2_index + 1) % len(self.keys)
            if self.p2_index == self.p1_index:
                self.p2_index = (self.p2_index + 1) % len(self.keys)

        if accept_pressed(p1):
            self.p1_confirmed = True
        if local and accept_pressed(p2):
            self.p2_confirmed = True
        if not local:
            self.p2_confirmed = True
        if self.p1_confirmed and self.p2_confirmed:
            if local and self.p1_index == self.p2_index:
                self.p2_index = (self.p2_index + 1) % len(self.keys)
            return "arena"
        if back_pressed(p1):
            return "back"
        return None

    def _commit_selection(self) -> None:
        session = self.context.session
        session.player_one_fighter = self.p1_key
        session.player_two_fighter = self.p2_key
        session.selected_arena = None
        self.context.saves.profile.selected_fighter = self.p1_key
        self.context.saves.save()
        self.context.audio.play_ui()
        self.context.state_manager.request_change(GameState.ARENA_SELECT)

    def draw(self, surface, fonts=None, t=None) -> None:
        fonts = fonts or self.fonts
        if fonts is None:
            return
        draw_background(surface, self.time if t is None else t)
        draw_text(surface, fonts["title"], self._text("screen.character_select.title", "Выбор бойца"), (90, 70), COLORS["white"])
        self._draw_panel(surface, fonts, self.p1_key, pygame.Rect(92, 220, 440, 330), self._text("screen.player_one", "Игрок 1").upper(), self.p1_confirmed)
        label = self._text("screen.player_two", "Игрок 2").upper() if self.mode is MatchMode.LOCAL_VS else self._text("screen.opponent", "Соперник").upper()
        self._draw_panel(surface, fonts, self.p2_key, pygame.Rect(748, 220, 440, 330), label, self.p2_confirmed)

    def _draw_panel(self, surface, fonts, key, rect, label, confirmed) -> None:
        registry = self._registry()
        definition = registry.get_fighter(key)
        pygame.draw.rect(surface, COLORS["panel"], rect, border_radius=8)
        pygame.draw.rect(surface, COLORS["green"] if confirmed else definition.palette[0], rect, 3, border_radius=8)
        draw_text(surface, fonts["small"], label, (rect.x + 28, rect.y + 24), COLORS["muted"])
        draw_text(surface, fonts["menu"], definition.name, (rect.x + 28, rect.y + 66), COLORS["white"])
        draw_text(surface, fonts["body"], definition.title, (rect.x + 30, rect.y + 110), definition.palette[1])

    def _registry(self):
        return getattr(self.context, "content", None) or get_default_registry()

    def _text(self, key: str, fallback: str) -> str:
        localization = getattr(self.context, "localization", None)
        return localization.get(key) if localization is not None else fallback
