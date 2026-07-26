from __future__ import annotations

import pygame

from .visual_constants import DEFAULT_METER_SEGMENTS


class HudRenderer:
    def __init__(self, registry) -> None:
        self.registry = registry
        self._fonts: dict[tuple[str, int, bool], pygame.font.Font] = {}
        self._display_health: dict[str, float] = {}

    def font(self, size: int, bold: bool = False) -> pygame.font.Font:
        hud = self.registry.hud
        family = hud.font_family if hud else "Segoe UI"
        key = (family, size, bold)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.SysFont(family, size, bold=bold)
        return self._fonts[key]

    def health_view(self, fighter_id: str, actual: int) -> float:
        current = self._display_health.get(fighter_id, float(actual))
        current += (actual - current) * 0.18
        self._display_health[fighter_id] = current
        return current

    def meter_segments(self, value: int) -> tuple[float, ...]:
        hud = self.registry.hud
        segments = hud.meter_segments if hud else DEFAULT_METER_SEGMENTS
        maximum = hud.meter_max if hud else 3000
        per = maximum / max(1, segments)
        return tuple(max(0.0, min(1.0, (value - i * per) / per)) for i in range(segments))

    def draw(self, surface: pygame.Surface, snapshot, settings=None) -> None:
        hud = self.registry.hud
        palette = hud.palette if hud else {}
        scale = getattr(getattr(settings, "video", settings), "ui_scale", 1.0)
        width = int((hud.health_width if hud else 360) * scale)
        self._draw_side(surface, snapshot.fighter_one, 70, 34, width, palette, flip=False)
        self._draw_side(surface, snapshot.fighter_two, 1280 - 70 - width, 34, width, palette, flip=True)
        timer = max(0, snapshot.round_timer_frames // 60)
        text = self.font(38, True).render(str(timer), True, palette.get("text", (238, 241, 244)))
        surface.blit(text, text.get_rect(center=(640, 54)))

    def _draw_side(self, surface, snap, x: int, y: int, width: int, palette, *, flip: bool) -> None:
        definition = self.registry.get_fighter(snap.fighter_id)
        max_health = definition.max_health
        smooth = self.health_view(snap.fighter_id, snap.health)
        health_w = int(width * max(0, min(max_health, smooth)) / max_health)
        pygame.draw.rect(surface, palette.get("panel", (26, 30, 36)), (x, y, width, 24), border_radius=4)
        bar_x = x + width - health_w if flip else x
        pygame.draw.rect(surface, palette.get("health", (207, 53, 63)), (bar_x, y, health_w, 24), border_radius=4)
        name = self.font(18, True).render(definition.name, True, palette.get("text", (238, 241, 244)))
        surface.blit(name, (x if not flip else x + width - name.get_width(), y + 28))
        segment_w = width // 3 - 4
        for index, filled in enumerate(self.meter_segments(snap.meter)):
            sx = x + index * (segment_w + 6)
            pygame.draw.rect(surface, palette.get("panel", (26, 30, 36)), (sx, y + 54, segment_w, 10), border_radius=2)
            pygame.draw.rect(surface, palette.get("meter", (63, 201, 197)), (sx, y + 54, int(segment_w * filled), 10), border_radius=2)
