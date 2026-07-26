from __future__ import annotations

from dataclasses import dataclass

import pygame

from .camera_controller import CameraController


@dataclass(slots=True)
class RenderContext:
    surface: pygame.Surface
    snapshot: object
    camera: CameraController
    alpha: float = 0.0
    world: object | None = None
    dt: float = 1 / 60
