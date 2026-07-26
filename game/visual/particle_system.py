from __future__ import annotations

import math

import pygame

from .particle import Particle


class ParticleSystem:
    def __init__(self, pool_size: int = 512) -> None:
        self.pool = [Particle() for _ in range(pool_size)]

    def emit(self, x: float, y: float, definition) -> None:
        count = min(definition.particle_count, len(self.pool))
        emitted = 0
        for particle in self.pool:
            if particle.active:
                continue
            angle = (emitted / max(1, count)) * math.tau
            speed = definition.speed * (0.55 + (emitted % 5) * 0.12)
            color = definition.color if emitted % 2 == 0 else definition.secondary_color
            particle.reset(x, y, math.cos(angle) * speed, math.sin(angle) * speed, definition.lifetime_frames, definition.radius, color)
            emitted += 1
            if emitted >= count:
                break

    def update(self, *, reduced_motion: bool = False) -> None:
        if reduced_motion:
            for particle in self.pool:
                if particle.active:
                    particle.age += 1
                    particle.active = particle.age < max(1, particle.lifetime // 2)
            return
        for particle in self.pool:
            particle.update()

    def draw(self, surface: pygame.Surface, camera) -> None:
        for particle in self.pool:
            if not particle.active:
                continue
            amount = 1.0 - particle.age / max(1, particle.lifetime)
            radius = max(1, int(particle.radius * amount))
            pygame.draw.circle(surface, particle.color, camera.world_to_screen(particle.x, particle.y), radius)

    def active_count(self) -> int:
        return sum(1 for particle in self.pool if particle.active)
