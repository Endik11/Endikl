from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

import pygame

from .fighter import FIGHTER_DEFINITIONS
from .settings import COLORS, GAME_TITLE, VIRTUAL_HEIGHT, VIRTUAL_WIDTH
from .sprites import SPRITE_ANCHOR, SPRITE_FACTORY


@dataclass(frozen=True)
class MenuItem:
    label: str
    action: str


@dataclass(frozen=True)
class ArenaDefinition:
    key: str
    name: str
    subtitle: str
    palette: tuple[tuple[int, int, int], tuple[int, int, int], tuple[int, int, int]]
    hazard: str


ARENAS = {
    "neon_foundry": ArenaDefinition(
        key="neon_foundry",
        name="Нефритовая кузня",
        subtitle="Квартал кузниц под электрическим дождём.",
        palette=((16, 20, 24), (207, 53, 63), (63, 201, 197)),
        hazard="molten_press",
    ),
    "storm_pier": ArenaDefinition(
        key="storm_pier",
        name="Штормовой пирс",
        subtitle="Лунный причал, где волны бьют по стальным столбам.",
        palette=((10, 18, 28), (79, 150, 214), (232, 181, 82)),
        hazard="tidal_edge",
    ),
    "glass_court": ArenaDefinition(
        key="glass_court",
        name="Стеклянный ринг",
        subtitle="Разбитый дворецкий трибунал над древним городом.",
        palette=((24, 24, 31), (142, 104, 207), (238, 241, 244)),
        hazard="falling_shards",
    ),
    "great_wall": ArenaDefinition(
        key="great_wall",
        name="Великая стена",
        subtitle="Крепость из камня, где ветер несёт пыль и легенды.",
        palette=((18, 24, 34), (164, 112, 62), (232, 181, 82)),
        hazard="crumbling_wall",
    ),
    "dragon_mountains": ArenaDefinition(
        key="dragon_mountains",
        name="Драконьи горы",
        subtitle="Склоны, укрытые туманом и древними знаками.",
        palette=((12, 22, 30), (90, 164, 122), (217, 232, 238)),
        hazard="mountain_edge",
    ),
    "pagoda_ridge": ArenaDefinition(
        key="pagoda_ridge",
        name="Пагодный хребет",
        subtitle="Ночной перевал с фонарями, храмами и ритмом ветра.",
        palette=((12, 16, 24), (163, 86, 164), (242, 202, 132)),
        hazard="temple_fall",
    ),
}


def accept_pressed(pressed: dict[str, bool]) -> bool:
    return any(
        pressed.get(command, False)
        for command in ("light_punch", "heavy_punch", "energy", "throw", "stance")
    )


def back_pressed(pressed: dict[str, bool]) -> bool:
    return pressed.get("block", False)


def draw_text(
    surface: pygame.Surface,
    font: pygame.font.Font,
    text: str,
    pos: tuple[int, int],
    color: tuple[int, int, int] = COLORS["white"],
    center: bool = False,
) -> pygame.Rect:
    rendered = font.render(text, True, color)
    rect = rendered.get_rect()
    if center:
        rect.center = pos
    else:
        rect.topleft = pos
    surface.blit(rendered, rect)
    return rect


def build_pause_menu_items(language: str = "ru") -> list[MenuItem]:
    if language != "ru":
        return [
            MenuItem("Resume", "resume"),
            MenuItem("Settings", "settings"),
            MenuItem("Restart", "restart"),
            MenuItem("Main menu", "menu"),
            MenuItem("Quit", "quit_game"),
        ]
    return [
        MenuItem("Продолжить", "resume"),
        MenuItem("Настройки", "settings"),
        MenuItem("Рестарт", "restart"),
        MenuItem("Главное меню", "menu"),
        MenuItem("Выйти", "quit_game"),
    ]


