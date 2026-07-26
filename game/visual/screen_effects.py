from __future__ import annotations

import pygame


class ScreenEffects:
    def __init__(self) -> None:
        self.flash_alpha = 0

    def flash(self, amount: int, settings=None) -> None:
        video = getattr(settings, "video", settings)
        if not getattr(video, "flashes", True) or getattr(video, "reduced_flashes", False):
            return
        self.flash_alpha = min(140, max(self.flash_alpha, amount))

    def draw(self, surface: pygame.Surface) -> None:
        if self.flash_alpha <= 0:
            return
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 255, 255, self.flash_alpha))
        surface.blit(overlay, (0, 0))
        self.flash_alpha = max(0, self.flash_alpha - 12)
