from __future__ import annotations

import pygame

from .settings import VIRTUAL_HEIGHT, VIRTUAL_WIDTH


class DisplayManager:
    VIRTUAL_SIZE = (VIRTUAL_WIDTH, VIRTUAL_HEIGHT)

    def __init__(self, settings) -> None:
        self.settings = settings
        self.screen: pygame.Surface | None = None
        self.virtual_surface = pygame.Surface(self.VIRTUAL_SIZE)
        self._physical_size = (settings.video.width, settings.video.height)
        self._viewport_rect = self.calculate_viewport(self._physical_size)

    @staticmethod
    def calculate_viewport(size: tuple[int, int]) -> pygame.Rect:
        width, height = max(1, int(size[0])), max(1, int(size[1]))
        scale = min(width / VIRTUAL_WIDTH, height / VIRTUAL_HEIGHT)
        viewport_width = max(1, round(VIRTUAL_WIDTH * scale))
        viewport_height = max(1, round(VIRTUAL_HEIGHT * scale))
        return pygame.Rect(
            (width - viewport_width) // 2,
            (height - viewport_height) // 2,
            viewport_width,
            viewport_height,
        )

    def create_display(self) -> pygame.Surface:
        flags = pygame.RESIZABLE
        if self.settings.video.fullscreen:
            flags = pygame.FULLSCREEN
        self.screen = pygame.display.set_mode(self._physical_size, flags)
        self._physical_size = self.screen.get_size()
        self._viewport_rect = self.calculate_viewport(self._physical_size)
        return self.screen

    def get_virtual_surface(self) -> pygame.Surface:
        return self.virtual_surface

    def present(self) -> None:
        if self.screen is None:
            raise RuntimeError("Display has not been created")
        self.screen.fill((0, 0, 0))
        if self._viewport_rect.size == self.VIRTUAL_SIZE:
            scaled = self.virtual_surface
        else:
            scaled = pygame.transform.smoothscale(
                self.virtual_surface,
                self._viewport_rect.size,
            )
        self.screen.blit(scaled, self._viewport_rect.topleft)
        pygame.display.flip()

    def handle_resize(self, size: tuple[int, int]) -> None:
        width, height = max(1, int(size[0])), max(1, int(size[1]))
        self._physical_size = (width, height)
        self.settings.video.width = width
        self.settings.video.height = height
        if self.screen is not None and not self.settings.video.fullscreen:
            self.screen = pygame.display.set_mode(self._physical_size, pygame.RESIZABLE)
            self._physical_size = self.screen.get_size()
        self._viewport_rect = self.calculate_viewport(self._physical_size)

    def apply_settings(self) -> pygame.Surface:
        self._physical_size = (
            self.settings.video.width,
            self.settings.video.height,
        )
        return self.create_display()

    def screen_to_virtual(
        self,
        position: tuple[int, int],
    ) -> tuple[int, int] | None:
        if not self._viewport_rect.collidepoint(position):
            return None
        local_x = position[0] - self._viewport_rect.x
        local_y = position[1] - self._viewport_rect.y
        return (
            min(VIRTUAL_WIDTH - 1, int(local_x * VIRTUAL_WIDTH / self._viewport_rect.width)),
            min(VIRTUAL_HEIGHT - 1, int(local_y * VIRTUAL_HEIGHT / self._viewport_rect.height)),
        )

    def virtual_to_screen(
        self,
        position: tuple[float, float],
    ) -> tuple[int, int]:
        return (
            self._viewport_rect.x
            + round(position[0] * self._viewport_rect.width / VIRTUAL_WIDTH),
            self._viewport_rect.y
            + round(position[1] * self._viewport_rect.height / VIRTUAL_HEIGHT),
        )

    @property
    def viewport_rect(self) -> pygame.Rect:
        return self._viewport_rect.copy()

    @property
    def physical_size(self) -> tuple[int, int]:
        return self._physical_size

