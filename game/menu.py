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
        for command in ("light_punch", "heavy_punch", "pause", "energy")
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


def draw_background(surface: pygame.Surface, t: float) -> None:
    surface.fill((7, 10, 18))
    for y in range(0, VIRTUAL_HEIGHT, 3):
        blend = y / VIRTUAL_HEIGHT
        color = (
            int(10 + 24 * blend),
            int(14 + 26 * blend),
            int(22 + 28 * blend),
        )
        pygame.draw.line(surface, color, (0, y), (VIRTUAL_WIDTH, y))

    mountain_color = (18, 28, 40)
    for i, x in enumerate((140, 430, 740, 1040)):
        points = [(x - 150, 610), (x - 90, 430 + i * 12), (x - 30, 500), (x + 40, 380), (x + 150, 610)]
        pygame.draw.polygon(surface, mountain_color, points)
        pygame.draw.polygon(surface, (38, 53, 70), points, 2)

    for i in range(24):
        x = (i * 92 + int(t * 18)) % (VIRTUAL_WIDTH + 160) - 80
        height = 82 + (i % 6) * 22
        rect = pygame.Rect(x, 490 - height, 52 + (i % 3) * 16, height)
        pygame.draw.rect(surface, (17, 24, 32), rect)
        if i % 2 == 0:
            pygame.draw.line(surface, (63, 201, 197), rect.topleft, rect.topright, 2)

    for i in range(4):
        cx = 220 + i * 250
        cy = 200 + (i % 2) * 40
        pygame.draw.circle(surface, (232, 181, 82), (cx, cy), 8)
        pygame.draw.circle(surface, (255, 215, 132), (cx, cy), 3)

    pygame.draw.rect(surface, (16, 18, 22), (0, 530, VIRTUAL_WIDTH, 190))
    for x in range(0, VIRTUAL_WIDTH, 64):
        pygame.draw.line(surface, (37, 43, 50), (x, 530), (x + 90, VIRTUAL_HEIGHT), 1)


def draw_arena_preview(surface: pygame.Surface, arena: ArenaDefinition, rect: pygame.Rect, t: float = 0.0) -> None:
    pygame.draw.rect(surface, arena.palette[0], rect, border_radius=8)
    if arena.key == "neon_foundry":
        pygame.draw.rect(surface, (38, 24, 20), (rect.x + 150, rect.y + 240, 250, 34), border_radius=8)
        pygame.draw.rect(surface, (255, 140, 44), (rect.x + 170, rect.y + 250, 210, 18), border_radius=6)
        for x in range(rect.x + 120, rect.right - 120, 70):
            pygame.draw.line(surface, arena.palette[2], (x, rect.y + 200), (x + 34, rect.bottom - 40), 2)
    elif arena.key == "storm_pier":
        pygame.draw.circle(surface, arena.palette[2], (rect.centerx + 180, rect.y + 120), 54)
        for x in range(rect.x + 60, rect.right - 40, 88):
            wave = int(8 + 5 * math.sin(t + x * 0.02))
            pygame.draw.arc(surface, arena.palette[1], (x, rect.bottom - 120 + wave, 70, 28), 0, math.pi, 2)
    elif arena.key == "glass_court":
        for i in range(8):
            x = rect.x + 90 + i * 96
            y = rect.y + 150 + (i % 2) * 28
            points = [(x, y), (x + 54, y + 36), (x + 18, y + 96)]
            pygame.draw.polygon(surface, (42, 44, 58), points)
            pygame.draw.polygon(surface, arena.palette[1] if i % 2 else arena.palette[2], points, 2)
    elif arena.key == "great_wall":
        pygame.draw.rect(surface, (88, 72, 52), (rect.x + 80, rect.y + 220, 840, 36), border_radius=6)
        for x in range(rect.x + 90, rect.right - 80, 120):
            pygame.draw.rect(surface, arena.palette[2], (x, rect.y + 180, 60, 60), border_radius=8)
            pygame.draw.rect(surface, arena.palette[1], (x + 10, rect.y + 190, 40, 40), border_radius=6)
    elif arena.key == "dragon_mountains":
        points = [(rect.x + 70, rect.bottom - 70), (rect.centerx - 120, rect.y + 180), (rect.centerx, rect.y + 90), (rect.centerx + 150, rect.y + 190), (rect.right - 70, rect.bottom - 70)]
        pygame.draw.polygon(surface, (30, 54, 44), points)
        pygame.draw.polygon(surface, arena.palette[1], points, 3)
        pygame.draw.circle(surface, arena.palette[2], (rect.centerx + 140, rect.y + 80), 24)
    elif arena.key == "pagoda_ridge":
        for x in range(rect.x + 100, rect.right - 100, 130):
            pygame.draw.rect(surface, (72, 40, 60), (x, rect.y + 210, 54, 90), border_radius=8)
            pygame.draw.rect(surface, arena.palette[2], (x + 10, rect.y + 200, 34, 32), border_radius=4)
        pygame.draw.circle(surface, (242, 202, 132), (rect.centerx, rect.y + 96), 34)