def draw_background(surface: pygame.Surface, t: float) -> None:
    surface.fill((5, 7, 12))
    for y in range(0, VIRTUAL_HEIGHT, 4):
        blend = y / VIRTUAL_HEIGHT
        color = (
            int(8 + 24 * blend),
            int(12 + 24 * blend),
            int(18 + 28 * blend),
        )
        pygame.draw.line(surface, color, (0, y), (VIRTUAL_WIDTH, y))

    for i, x in enumerate((120, 360, 700, 1040)):
        points = [(x - 180, 610), (x - 100, 420 + i * 12), (x - 20, 500), (x + 60, 360), (x + 180, 610)]
        pygame.draw.polygon(surface, (16, 18, 24), points)
        pygame.draw.polygon(surface, (72, 38, 34), points, 2)

    for i in range(26):
        x = (i * 94 + int(t * 24)) % (VIRTUAL_WIDTH + 180) - 90
        height = 86 + (i % 5) * 22
        rect = pygame.Rect(x, 500 - height, 56 + (i % 4) * 12, height)
        pygame.draw.rect(surface, (11, 15, 21), rect)
        if i % 2 == 0:
            pygame.draw.line(surface, (207, 53, 63), rect.topleft, rect.topright, 2)

    for i in range(5):
        cx = 170 + i * 245
        cy = 180 + (i % 2) * 36
        pygame.draw.circle(surface, (112, 24, 33), (cx, cy), 10)
        pygame.draw.circle(surface, (232, 181, 82), (cx, cy), 3)

    pygame.draw.rect(surface, (12, 14, 18), (0, 520, VIRTUAL_WIDTH, 200))
    for x in range(0, VIRTUAL_WIDTH, 70):
        pygame.draw.line(surface, (36, 44, 56), (x, 520), (x + 70, VIRTUAL_HEIGHT), 1)

    pygame.draw.rect(surface, (24, 30, 38), (66, 56, 1148, 622), border_radius=22)
    pygame.draw.rect(surface, (207, 53, 63), (66, 56, 1148, 622), 3, border_radius=22)


def draw_arena_preview(surface: pygame.Surface, arena: ArenaDefinition, rect: pygame.Rect, t: float = 0.0) -> None:
    pygame.draw.rect(surface, arena.palette[0], rect, border_radius=12)
    pygame.draw.rect(surface, (20, 24, 30), rect.inflate(-8, -8), border_radius=8)
    if arena.key == "neon_foundry":
        pygame.draw.rect(surface, (38, 24, 20), (rect.x + 140, rect.y + 240, 280, 36), border_radius=10)
        pygame.draw.rect(surface, (255, 140, 44), (rect.x + 160, rect.y + 250, 240, 18), border_radius=8)
        for x in range(rect.x + 110, rect.right - 110, 70):
            pygame.draw.line(surface, arena.palette[2], (x, rect.y + 205), (x + 38, rect.bottom - 44), 3)
    elif arena.key == "storm_pier":
        pygame.draw.circle(surface, arena.palette[2], (rect.centerx + 180, rect.y + 118), 58)
        for x in range(rect.x + 50, rect.right - 40, 92):
            wave = int(8 + 6 * math.sin(t + x * 0.02))
            pygame.draw.arc(surface, arena.palette[1], (x, rect.bottom - 122 + wave, 82, 36), 0, math.pi, 3)
    elif arena.key == "glass_court":
        for i in range(8):
            x = rect.x + 84 + i * 96
            y = rect.y + 152 + (i % 2) * 24
            points = [(x, y), (x + 56, y + 34), (x + 18, y + 98)]
            pygame.draw.polygon(surface, (45, 46, 58), points)
            pygame.draw.polygon(surface, arena.palette[1] if i % 2 else arena.palette[2], points, 2)
    elif arena.key == "great_wall":
        pygame.draw.rect(surface, (86, 68, 52), (rect.x + 80, rect.y + 220, 840, 36), border_radius=8)
        for x in range(rect.x + 90, rect.right - 80, 122):
            pygame.draw.rect(surface, arena.palette[2], (x, rect.y + 176, 64, 64), border_radius=10)
            pygame.draw.rect(surface, arena.palette[1], (x + 10, rect.y + 186, 44, 44), border_radius=7)
    elif arena.key == "dragon_mountains":
        points = [(rect.x + 70, rect.bottom - 62), (rect.centerx - 120, rect.y + 180), (rect.centerx, rect.y + 94), (rect.centerx + 150, rect.y + 190), (rect.right - 70, rect.bottom - 62)]
        pygame.draw.polygon(surface, (30, 54, 44), points)
        pygame.draw.polygon(surface, arena.palette[1], points, 3)
        pygame.draw.circle(surface, arena.palette[2], (rect.centerx + 140, rect.y + 80), 26)
    elif arena.key == "pagoda_ridge":
        for x in range(rect.x + 90, rect.right - 90, 128):
            pygame.draw.rect(surface, (74, 42, 62), (x, rect.y + 208, 56, 92), border_radius=8)
            pygame.draw.rect(surface, arena.palette[2], (x + 10, rect.y + 198, 36, 34), border_radius=4)
        pygame.draw.circle(surface, (242, 202, 132), (rect.centerx, rect.y + 96), 38)


