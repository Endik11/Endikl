from __future__ import annotations

import pygame

from ..enums import GameState, parse_match_mode
from ..settings import COLORS, GAME_TITLE
from .base_screen import BaseScreen
from .ui_helpers import MenuItem, accept_pressed, draw_background, draw_text


class MainMenuScreen(BaseScreen):
    def __init__(self, context=None) -> None:
        super().__init__(context)
        self.items = [
            MenuItem("Начать бой", "story"),
            MenuItem("Выбор персонажа", "vs"),
            MenuItem("Выбор арены", "arena"),
            MenuItem("Тренировка", "training"),
            MenuItem("Башня испытаний", "tournament"),
            MenuItem("Магазин", "shop"),
            MenuItem("Коллекция", "collection"),
            MenuItem("Статистика", "stats"),
            MenuItem("Профиль", "profile"),
            MenuItem("Настройки", "settings"),
            MenuItem("Выход", "quit"),
        ]
        self.selected = 0
        self.fonts = None
        self.time = 0.0

    def _item_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(84, 218 + index * 40 - 6, 366, 36)

    def update(self, dt_or_pressed, events=None):
        if isinstance(dt_or_pressed, dict):
            return self._legacy_update(dt_or_pressed, events or [])
        self.time += float(dt_or_pressed)
        action = self._legacy_update(
            self.context.input.pressed_for("p1"),
            self._consume_events(),
        )
        if action:
            self._activate(action)
        return None

    def _legacy_update(self, pressed: dict[str, bool], events: list[pygame.event.Event]):
        for event in events:
            position = self._event_position(event)
            if position is None:
                continue
            for index in range(len(self.items)):
                if self._item_rect(index).collidepoint(position):
                    self.selected = index
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        return self.items[index].action
        if pressed.get("down"):
            self.selected = (self.selected + 1) % len(self.items)
        if pressed.get("up"):
            self.selected = (self.selected - 1) % len(self.items)
        if pressed.get("pause") or accept_pressed(pressed):
            return self.items[self.selected].action
        return None

    def _event_position(self, event) -> tuple[int, int] | None:
        if event.type not in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN):
            return None
        if self.context is None:
            return event.pos
        return self.context.display.screen_to_virtual(event.pos)

    def _activate(self, action: str) -> None:
        mapping = {
            "settings": GameState.SETTINGS,
            "shop": GameState.SHOP,
            "collection": GameState.COLLECTION,
            "stats": GameState.STATS,
            "profile": GameState.PROFILE,
            "arena": GameState.ARENA_SELECT,
        }
        if action == "quit":
            self.context.request_exit()
            return
        if action == "arena" and not self.context.session.fighters_selected:
            action = "vs"
        if action in {"story", "arcade", "tournament", "vs", "training"}:
            if action == "story":
                self.context.state_manager.request_change(GameState.MODE_SELECT)
                self.context.audio.play_ui()
                return
            self.context.session.selected_mode = parse_match_mode(action)
            self.context.state_manager.request_change(GameState.CHARACTER_SELECT)
            self.context.audio.play_ui()
            return
        self.context.state_manager.request_change(mapping[action])
        self.context.audio.play_ui()

    def draw(self, surface, fonts=None, t=None) -> None:
        fonts = fonts or self.fonts
        if fonts is None:
            return
        draw_background(surface, self.time if t is None else t, key_art=True)
        draw_text(surface, fonts["title"], GAME_TITLE, (94, 88), COLORS["white"])
        draw_text(surface, fonts["subtitle"], "Наследие", (104, 166), COLORS["gold"])
        for index, item in enumerate(self.items):
            y = 218 + index * 40
            selected = index == self.selected
            if selected:
                pygame.draw.rect(surface, COLORS["panel_light"], (84, y - 6, 366, 36), border_radius=6)
            draw_text(surface, fonts["menu"], item.label, (108, y), COLORS["gold"] if selected else COLORS["white"])
        draw_text(surface, fonts["menu"], GAME_TITLE, (674, 148), COLORS["gold"])


MenuScreen = MainMenuScreen
