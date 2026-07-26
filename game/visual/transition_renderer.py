from __future__ import annotations

import pygame


class TransitionRenderer:
    def draw(self, surface: pygame.Surface, amount: float) -> None:
        alpha = int(max(0.0, min(1.0, amount)) * 180)
        if alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))
