from __future__ import annotations

from dataclasses import dataclass

import pygame


@dataclass(frozen=True)
class BoxSpec:
    x: int
    y: int
    w: int
    h: int

    def to_rect(self, origin: pygame.Vector2, facing: int) -> pygame.Rect:
        if facing >= 0:
            left = int(origin.x + self.x)
        else:
            left = int(origin.x - self.x - self.w)
        top = int(origin.y + self.y)
        return pygame.Rect(left, top, self.w, self.h)


@dataclass(frozen=True)
class AttackData:
    name: str
    startup: float
    active: float
    recovery: float
    damage: int
    chip_damage: int
    hit_stun: float
    block_stun: float
    knockback_x: float
    knockback_y: float
    hitbox: BoxSpec
    energy_gain: int = 70
    energy_cost: int = 0
    cancellable: bool = False
    launcher: bool = False
    finisher: str | None = None

    @property
    def total_time(self) -> float:
        return self.startup + self.active + self.recovery


def resolve_body_overlap(left: pygame.Rect, right: pygame.Rect) -> tuple[int, int]:
    """Returns small x offsets to separate overlapping fighter bodies."""
    if not left.colliderect(right):
        return 0, 0

    overlap = min(left.right - right.left, right.right - left.left)
    if overlap <= 0:
        return 0, 0
    push = overlap // 2 + 1
    if left.centerx <= right.centerx:
        return -push, push
    return push, -push


def is_attack_active(attack: AttackData | None, timer: float) -> bool:
    if attack is None:
        return False
    return attack.startup <= timer <= attack.startup + attack.active


def mirror_rect(rect: pygame.Rect, surface_width: int) -> pygame.Rect:
    return pygame.Rect(surface_width - rect.right, rect.top, rect.width, rect.height)