class CollectionScreen:
    def __init__(self, profile) -> None:
        self.profile = profile
        self.selected = 0

    def update(self, pressed: dict[str, bool], events: list[pygame.event.Event] | None = None) -> str | None:
        if pressed.get("block"):
            return "back"
        return None

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font], t: float) -> None:
        draw_background(surface, t)
        draw_text(surface, fonts["title"], "Коллекция", (96, 80), COLORS["white"])
        draw_text(surface, fonts["small"], "Собранные бойцы, арены и предметы", (102, 158), COLORS["muted"])
        draw_text(surface, fonts["menu"], f"Бойцы: {', '.join(self.profile.unlocked_fighters)}", (110, 238), COLORS["gold"])
        draw_text(surface, fonts["menu"], f"Арены: {', '.join(self.profile.unlocked_arenas)}", (110, 288), COLORS["gold"])
        draw_text(surface, fonts["menu"], f"Предметы: {len(self.profile.purchased_items)}", (110, 338), COLORS["gold"])


class StatsScreen:
    def __init__(self, profile) -> None:
        self.profile = profile

    def update(self, pressed: dict[str, bool], events: list[pygame.event.Event] | None = None) -> str | None:
        if pressed.get("block"):
            return "back"
        return None

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font], t: float) -> None:
        draw_background(surface, t)
        draw_text(surface, fonts["title"], "Статистика", (96, 80), COLORS["white"])
        record = self.profile.record
        draw_text(surface, fonts["menu"], f"Побед: {record.wins}", (110, 240), COLORS["gold"])
        draw_text(surface, fonts["menu"], f"Поражений: {record.losses}", (110, 292), COLORS["gold"])
        draw_text(surface, fonts["menu"], f"Идеальные: {record.perfects}", (110, 344), COLORS["gold"])
        draw_text(surface, fonts["menu"], f"Финальные: {record.fatalities + record.brutalities + record.stage_fatalities}", (110, 396), COLORS["gold"])


