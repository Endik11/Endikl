from __future__ import annotations

from typing import Callable

import pygame

from ..settings import COLORS, DEFAULT_KEYBOARD, FPS_OPTIONS
from ..enums import GameState
from .base_screen import BaseScreen
from .ui_helpers import accept_pressed, back_pressed, draw_background, draw_text


Row = tuple[str, Callable[[], str], Callable[[int], None]]


class SettingsScreen(BaseScreen):
    def __init__(self, settings=None, context=None) -> None:
        super().__init__(context)
        if settings is None and context is not None:
            settings = context.settings.settings
        self.settings = settings
        self.selected = 0
        self.sections = [
            ("Видео", self._video_rows),
            ("FPS", self._fps_rows),
            ("Звук", self._audio_rows),
            ("Управление", self._control_rows),
            ("Visual", self._visual_rows),
            ("Назад", self._back_row),
        ]
        self.section_index = 0
        self.rows: list[Row] = []
        self.fonts = None
        self.time = 0.0
        self._refresh_rows()

    def update(self, dt_or_pressed, events=None):
        if isinstance(dt_or_pressed, dict):
            return self._legacy_update(dt_or_pressed, events or [])
        self.time += float(dt_or_pressed)
        action = self._legacy_update(
            self.context.input.pressed_for("p1"),
            self._consume_events(),
        )
        if action == "back":
            self.context.settings.settings = self.settings
            self.context.settings.save()
            self.context.display.apply_settings()
            self.context.state_manager.go_back()
        return None

    def _legacy_update(self, pressed: dict[str, bool], events: list[pygame.event.Event]):
        for event in events:
            if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
                continue
            position = event.pos if self.context is None else self.context.display.screen_to_virtual(event.pos)
            if position is None:
                continue
            for index in range(len(self.rows)):
                if self._row_rect(index).collidepoint(position):
                    self.selected = index
                    if self.rows[index][0] == "Назад":
                        return "back"
                    self.rows[index][2](1)
                    return None
            for index in range(len(self.sections)):
                if self._section_rect(index).collidepoint(position):
                    self.select_section(index)
                    return None
        if pressed.get("right"):
            if self.section_index in {1, 2, 3, 4}:
                self.rows[self.selected][2](1)
            else:
                self.select_section(min(len(self.sections) - 1, self.section_index + 1))
            return None
        if pressed.get("left"):
            if self.section_index in {1, 2, 3, 4}:
                self.rows[self.selected][2](-1)
            else:
                self.select_section(max(0, self.section_index - 1))
            return None
        if pressed.get("down"):
            self.selected = (self.selected + 1) % len(self.rows)
        if pressed.get("up"):
            self.selected = (self.selected - 1) % len(self.rows)
        if accept_pressed(pressed):
            if self.rows[self.selected][0] == "Назад":
                return "back"
            self.rows[self.selected][2](1)
        if back_pressed(pressed):
            return "back"
        return None

    def select_section(self, index: int) -> None:
        if 0 <= index < len(self.sections):
            self.section_index = index
            self.selected = 0
            self._refresh_rows()

    def _refresh_rows(self) -> None:
        self.rows = self.sections[self.section_index][1]()
        self.selected = min(self.selected, max(0, len(self.rows) - 1))

    def _row_rect(self, index: int) -> pygame.Rect:
        spacing = 32 if len(self.rows) > 8 else 48
        return pygame.Rect(94, 232 + index * spacing - 8, 760, min(34, spacing))

    def _section_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(94 + index * 124, 190, 110, 34)

    def _video_rows(self) -> list[Row]:
        return [
            ("Разрешение", self._resolution_value, self._change_resolution),
            ("Режим окна", self._display_mode_value, self._change_display_mode),
            ("Полноэкранный", self._fullscreen_value, self._toggle_fullscreen),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def _visual_rows(self) -> list[Row]:
        return [
            ("Particles", lambda: self._bool_value(self.settings.video.particles), lambda direction: self._toggle_video("particles")),
            ("Trails", lambda: self._bool_value(self.settings.video.trails), lambda direction: self._toggle_video("trails")),
            ("Shadows", lambda: self._bool_value(self.settings.video.shadows), lambda direction: self._toggle_video("shadows")),
            ("Shake", lambda: self._bool_value(self.settings.video.camera_shake), lambda direction: self._toggle_video("camera_shake")),
            ("Flashes", lambda: self._bool_value(self.settings.video.flashes), lambda direction: self._toggle_video("flashes")),
            ("Dynamic zoom", lambda: self._bool_value(self.settings.video.dynamic_zoom), lambda direction: self._toggle_video("dynamic_zoom")),
            ("Background", lambda: self._bool_value(self.settings.video.background_animation), lambda direction: self._toggle_video("background_animation")),
            ("Damage nums", lambda: self._bool_value(self.settings.video.damage_numbers), lambda direction: self._toggle_video("damage_numbers")),
            ("Colorblind", lambda: self._bool_value(self.settings.video.colorblind_indicators), lambda direction: self._toggle_video("colorblind_indicators")),
            ("Reduced motion", lambda: self._bool_value(self.settings.video.reduced_motion), lambda direction: self._toggle_video("reduced_motion")),
            ("Reduced flashes", lambda: self._bool_value(self.settings.video.reduced_flashes), lambda direction: self._toggle_video("reduced_flashes")),
            ("Unverified assets", lambda: self._bool_value(self.settings.video.allow_unverified_assets), lambda direction: self._toggle_video("allow_unverified_assets")),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def _fps_rows(self) -> list[Row]:
        return [("FPS", self._fps_value, self._change_fps), ("Назад", lambda: "", lambda direction: None)]

    def _audio_rows(self) -> list[Row]:
        return [
            ("Музыка", self._music_value, self._change_music),
            ("Эффекты", self._sfx_value, self._change_sfx),
            ("Интерфейс", self._interface_value, self._change_interface),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def _control_rows(self) -> list[Row]:
        return [("Переназначить", lambda: "", self._open_controls), ("Сброс управления", lambda: "Готово", self._reset_controls), ("Назад", lambda: "", lambda direction: None)]

    def _open_controls(self, direction: int) -> None:
        if self.context is not None and not self.context.state_manager.has_pending_change:
            self.context.state_manager.request_change(GameState.CONTROLS)

    def _back_row(self) -> list[Row]:
        return [("Назад", lambda: "", lambda direction: None)]

    def _resolution_value(self) -> str:
        return f"{self.settings.video.width}x{self.settings.video.height}"

    def _change_resolution(self, direction: int) -> None:
        options = [(1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440)]
        current = (self.settings.video.width, self.settings.video.height)
        index = options.index(current) if current in options else 0
        self.settings.video.width, self.settings.video.height = options[(index + direction) % len(options)]

    def _display_mode_value(self) -> str:
        return "Оконный" if self.settings.video.display_mode == "windowed" else "Полный"

    def _change_display_mode(self, direction: int) -> None:
        self.settings.video.display_mode = "fullscreen" if self.settings.video.display_mode == "windowed" else "windowed"
        self.settings.video.fullscreen = self.settings.video.display_mode == "fullscreen"

    def _fps_value(self) -> str:
        return "Без ограничений" if self.settings.video.fps_limit == 0 else str(self.settings.video.fps_limit)

    def _change_fps(self, direction: int) -> None:
        current = self.settings.video.fps_limit
        index = FPS_OPTIONS.index(current) if current in FPS_OPTIONS else FPS_OPTIONS.index(60)
        self.settings.video.fps_limit = FPS_OPTIONS[(index + direction) % len(FPS_OPTIONS)]

    def _music_value(self) -> str:
        return f"{int(self.settings.audio.music_volume * 100)}%"

    def _change_music(self, direction: int) -> None:
        self.settings.audio.music_volume = max(0.0, min(1.0, self.settings.audio.music_volume + direction * 0.1))

    def _sfx_value(self) -> str:
        return f"{int(self.settings.audio.sfx_volume * 100)}%"

    def _change_sfx(self, direction: int) -> None:
        self.settings.audio.sfx_volume = max(0.0, min(1.0, self.settings.audio.sfx_volume + direction * 0.1))

    def _interface_value(self) -> str:
        return f"{int(self.settings.audio.interface_volume * 100)}%"

    def _change_interface(self, direction: int) -> None:
        self.settings.audio.interface_volume = max(0.0, min(1.0, self.settings.audio.interface_volume + direction * 0.1))

    def _reset_controls(self, direction: int) -> None:
        self.settings.controls.keyboard = {player: dict(mapping) for player, mapping in DEFAULT_KEYBOARD.items()}

    def _particles_value(self) -> str:
        return "Вкл" if self.settings.video.particles else "Выкл"

    def _toggle_particles(self, direction: int) -> None:
        self.settings.video.particles = not self.settings.video.particles

    def _shake_value(self) -> str:
        return "Вкл" if self.settings.video.camera_shake else "Выкл"

    def _toggle_shake(self, direction: int) -> None:
        self.settings.video.camera_shake = not self.settings.video.camera_shake

    def _fullscreen_value(self) -> str:
        return "Вкл" if self.settings.video.fullscreen else "Выкл"

    def _toggle_fullscreen(self, direction: int) -> None:
        self.settings.video.fullscreen = not self.settings.video.fullscreen

    def _bool_value(self, value: bool) -> str:
        return "On" if value else "Off"

    def _toggle_video(self, field: str) -> None:
        setattr(self.settings.video, field, not getattr(self.settings.video, field))

    def draw(self, surface, fonts=None, t=None) -> None:
        fonts = fonts or self.fonts
        if fonts is None:
            return
        draw_background(surface, self.time if t is None else t)
        draw_text(surface, fonts["title"], "Настройки", (116, 100), COLORS["white"])
        for index, (label, _) in enumerate(self.sections):
            rect = self._section_rect(index)
            active = index == self.section_index
            pygame.draw.rect(surface, COLORS["gold"] if active else COLORS["panel_light"], rect, border_radius=8)
            draw_text(surface, fonts["tiny"], label, rect.center, COLORS["white"], center=True)
        for index, (label, value, _) in enumerate(self.rows):
            spacing = 32 if len(self.rows) > 8 else 48
            y = 232 + index * spacing
            row_font = fonts["small"] if len(self.rows) > 8 else fonts["menu"]
            draw_text(surface, row_font, label, (124, y), COLORS["gold"] if index == self.selected else COLORS["white"])
            draw_text(surface, row_font, value(), (610, y), COLORS["cyan"])

