from __future__ import annotations

import pygame

from ..definitions import ArenaVisualDefinition
from .arena_layer import ArenaLayer
from .visual_constants import GROUND_Y, VIRTUAL_WIDTH


class ArenaRenderer:
    def __init__(self) -> None:
        self._cache: dict[str, list[ArenaLayer]] = {}

    def draw(self, surface: pygame.Surface, visual: ArenaVisualDefinition, camera, t: float = 0.0) -> None:
        layers = self._cache.setdefault(visual.id, [ArenaLayer(layer, visual.palette) for layer in visual.layers])
        for layer, raw in zip(layers, visual.layers):
            parallax = float(raw.get("parallax", 0.5))
            offset = int((camera.x - VIRTUAL_WIDTH / 2) * parallax) % VIRTUAL_WIDTH
            surf = layer.surface()
            surface.blit(surf, (-offset, 0))
            if offset:
                surface.blit(surf, (VIRTUAL_WIDTH - offset, 0))
        pygame.draw.rect(surface, visual.palette[0], (0, GROUND_Y, VIRTUAL_WIDTH, 136))
        pygame.draw.line(surface, visual.palette[2], (0, GROUND_Y), (VIRTUAL_WIDTH, GROUND_Y), 4)