class MenuScreen:
    def __init__(self) -> None:
        self.items = [
            MenuItem("Начать бой", "story"),
            MenuItem("Выбор персонажа", "vs"),
            MenuItem("Выбор арены", "arena"),
            MenuItem("Тренировка", "training"),
            MenuItem("Башня испытаний", "tournament"),
            MenuItem("Магазин", "shop"),
            MenuItem("Коллекция", "collection"),
            MenuItem("Статистика", "stats"),
            MenuItem("Настройки", "settings"),
            MenuItem("Выход", "quit"),
        ]
        self.selected = 0

    def _mouse_pos(self) -> tuple[int, int]:
        try:
            mouse_pos = pygame.mouse.get_pos()
        except pygame.error:
            return (0, 0)
        surface = pygame.display.get_surface()
        if surface is None:
            return mouse_pos
        screen_w, screen_h = surface.get_size()
        if screen_w <= 0 or screen_h <= 0:
            return mouse_pos
        if (screen_w, screen_h) == (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
            return mouse_pos
        return (
            int(mouse_pos[0] * VIRTUAL_WIDTH / screen_w),
            int(mouse_pos[1] * VIRTUAL_HEIGHT / screen_h),
        )

    def _item_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(84, 262 + index * 46 - 8, 320, 40)

    def update(self, pressed: dict[str, bool], events: list[pygame.event.Event] | None = None) -> str | None:
        if events is None:
            events = []
        mouse_pos = self._mouse_pos()
        for index, item in enumerate(self.items):
            if self._item_rect(index).collidepoint(mouse_pos):
                self.selected = index
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                for index, item in enumerate(self.items):
                    if self._item_rect(index).collidepoint(mouse_pos):
                        self.selected = index
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, item in enumerate(self.items):
                    if self._item_rect(index).collidepoint(mouse_pos):
                        self.selected = index
                        return item.action
        if pressed.get("down"):
            self.selected = (self.selected + 1) % len(self.items)
        if pressed.get("up"):
            self.selected = (self.selected - 1) % len(self.items)
        if pressed.get("pause"):
            return self.items[self.selected].action
        if accept_pressed(pressed):
            return self.items[self.selected].action
        return None

    def draw(
        self,
        surface: pygame.Surface,
        fonts: dict[str, pygame.font.Font],
        t: float,
    ) -> None:
        draw_background(surface, t)
        draw_text(surface, fonts["title"], "Mortal End", (94, 88), COLORS["white"])
        draw_text(surface, fonts["subtitle"], "Наследие", (104, 166), COLORS["gold"])
        draw_text(
            surface,
            fonts["small"],
            "Русская локализация и новые арены",
            (99, 218),
            COLORS["muted"],
        )

        start_y = 262
        for i, item in enumerate(self.items):
            y = start_y + i * 46
            selected = i == self.selected
            color = COLORS["gold"] if selected else COLORS["white"]
            if selected:
                pygame.draw.rect(
                    surface,
                    (42, 48, 57),
                    pygame.Rect(84, y - 8, 320, 40),
                    border_radius=6,
                )
                pygame.draw.line(surface, COLORS["red"], (88, y + 31), (392, y + 31), 3)
            draw_text(surface, fonts["menu"], item.label, (108, y), color)

        panel = pygame.Rect(640, 115, 470, 390)
        pygame.draw.rect(surface, (18, 21, 28), panel, border_radius=12)
        pygame.draw.rect(surface, (207, 53, 63), panel, 2, border_radius=12)
        pygame.draw.rect(surface, (40, 26, 26), panel.inflate(-12, -12), border_radius=10)
        draw_text(surface, fonts["menu"], GAME_TITLE, (674, 148), COLORS["gold"])
        body = [
            "Четыре оригинальных бойца.",
            "Шесть сцен с восточным настроением.",
            "Хитбоксы, хербоксы и комбо-буфер.",
            "Финальные добивания и завершения.",
            "Клавиатура, геймпад и русская локализация.",
        ]
        for index, line in enumerate(body):
            draw_text(surface, fonts["body"], line, (676, 205 + index * 42), COLORS["white"])


class SettingsScreen:
    def __init__(self, settings) -> None:
        self.settings = settings
        self.selected = 0
        self.sections = [
            ("Видео", self._video_rows),
            ("FPS", self._fps_rows),
            ("Звук", self._audio_rows),
            ("Управление", self._control_rows),
            ("Назад", self._back_row),
        ]
        self.section_index = 0
        self.rows: list[tuple[str, Callable[[], str], Callable[[int], None]]] = []
        self._refresh_rows()

    def _mouse_pos(self) -> tuple[int, int]:
        try:
            mouse_pos = pygame.mouse.get_pos()
        except pygame.error:
            return (0, 0)
        surface = pygame.display.get_surface()
        if surface is None:
            return mouse_pos
        screen_w, screen_h = surface.get_size()
        if screen_w <= 0 or screen_h <= 0:
            return mouse_pos
        if (screen_w, screen_h) == (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
            return mouse_pos
        return (
            int(mouse_pos[0] * VIRTUAL_WIDTH / screen_w),
            int(mouse_pos[1] * VIRTUAL_HEIGHT / screen_h),
        )

    def _row_rect(self, index: int) -> pygame.Rect:
        return pygame.Rect(94, 242 + index * 48 - 10, 720, 38)

    def _section_rect(self, section_index: int) -> pygame.Rect:
        return pygame.Rect(94 + section_index * 124, 190, 110, 34)

    def update(self, pressed: dict[str, bool], events: list[pygame.event.Event] | None = None) -> str | None:
        if events is None:
            events = []
        mouse_pos = self._mouse_pos()

        for index, row in enumerate(self.rows):
            if self._row_rect(index).collidepoint(mouse_pos):
                self.selected = index

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for index, row in enumerate(self.rows):
                    if self._row_rect(index).collidepoint(mouse_pos):
                        self.selected = index
                        if row[0] == "Назад":
                            return "back"
                        row[2](1)
                        return None
                for section_index, (label, _) in enumerate(self.sections):
                    if self._section_rect(section_index).collidepoint(mouse_pos):
                        self.select_section(section_index)
                        return None

        if pressed.get("right"):
            if self.section_index in {1, 2, 3}:
                self.rows[self.selected][2](1)
            else:
                self.select_section(min(len(self.sections) - 1, self.section_index + 1))
            return None
        if pressed.get("left"):
            if self.section_index in {1, 2, 3}:
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

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font], t: float) -> None:
        draw_background(surface, t)
        panel = pygame.Rect(70, 70, 1120, 560)
        pygame.draw.rect(surface, (17, 21, 28), panel, border_radius=18)
        pygame.draw.rect(surface, COLORS["gold"], panel, 2, border_radius=18)
        pygame.draw.rect(surface, (24, 30, 38), pygame.Rect(86, 98, 1088, 500), border_radius=14)
        draw_text(surface, fonts["title"], "Настройки", (116, 100), COLORS["white"])
        draw_text(surface, fonts["small"], "Клик по вкладкам — быстрая навигация. Блок — назад.", (120, 150), COLORS["muted"])

        for section_index, (label, _) in enumerate(self.sections):
            rect = pygame.Rect(94 + section_index * 124, 190, 110, 34)
            active = section_index == self.section_index
            pygame.draw.rect(surface, (44, 51, 64) if not active else COLORS["gold"], rect, border_radius=8)
            color = COLORS["white"] if active else COLORS["muted"]
            draw_text(surface, fonts["tiny"], label, (rect.centerx, rect.centery + 2), color, center=True)

        for i, (label, value_func, _) in enumerate(self.rows):
            y = 242 + i * 48
            selected = i == self.selected
            row = pygame.Rect(94, y - 10, 720, 38)
            if selected:
                pygame.draw.rect(surface, (36, 43, 53), row, border_radius=6)
                pygame.draw.line(surface, COLORS["gold"], row.bottomleft, row.bottomright, 3)
            draw_text(surface, fonts["menu"], label, (124, y), COLORS["gold"] if selected else COLORS["white"])
            draw_text(surface, fonts["menu"], value_func(), (520, y), COLORS["cyan"])

        footer = pygame.Rect(94, 600, 720, 76)
        pygame.draw.rect(surface, (24, 30, 38), footer, border_radius=10)
        draw_text(surface, fonts["small"], f"Текущий раздел: {self.sections[self.section_index][0]}", (116, 620), COLORS["gold"])
        draw_text(surface, fonts["tiny"], "Сохранение происходит при выходе из настроек", (116, 644), COLORS["muted"])

    def select_section(self, index: int) -> None:
        if 0 <= index < len(self.sections):
            self.section_index = index
            self.selected = 0
            self._refresh_rows()

    def _refresh_rows(self) -> None:
        self.rows = self.sections[self.section_index][1]()
        self.selected = min(self.selected, max(0, len(self.rows) - 1))

    def _video_rows(self) -> list[tuple[str, Callable[[], str], Callable[[int], None]]]:
        return [
            ("Разрешение", self._resolution_value, self._change_resolution),
            ("Режим окна", self._display_mode_value, self._change_display_mode),
            ("Полноэкранный", self._fullscreen_value, self._toggle_fullscreen),
            ("Частицы", self._particles_value, self._toggle_particles),
            ("Тряска камеры", self._shake_value, self._toggle_shake),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def _fps_rows(self) -> list[tuple[str, Callable[[], str], Callable[[int], None]]]:
        return [
            ("FPS", self._fps_value, self._change_fps),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def _audio_rows(self) -> list[tuple[str, Callable[[], str], Callable[[int], None]]]:
        return [
            ("Музыка", self._music_value, self._change_music),
            ("Эффекты", self._sfx_value, self._change_sfx),
            ("Интерфейс", self._interface_value, self._change_interface),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def _control_rows(self) -> list[tuple[str, Callable[[], str], Callable[[int], None]]]:
        return [
            ("Сброс управления", self._reset_controls_value, self._reset_controls),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def _back_row(self) -> list[tuple[str, Callable[[], str], Callable[[int], None]]]:
        return [("Назад", lambda: "", lambda direction: None)]

    def _resolution_value(self) -> str:
        return f"{self.settings.video.width}x{self.settings.video.height}"

    def _change_resolution(self, direction: int) -> None:
        options = [(1280, 720), (1366, 768), (1600, 900), (1920, 1080), (2560, 1440)]
        current = (self.settings.video.width, self.settings.video.height)
        index = options.index(current) if current in options else 3
        new_index = (index + direction) % len(options)
        self.settings.video.width, self.settings.video.height = options[new_index]

    def _display_mode_value(self) -> str:
        return "Оконный" if self.settings.video.display_mode == "windowed" else "Полный"

    def _change_display_mode(self, direction: int) -> None:
        modes = ["windowed", "fullscreen"]
        current = self.settings.video.display_mode if self.settings.video.display_mode in modes else "windowed"
        index = modes.index(current)
        self.settings.video.display_mode = modes[(index + direction) % len(modes)]
        self.settings.video.fullscreen = self.settings.video.display_mode == "fullscreen"

    def _fps_value(self) -> str:
        return "Без ограничений" if self.settings.video.fps_limit == 0 else str(self.settings.video.fps_limit)

    def _change_fps(self, direction: int) -> None:
        from .settings import FPS_OPTIONS
        current = self.settings.video.fps_limit
        options = FPS_OPTIONS
        index = options.index(current) if current in options else options.index(60)
        self.settings.video.fps_limit = options[(index + direction) % len(options)]

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

    def _reset_controls_value(self) -> str:
        return "Готово"

    def _reset_controls(self, direction: int) -> None:
        from .settings import DEFAULT_KEYBOARD
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


class CharacterSelectScreen:
    def __init__(self, mode: str, p1_key: str = "kael", p2_key: str = "sable") -> None:
        self.mode = mode
        self.keys = list(FIGHTER_DEFINITIONS.keys())
        self.p1_index = self.keys.index(p1_key) if p1_key in self.keys else 0
        self.p2_index = self.keys.index(p2_key) if p2_key in self.keys else 1

    @property
    def p1_key(self) -> str:
        return self.keys[self.p1_index]

    @property
    def p2_key(self) -> str:
        return self.keys[self.p2_index]

    def update(
        self,
        p1_pressed: dict[str, bool],
        p2_pressed: dict[str, bool],
        events: list[pygame.event.Event] | None = None,
    ) -> str | None:
        if events is None:
            events = []
        mouse_pos = pygame.mouse.get_pos()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                left_rect = pygame.Rect(92, 220, 440, 330)
                right_rect = pygame.Rect(748, 220, 440, 330)
                if left_rect.collidepoint(mouse_pos):
                    self.p1_index = (self.p1_index + 1) % len(self.keys)
                elif right_rect.collidepoint(mouse_pos):
                    self.p2_index = (self.p2_index + 1) % len(self.keys)
                else:
                    for index, key in enumerate(self.keys):
                        tile = pygame.Rect(278 + index * 182, 612, 130, 66)
                        if tile.collidepoint(mouse_pos):
                            if mouse_pos[0] < 640:
                                self.p1_index = index
                            else:
                                self.p2_index = index
                            break
        if p1_pressed.get("left"):
            self.p1_index = (self.p1_index - 1) % len(self.keys)
        if p1_pressed.get("right"):
            self.p1_index = (self.p1_index + 1) % len(self.keys)

        local_select = self.mode == "vs"
        if local_select:
            if p2_pressed.get("left"):
                self.p2_index = (self.p2_index - 1) % len(self.keys)
            if p2_pressed.get("right"):
                self.p2_index = (self.p2_index + 1) % len(self.keys)
        else:
            if p1_pressed.get("down"):
                self.p2_index = (self.p2_index + 1) % len(self.keys)
                if self.p2_index == self.p1_index:
                    self.p2_index = (self.p2_index + 1) % len(self.keys)

        if accept_pressed(p1_pressed):
            if self.p1_index == self.p2_index and self.mode == "vs":
                self.p2_index = (self.p2_index + 1) % len(self.keys)
            return "arena"
        if back_pressed(p1_pressed):
            return "back"
        return None

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font], t: float) -> None:
        draw_background(surface, t)
        draw_text(surface, fonts["title"], "Выбор бойца", (90, 70), COLORS["white"])
        draw_text(
            surface,
            fonts["small"],
            "Игрок 1 — стрелки. Игрок 2 — IJKL в локальном режиме.",
            (96, 148),
            COLORS["muted"],
        )

        self._draw_fighter_panel(surface, fonts, self.p1_key, pygame.Rect(92, 220, 440, 330), "ИГРОК 1")
        opponent_label = "ИГРОК 2" if self.mode == "vs" else "СОПЕРНИК"
        self._draw_fighter_panel(surface, fonts, self.p2_key, pygame.Rect(748, 220, 440, 330), opponent_label)

        for i, key in enumerate(self.keys):
            definition = FIGHTER_DEFINITIONS[key]
            x = 278 + i * 182
            y = 612
            selected = key in (self.p1_key, self.p2_key)
            color = definition.palette[0]
            tile = pygame.Rect(x, y, 130, 66)
            pygame.draw.rect(surface, COLORS["panel_light"] if selected else COLORS["panel"], tile, border_radius=8)
            pygame.draw.rect(surface, color, tile, 3 if selected else 1, border_radius=8)
            draw_text(surface, fonts["small"], definition.name.split()[0], (tile.centerx, y + 22), COLORS["white"], center=True)

    def _draw_fighter_panel(
        self,
        surface: pygame.Surface,
        fonts: dict[str, pygame.font.Font],
        key: str,
        rect: pygame.Rect,
        label: str,
    ) -> None:
        definition = FIGHTER_DEFINITIONS[key]
        pygame.draw.rect(surface, COLORS["panel"], rect, border_radius=8)
        pygame.draw.rect(surface, definition.palette[0], rect, 3, border_radius=8)
        draw_text(surface, fonts["small"], label, (rect.x + 28, rect.y + 24), COLORS["muted"])
        draw_text(surface, fonts["menu"], definition.name, (rect.x + 28, rect.y + 66), COLORS["white"])
        draw_text(surface, fonts["body"], definition.title, (rect.x + 30, rect.y + 110), definition.palette[1])
        words = definition.story.split()
        line = ""
        y = rect.y + 164
        for word in words:
            if len(line + " " + word) > 45:
                draw_text(surface, fonts["small"], line.strip(), (rect.x + 30, y), COLORS["white"])
                y += 28
                line = word
            else:
                line += " " + word
        if line:
            draw_text(surface, fonts["small"], line.strip(), (rect.x + 30, y), COLORS["white"])

        sprite = SPRITE_FACTORY.get(definition, "idle", 0, 1, 1000)
        scaled = pygame.transform.smoothscale(sprite, (208, 226))
        sprite_anchor = pygame.Vector2(
            SPRITE_ANCHOR.x * (208 / sprite.get_width()),
            SPRITE_ANCHOR.y * (226 / sprite.get_height()),
        )
        ground = pygame.Vector2(rect.centerx + 96, rect.bottom - 18)
        dest = ground - sprite_anchor
        surface.blit(scaled, (int(dest.x), int(dest.y)))


class ArenaSelectScreen:
    def __init__(self, arena_key: str = "neon_foundry") -> None:
        self.keys = list(ARENAS.keys())
        self.index = self.keys.index(arena_key) if arena_key in self.keys else 0

    @property
    def arena_key(self) -> str:
        return self.keys[self.index]

    def update(self, pressed: dict[str, bool], events: list[pygame.event.Event] | None = None) -> str | None:
        if events is None:
            events = []
        mouse_pos = pygame.mouse.get_pos()
        preview = pygame.Rect(150, 218, 980, 360)
        left_rect = pygame.Rect(120, 610, 120, 40)
        right_rect = pygame.Rect(1040, 610, 120, 40)
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if preview.collidepoint(mouse_pos):
                    return "fight"
                if left_rect.collidepoint(mouse_pos):
                    self.index = (self.index - 1) % len(self.keys)
                elif right_rect.collidepoint(mouse_pos):
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

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font], t: float) -> None:
        draw_background(surface, t)
        draw_text(surface, fonts["title"], "Выбор арены", (90, 70), COLORS["white"])
        draw_text(surface, fonts["small"], "Стрелки меняют сцену. Подтверждение — бой.", (96, 148), COLORS["muted"])

        arena = ARENAS[self.arena_key]
        preview = pygame.Rect(150, 218, 980, 360)
        draw_arena_preview(surface, arena, preview, t)

        draw_text(surface, fonts["menu"], arena.name, (VIRTUAL_WIDTH // 2, 610), COLORS["gold"], center=True)
        draw_text(surface, fonts["body"], arena.subtitle, (VIRTUAL_WIDTH // 2, 650), COLORS["white"], center=True)
