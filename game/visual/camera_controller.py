from __future__ import annotations

import math
from dataclasses import dataclass

from .visual_constants import MAX_CAMERA_ZOOM, MAX_SHAKE_PIXELS, MIN_CAMERA_ZOOM, VIRTUAL_HEIGHT, VIRTUAL_WIDTH


@dataclass(slots=True)
class CameraController:
    x: float = VIRTUAL_WIDTH / 2
    y: float = VIRTUAL_HEIGHT / 2
    zoom: float = 1.0
    shake: float = 0.0
    _phase: float = 0.0

    def update(self, snapshot, bounds: tuple[float, float], dt: float, settings=None) -> None:
        left, right = bounds
        f1 = snapshot.fighter_one
        f2 = snapshot.fighter_two
        target_x = (f1.x + f2.x) * 0.5
        target_y = min(VIRTUAL_HEIGHT / 2 + 42, (f1.y + f2.y) * 0.5 - 90)
        distance = abs(f1.x - f2.x)
        dynamic_zoom = getattr(getattr(settings, "video", settings), "dynamic_zoom", True)
        reduced = getattr(getattr(settings, "video", settings), "reduced_motion", False)
        target_zoom = 1.0 if not dynamic_zoom else max(MIN_CAMERA_ZOOM, min(MAX_CAMERA_ZOOM, 1.12 - distance / 2200))
        if reduced:
            target_zoom = 1.0 + (target_zoom - 1.0) * 0.25
        smoothing = 0.08 if not reduced else 0.04
        self.x += (target_x - self.x) * smoothing
        self.y += (target_y - self.y) * smoothing
        self.zoom += (target_zoom - self.zoom) * smoothing
        half_width = (VIRTUAL_WIDTH / self.zoom) * 0.5
        self.x = max(left + half_width, min(right - half_width, self.x))
        self._phase += dt * 21.0
        self.shake = max(0.0, self.shake - dt * (18.0 if not reduced else 32.0))

    def emphasize(self, strength: float, settings=None) -> None:
        enabled = getattr(getattr(settings, "video", settings), "camera_shake", True)
        reduced = getattr(getattr(settings, "video", settings), "reduced_motion", False)
        if not enabled:
            return
        amount = strength * (0.35 if reduced else 1.0)
        self.shake = min(MAX_SHAKE_PIXELS, max(self.shake, amount))

    def offset(self) -> tuple[float, float]:
        return math.sin(self._phase) * self.shake, math.cos(self._phase * 1.37) * self.shake * 0.55

    def world_to_screen(self, x: float, y: float) -> tuple[int, int]:
        shake_x, shake_y = self.offset()
        screen_x = (x - self.x) * self.zoom + VIRTUAL_WIDTH / 2 + shake_x
        screen_y = (y - self.y) * self.zoom + VIRTUAL_HEIGHT / 2 + shake_y
        return int(screen_x), int(screen_y)
