from __future__ import annotations

import math
import random
from dataclasses import dataclass

import pygame

from .settings import COLORS, VIRTUAL_HEIGHT, VIRTUAL_WIDTH


@dataclass
class Particle:
    pos: pygame.Vector2
    vel: pygame.Vector2
    radius: float
    color: tuple[int, int, int]
    lifetime: float
    max_lifetime: float
    gravity: float = 0.0

    def update(self, dt: float) -> bool:
        self.lifetime -= dt
        self.vel.y += self.gravity * dt
        self.pos += self.vel * dt
        return self.lifetime > 0

    def draw(self, surface: pygame.Surface, offset: pygame.Vector2) -> None:
        alpha = max(0, min(255, int(255 * (self.lifetime / self.max_lifetime))))
        size = max(1, int(self.radius * (0.45 + self.lifetime / self.max_lifetime)))
        particle_surface = pygame.Surface((size * 2 + 2, size * 2 + 2), pygame.SRCALPHA)
        color = (*self.color, alpha)
        pygame.draw.circle(particle_surface, color, (size + 1, size + 1), size)
        surface.blit(particle_surface, self.pos - offset - pygame.Vector2(size, size))


class ParticleSystem:
    def __init__(self) -> None:
        self.particles: list[Particle] = []

    def update(self, dt: float) -> None:
        self.particles = [p for p in self.particles if p.update(dt)]

    def draw(self, surface: pygame.Surface, offset: pygame.Vector2) -> None:
        for particle in self.particles:
            particle.draw(surface, offset)

    def burst(
        self,
        position: pygame.Vector2,
        color: tuple[int, int, int] = COLORS["gold"],
        count: int = 18,
        power: float = 440.0,
    ) -> None:
        for _ in range(count):
            angle = random.uniform(-math.pi, math.pi)
            speed = random.uniform(power * 0.2, power)
            vel = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            self.particles.append(
                Particle(
                    pos=pygame.Vector2(position),
                    vel=vel,
                    radius=random.uniform(3.0, 8.0),
                    color=color,
                    lifetime=random.uniform(0.18, 0.55),
                    max_lifetime=0.55,
                    gravity=980.0,
                )
            )

    def dust(self, position: pygame.Vector2, direction: int, count: int = 7) -> None:
        for _ in range(count):
            self.particles.append(
                Particle(
                    pos=pygame.Vector2(position),
                    vel=pygame.Vector2(
                        random.uniform(70, 220) * -direction,
                        random.uniform(-90, -15),
                    ),
                    radius=random.uniform(4.0, 9.0),
                    color=(130, 125, 112),
                    lifetime=random.uniform(0.2, 0.45),
                    max_lifetime=0.45,
                    gravity=300.0,
                )
            )

    def ambient(self, dt: float) -> None:
        if random.random() > dt * 8.0:
            return
        self.particles.append(
            Particle(
                pos=pygame.Vector2(
                    random.uniform(0, VIRTUAL_WIDTH),
                    random.uniform(80, VIRTUAL_HEIGHT - 160),
                ),
                vel=pygame.Vector2(random.uniform(-12, 12), random.uniform(-18, -4)),
                radius=random.uniform(1.5, 3.5),
                color=(95, 130, 150),
                lifetime=random.uniform(1.2, 2.6),
                max_lifetime=2.6,
            )
        )

