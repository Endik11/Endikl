from __future__ import annotations

import pygame

from .visual_constants import VIRTUAL_HEIGHT, VIRTUAL_WIDTH


class ArenaLayer:
    def __init__(self, layer: dict[str, object], palette: tuple[tuple[int, int, int], ...]) -> None:
        self.layer = layer
        self.palette = palette
        self._surface: pygame.Surface | None = None

    def surface(self) -> pygame.Surface:
        if self._surface is None:
            surf = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
            kind = str(self.layer.get("kind", "mid"))
            density = int(self.layer.get("density", 6))
            base = self.palette[0]
            accent = self.palette[1 if kind != "front" else 2]
            if kind == "sky":
                surf.fill((*base, 255))
                for i in range(density):
                    y = 60 + i * 38
                    pygame.draw.line(surf, (*accent, 55), (0, y), (VIRTUAL_WIDTH, y + 80), 3)
            elif kind == "front":
                for i in range(density):
                    x = (i * 117) % VIRTUAL_WIDTH
                    pygame.draw.rect(surf, (*accent, 120), (x, 532 - (i % 4) * 12, 58, 70), border_radius=3)
            else:
                for i in range(density):
                    x = 40 + i * 150
                    h = 140 + (i % 3) * 40
                    pygame.draw.rect(surf, (*accent, 85), (x, 420 - h, 90, h), border_radius=4)
            self._surface = surf
        return self._surface
