from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True, frozen=True)
class AttackDefinition:
    id: str
    owner_id: str
    display_name_key: str
    animation: str
    startup_frames: int
    active_frames: int
    recovery_frames: int
    damage: int
    chip_damage: int
    hit_stun_frames: int
    block_stun_frames: int
    hit_level: str
    knockback_x: float
    knockback_y: float
    energy_gain: int
    energy_cost: int
    cancel_on_hit: tuple[str, ...]
    cancel_on_block: tuple[str, ...]
    properties: frozenset[str]
    legacy_action_name: str
    hitbox: tuple[int, int, int, int]
    cancel_start_frame: int = 0
    cancel_end_frame: int = 0
    hit_stop_frames: int = 3
    block_stop_frames: int = 2
    movement_x_per_frame: float = 0
    movement_y_per_frame: float = 0
    can_turn: bool = False
    can_hit_once: bool = True
    hitboxes_by_frame: tuple[tuple[int, tuple[dict, ...]], ...] = ()
    hurtbox_overrides_by_frame: tuple[tuple[int, tuple[dict, ...]], ...] = ()
    armor_frames: tuple[int, ...] = ()
    invulnerability_frames: tuple[tuple[int, frozenset[str]], ...] = ()
    projectile_definition: dict | None = None
    multi_hit_interval_frames: int = 1
