from __future__ import annotations

from .collision import AttackData, BoxSpec
from .definitions import ArenaDefinition, AttackDefinition, ComboDefinition, FighterDefinition


# Content frames document timing at 100 Hz so every pre-JSON decimal timing is
# represented exactly. This is a data conversion only; combat remains variable-dt.
CONTENT_FRAMES_PER_SECOND = 60.0


def build_combat_frame_data(definition: AttackDefinition):
    from .combat.frame_data import FrameData
    return FrameData(
        definition.startup_frames,definition.active_frames,definition.recovery_frames,
        definition.hit_stun_frames,definition.block_stun_frames,
        definition.cancel_start_frame,definition.cancel_end_frame,
        definition.hit_stop_frames,definition.block_stop_frames,
        definition.movement_x_per_frame,definition.movement_y_per_frame,
        definition.can_turn,definition.can_hit_once,definition.multi_hit_interval_frames,
        definition.hitboxes_by_frame,definition.hurtbox_overrides_by_frame,
        definition.armor_frames,definition.invulnerability_frames,
        definition.projectile_definition,definition.properties,
    )


def build_legacy_attack(definition: AttackDefinition, display_name: str) -> AttackData:
    properties = definition.properties
    return AttackData(
        name=display_name,
        startup=definition.startup_frames / CONTENT_FRAMES_PER_SECOND,
        active=definition.active_frames / CONTENT_FRAMES_PER_SECOND,
        recovery=definition.recovery_frames / CONTENT_FRAMES_PER_SECOND,
        damage=definition.damage,
        chip_damage=definition.chip_damage,
        hit_stun=definition.hit_stun_frames / CONTENT_FRAMES_PER_SECOND,
        block_stun=definition.block_stun_frames / CONTENT_FRAMES_PER_SECOND,
        knockback_x=definition.knockback_x,
        knockback_y=definition.knockback_y,
        hitbox=BoxSpec(*definition.hitbox),
        energy_gain=definition.energy_gain,
        energy_cost=definition.energy_cost,
        cancellable=bool(definition.cancel_on_hit or "special" in properties),
        launcher="launcher" in properties,
        finisher="final_strike" if "super" in properties else None,
    )


def build_legacy_fighter(definition: FighterDefinition) -> FighterDefinition:
    """The expanded immutable definition exposes all legacy properties itself."""
    return definition


def build_legacy_combo(definition: ComboDefinition, attack: AttackData, display_name: str):
    from .combos import ComboMove
    return ComboMove(
        name=display_name,
        sequence=definition.inputs,
        attack=attack,
        max_age=definition.max_gap_frames / CONTENT_FRAMES_PER_SECOND,
    )


def build_legacy_arena(definition: ArenaDefinition) -> ArenaDefinition:
    return definition
