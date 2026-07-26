from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BoneTransform:
    id: str
    x: float
    y: float
    rotation: float
    scale: tuple[float, float]
    length: float
    thickness: float
    shape: str
    palette_role: str
    draw_order: int
    alpha: float = 1.0
