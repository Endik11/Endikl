from __future__ import annotations

import pygame

from ..definitions import ArenaVisualDefinition
from .arena_layer import ArenaLayer
from .visual_constants import GROUND_Y, VIRTUAL_WIDTH


class ArenaRenderer:
    def __init__(self) -> None:
        self._cache: dict[str, list[ArenaLayer]] = {}

    @staticmethod
    def ground_screen_y(camera) -> int:
        return camera.world_to_screen(0, GROUND_Y)[1]

    def draw(self, surface: pygame.Surface, visual: ArenaVisualDefinition, camera, t: float = 0.0) -> None:
        layers = self._cache.setdefault(visual.id, [ArenaLayer(layer, visual.palette) for layer in visual.layers])
        for layer, raw in zip(layers, visual.layers):
            parallax = float(raw.get("parallax", 0.5))
            offset = int((camera.x - VIRTUAL_WIDTH / 2) * parallax) % VIRTUAL_WIDTH
            surf = layer.surface()
            surface.blit(surf, (-offset, 0))
            if offset:
                surface.blit(surf, (VIRTUAL_WIDTH - offset, 0))
        # The fighters use the camera's world-to-screen transform. Keeping
        # the floor at a hard-coded screen y makes them float as the camera
        # follows the pair vertically.
        ground_screen_y = self.ground_screen_y(camera)
        pygame.draw.rect(surface, visual.palette[0], (0, ground_screen_y, VIRTUAL_WIDTH, max(0, 720 - ground_screen_y)))
        horizon = ground_screen_y + 2
        floor = visual.palette[0]
        floor_color = tuple(max(0, min(255, channel + 8)) for channel in floor)
        pygame.draw.polygon(surface, floor_color, ((0, horizon), (VIRTUAL_WIDTH, horizon), (VIRTUAL_WIDTH, 720), (0, 720)))
        grid_color = tuple(max(0, min(255, channel)) for channel in visual.palette[1])
        for index in range(1, 7):
            depth = index / 7
            y = horizon + int((depth ** 1.65) * (720 - horizon))
            pygame.draw.line(surface, grid_color, (0, y), (VIRTUAL_WIDTH, y), 1 if index < 5 else 2)
        vanishing = (VIRTUAL_WIDTH // 2, horizon)
        for x in range(-640, VIRTUAL_WIDTH + 641, 160):
            pygame.draw.line(surface, visual.palette[2], vanishing, (x, 720), 1)
        pygame.draw.line(surface, visual.palette[2], (0, horizon), (VIRTUAL_WIDTH, horizon), 4)
