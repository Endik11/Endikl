from __future__ import annotations

from dataclasses import dataclass

from .animation_player import AnimationPlayer


@dataclass(slots=True)
class FighterVisualState:
    fighter_id: str
    player: AnimationPlayer
    last_health: int = 0
    last_meter: int = 0
