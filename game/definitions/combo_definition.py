from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class ComboDefinition:
    id: str
    owner_id: str
    display_name_key: str
    inputs: tuple[str, ...]
    max_gap_frames: int
    required_state: str
    resulting_attack_id: str
    meter_cost: int
    enabled: bool
    priority: int = 0
