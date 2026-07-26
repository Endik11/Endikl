from __future__ import annotations

import pygame


class LightingRenderer:
    def __init__(self) -> None:
        self._overlay: pygame.Surface | None = None

    def draw(self, surface: pygame.Surface, color: tuple[int, int, int]) -> None:
        if self._overlay is None or self._overlay.get_size() != surface.get_size():
            self._overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        # The overlay alpha is intentional. Additive RGB blending ignored it
        # on opaque targets and washed the whole arena into a flat colour.
        self._overlay.fill((*color, 18))
        surface.blit(self._overlay, (0, 0))