class MenuScreen:
    def __init__(self) -> None:
        self.items = [
            MenuItem("История", "story"),
            MenuItem("Аркада", "arcade"),
            MenuItem("Турнир", "tournament"),
            MenuItem("Локальный VS", "vs"),
            MenuItem("Тренировка", "training"),
            MenuItem("Настройки", "settings"),
            MenuItem("Выход", "quit"),
        ]
        self.selected = 0

    def update(self, pressed: dict[str, bool]) -> str | None:
        if pressed.get("down"):
            self.selected = (self.selected + 1) % len(self.items)
        if pressed.get("up"):
            self.selected = (self.selected - 1) % len(self.items)
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

        start_y = 302
        for i, item in enumerate(self.items):
            y = start_y + i * 52
            selected = i == self.selected
            color = COLORS["gold"] if selected else COLORS["white"]
            if selected:
                pygame.draw.rect(
                    surface,
                    (42, 48, 57),
                    pygame.Rect(84, y - 8, 310, 42),
                    border_radius=6,
                )
                pygame.draw.line(surface, COLORS["red"], (88, y + 33), (384, y + 33), 3)
            draw_text(surface, fonts["menu"], item.label, (108, y), color)

        panel = pygame.Rect(640, 115, 470, 390)
        pygame.draw.rect(surface, (24, 28, 34), panel, border_radius=8)
        pygame.draw.rect(surface, (63, 201, 197), panel, 2, border_radius=8)
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
        self.rows: list[tuple[str, Callable[[], str], Callable[[int], None]]] = [
            ("Сложность", self._difficulty_value, self._change_difficulty),
            ("Раунды", self._rounds_value, self._change_rounds),
            ("Таймер", self._timer_value, self._change_timer),
            ("Частицы", self._particles_value, self._toggle_particles),
            ("Тряска камеры", self._shake_value, self._toggle_shake),
            ("Полноэкранный режим", self._fullscreen_value, self._toggle_fullscreen),
            ("Назад", lambda: "", lambda direction: None),
        ]

    def update(self, pressed: dict[str, bool]) -> str | None:
        if pressed.get("down"):
            self.selected = (self.selected + 1) % len(self.rows)
        if pressed.get("up"):
            self.selected = (self.selected - 1) % len(self.rows)
        if pressed.get("left"):
            self.rows[self.selected][2](-1)
        if pressed.get("right") or accept_pressed(pressed):
            if self.rows[self.selected][0] == "Назад":
                return "back"
            self.rows[self.selected][2](1)
        if back_pressed(pressed):
            return "back"
        return None

    def draw(self, surface: pygame.Surface, fonts: dict[str, pygame.font.Font], t: float) -> None:
        draw_background(surface, t)
        draw_text(surface, fonts["title"], "Настройки", (96, 80), COLORS["white"])
        draw_text(
            surface,
            fonts["small"],
            "Стрелки меняют значения. Блок — назад.",
            (102, 158),
            COLORS["muted"],
        )
        for i, (label, value_func, _) in enumerate(self.rows):
            y = 242 + i * 58
            selected = i == self.selected
            row = pygame.Rect(94, y - 10, 720, 46)
            if selected:
                pygame.draw.rect(surface, COLORS["panel_light"], row, border_radius=6)
                pygame.draw.line(surface, COLORS["gold"], row.bottomleft, row.bottomright, 3)
            draw_text(surface, fonts["menu"], label, (124, y), COLORS["gold"] if selected else COLORS["white"])
            draw_text(surface, fonts["menu"], value_func(), (520, y), COLORS["cyan"])

    def _difficulty_value(self) -> str:
        labels = {"easy": "Легко", "normal": "Нормально", "hard": "Сложно"}
        return labels.get(self.settings.gameplay.difficulty, self.settings.gameplay.difficulty.title())

    def _change_difficulty(self, direction: int) -> None:
        options = ["easy", "normal", "hard"]
        current = options.index(self.settings.gameplay.difficulty)
        self.settings.gameplay.difficulty = options[(current + direction) % len(options)]

    def _rounds_value(self) -> str:
        return str(self.settings.gameplay.rounds_to_win)

    def _change_rounds(self, direction: int) -> None:
        self.settings.gameplay.rounds_to_win = max(
            1, min(5, self.settings.gameplay.rounds_to_win + direction)
        )

    def _timer_value(self) -> str:
        return str(self.settings.gameplay.round_seconds)

    def _change_timer(self, direction: int) -> None:
        self.settings.gameplay.round_seconds = max(
            30, min(180, self.settings.gameplay.round_seconds + direction * 10)
        )

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
    ) -> str | None:
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

    def update(self, pressed: dict[str, bool]) -> str | None:
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
