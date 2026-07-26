from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Particle:
    x: float = 0.0
    y: float = 0.0
    vx: float = 0.0
    vy: float = 0.0
    age: int = 0
    lifetime: int = 1
    radius: float = 2.0
    color: tuple[int, int, int] = (255, 255, 255)
    active: bool = False

    def reset(self, x: float, y: float, vx: float, vy: float, lifetime: int, radius: float, color: tuple[int, int, int]) -> None:
        self.x = x; self.y = y; self.vx = vx; self.vy = vy; self.age = 0; self.lifetime = max(1, lifetime); self.radius = radius; self.color = color; self.active = True

    def update(self) -> None:
        if not self.active:
            return
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.18
        self.age += 1
        self.active = self.age < self.lifetime
