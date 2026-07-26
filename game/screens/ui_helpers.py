from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from ..arena_catalog import ArenaDefinition
from ..settings import COLORS, VIRTUAL_HEIGHT, VIRTUAL_WIDTH


_KEY_ART: pygame.Surface | None = None
_KEY_ART_SCALED: pygame.Surface | None = None


@dataclass(frozen=True)
class MenuItem:
    label: str
    action: str


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
    rect.center = pos if center else rect.center
    if not center:
        rect.topleft = pos
    surface.blit(rendered, rect)
    return rect


def draw_background(surface: pygame.Surface, t: float, *, key_art: bool = False) -> None:
    global _KEY_ART, _KEY_ART_SCALED
    if key_art:
        if _KEY_ART is None:
            try:
                from ..platform_paths import asset_path

                _KEY_ART = pygame.image.load(asset_path("ui", "shadow_realm_keyart.png"))
            except (OSError, pygame.error):
                _KEY_ART = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
                _KEY_ART.fill((5, 7, 12))
        if _KEY_ART_SCALED is None or _KEY_ART_SCALED.get_size() != (VIRTUAL_WIDTH, VIRTUAL_HEIGHT):
            _KEY_ART_SCALED = pygame.transform.smoothscale(_KEY_ART, (VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        surface.blit(_KEY_ART_SCALED, (0, 0))
        shade = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        shade.fill((4, 7, 13, 112))
        surface.blit(shade, (0, 0))
        pygame.draw.rect(surface, (8, 11, 18, 208), (54, 48, 470, 624), border_radius=18)
        pygame.draw.line(surface, COLORS["cyan"], (54, 48), (54, 672), 3)
        pygame.draw.line(surface, COLORS["red"], (54, 672), (524, 672), 3)
        return
    surface.fill((5, 7, 12))
    for y in range(0, VIRTUAL_HEIGHT, 4):
        blend = y / VIRTUAL_HEIGHT
        pygame.draw.line(
            surface,
            (int(8 + 24 * blend), int(12 + 24 * blend), int(18 + 28 * blend)),
            (0, y),
            (VIRTUAL_WIDTH, y),
        )
    for index, x in enumerate((120, 360, 700, 1040)):
        points = [
            (x - 180, 610),
            (x - 100, 420 + index * 12),
            (x - 20, 500),
            (x + 60, 360),
            (x + 180, 610),
        ]
        pygame.draw.polygon(surface, (16, 18, 24), points)
        pygame.draw.polygon(surface, (72, 38, 34), points, 2)
    pygame.draw.rect(surface, (12, 14, 18), (0, 520, VIRTUAL_WIDTH, 200))
    pygame.draw.rect(surface, (24, 30, 38), (66, 56, 1148, 622), border_radius=22)
    pygame.draw.rect(surface, COLORS["red"], (66, 56, 1148, 622), 3, border_radius=22)


def draw_arena_preview(
    surface: pygame.Surface,
    arena: ArenaDefinition,
    rect: pygame.Rect,
    t: float = 0.0,
) -> None:
    pygame.draw.rect(surface, arena.palette[0], rect, border_radius=12)
    pygame.draw.rect(surface, (20, 24, 30), rect.inflate(-8, -8), border_radius=8)
    if arena.key == "storm_pier":
        pygame.draw.circle(surface, arena.palette[2], (rect.centerx + 180, rect.y + 118), 58)
        for x in range(rect.x + 50, rect.right - 40, 92):
            wave = int(8 + 6 * math.sin(t + x * 0.02))
            pygame.draw.arc(surface, arena.palette[1], (x, rect.bottom - 122 + wave, 82, 36), 0, math.pi, 3)
    elif arena.key == "dragon_mountains":
        points = [(rect.x + 70, rect.bottom - 62), (rect.centerx, rect.y + 94), (rect.right - 70, rect.bottom - 62)]
        pygame.draw.polygon(surface, (30, 54, 44), points)
        pygame.draw.polygon(surface, arena.palette[1], points, 3)
    else:
        for index, x in enumerate(range(rect.x + 90, rect.right - 90, 128)):
            height = 70 + index % 3 * 28
            pygame.draw.rect(surface, arena.palette[1], (x, rect.bottom - 80 - height, 64, height), border_radius=6)
            pygame.draw.line(surface, arena.palette[2], (x, rect.bottom - 80), (x + 64, rect.bottom - 80), 3)


def build_pause_menu_items(language: str = "ru") -> list[MenuItem]:
    if language != "ru":
        labels = (("Resume", "resume"), ("Settings", "settings"), ("Restart", "restart"), ("Main menu", "menu"), ("Quit", "quit_game"))
    else:
        labels = (("Продолжить", "resume"), ("Настройки", "settings"), ("Рестарт", "restart"), ("Главное меню", "menu"), ("Выйти", "quit_game"))
    return [MenuItem(label, action) for label, action in labels]

