from __future__ import annotations

from dataclasses import dataclass


ALLOWED_ANIMATION_EVENTS = {
    "footstep",
    "trail_start",
    "trail_stop",
    "cloth_impulse",
    "weapon_flash",
    "dust",
    "camera_emphasis",
    "ui_accent",
}


@dataclass(frozen=True, slots=True)
class VisualAnimationEvent:
    frame: int
    type: str
    payload: dict[str, object]

    def is_visual_only(self) -> bool:
        return self.type in ALLOWED_ANIMATION_EVENTS
