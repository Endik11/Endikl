from __future__ import annotations

import pygame


class ShadowRenderer:
    def draw(self, surface: pygame.Surface, x: int, y: int, width: int, color=(0, 0, 0)) -> None:
        rect = pygame.Rect(0, 0, width, max(10, width // 5))
        rect.center = (x, y + 4)
        pygame.draw.ellipse(surface, (*color, 95), rect)
