from dataclasses import dataclass

from .combat_event import CombatEvent
from .enums import AttackLevel, DamageSourceType, HitResult


@dataclass(slots=True, frozen=True)
class DamageRequest:
    source_id: str
    target_id: str
    attack_id: str | None
    base_damage: int
    chip_damage: int
    hit_level: AttackLevel
    source_type: DamageSourceType
    properties: frozenset[str] = frozenset()
    hit_stun_frames: int = 0
    block_stun_frames: int = 0
    knockback_x: float = 0
    knockback_y: float = 0
    meter_gain_source: int = 0
    meter_gain_target: int = 0
    can_chip_kill: bool = False
    ignores_scaling: bool = False


@dataclass(slots=True, frozen=True)
class CombatResolution:
    result: HitResult
    health_damage: int = 0
    chip_damage: int = 0
    blocked: bool = False
    armor_absorbed: bool = False
    invulnerable: bool = False
    hit_stun_frames: int = 0
    block_stun_frames: int = 0
    applied_knockback: tuple[float, float] = (0, 0)
    meter_source: int = 0
    meter_target: int = 0
    events: tuple[CombatEvent, ...] = ()
