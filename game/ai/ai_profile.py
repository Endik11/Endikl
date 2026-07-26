from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIProfile:
    id: str
    aggression: float = 0.5
    preferred_distance: float = 180.0
    reaction_frames: int = 8
    decision_interval_frames: int = 6
    execution_error_probability: float = 0.05
    block_probability: float = 0.55
    low_block_probability: float = 0.35
    throw_probability: float = 0.1
    throw_tech_probability: float = 0.3
    jump_probability: float = 0.08
    projectile_probability: float = 0.12
    anti_air_probability: float = 0.55
    punish_probability: float = 0.5
    combo_depth: int = 2
    meter_usage: float = 0.45
    corner_escape_probability: float = 0.55
    wake_up_behavior: str = "block"
    preferred_commands: tuple[str, ...] = ()
    forbidden_commands: tuple[str, ...] = ()
    adaptation_rate: float = 0.25

    @classmethod
    def from_dict(cls, profile_id: str, row: dict) -> "AIProfile":
        fields = cls.__dataclass_fields__
        values = {key: value for key, value in row.items() if key in fields and key != "id"}
        for key in ("preferred_commands", "forbidden_commands"):
            if key in values:
                values[key] = tuple(str(item) for item in values[key])
        return cls(profile_id, **values)
