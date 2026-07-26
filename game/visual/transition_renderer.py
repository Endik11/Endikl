from __future__ import annotations

import pygame


class TransitionRenderer:
    def __init__(self):self._overlay=None
    def draw(self, surface: pygame.Surface, amount: float) -> None:
        alpha = int(max(0.0, min(1.0, amount)) * 180)
        if alpha <= 0:
            return
        if self._overlay is None or self._overlay.get_size()!=surface.get_size():self._overlay=pygame.Surface(surface.get_size(),pygame.SRCALPHA)
        self._overlay.fill((0, 0, 0, alpha));surface.blit(self._overlay, (0, 0))
