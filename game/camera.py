from __future__ import annotations

import random

import pygame

from .settings import VIRTUAL_WIDTH, clamp


class Camera:
    def __init__(self) -> None:
        self.offset = pygame.Vector2()
        self.shake_time = 0.0
        self.shake_strength = 0.0

    def update(self, dt: float, focus_x: float) -> None:
        target_x = clamp(focus_x - VIRTUAL_WIDTH / 2, -90, 90)
        self.offset.x += (target_x - self.offset.x) * min(1.0, dt * 5.0)
        self.offset.y += (0 - self.offset.y) * min(1.0, dt * 5.0)

        if self.shake_time > 0:
            self.shake_time -= dt
            falloff = max(0.0, self.shake_time / 0.25)
            self.offset.x += random.uniform(-1, 1) * self.shake_strength * falloff
            self.offset.y += random.uniform(-1, 1) * self.shake_strength * falloff

    def shake(self, strength: float = 12.0, duration: float = 0.25) -> None:
        self.shake_strength = max(self.shake_strength, strength)
        self.shake_time = max(self.shake_time, duration)

