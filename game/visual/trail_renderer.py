from __future__ import annotations

import pygame


class TrailRenderer:
    def __init__(self) -> None:
        self.points: list[tuple[int, int, tuple[int, int, int]]] = []

    def add(self, point: tuple[int, int], color: tuple[int, int, int]) -> None:
        self.points.append((point[0], point[1], color))
        self.points = self.points[-32:]

    def draw(self, surface: pygame.Surface, *, enabled: bool = True) -> None:
        if not enabled:
            return
        for index, (x, y, color) in enumerate(self.points):
            pygame.draw.circle(surface, color, (x, y), max(1, index // 5))
