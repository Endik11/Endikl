import pytest

from game.content_registry import get_default_registry
from game.definition_adapters import (
    build_legacy_arena,
    build_legacy_attack,
    build_legacy_combo,
    build_legacy_fighter,
    build_combat_frame_data,
)


def test_fighter_and_arena_compatibility() -> None:
    registry = get_default_registry()
    fighter = build_legacy_fighter(registry.get_fighter("ren_kaido"))
    arena = build_legacy_arena(registry.get_arena("neon_foundry"))
    assert fighter.key == "ren_kaido" and fighter.speed == fighter.walk_speed
    assert arena.key == "neon_foundry" and arena.name == "Нефритовая кузня"


def test_attack_preserves_timing_damage_and_energy() -> None:
    registry = get_default_registry()
    definition = registry.get_attack("bronze_sky_break")
    attack = build_legacy_attack(definition, registry.localization.get(definition.display_name_key))
    assert attack.startup == 0.20
    assert attack.active == pytest.approx(0.18, abs=1 / 60)
    assert attack.recovery == 0.45
    assert attack.damage == 180 and attack.energy_cost == 300


def test_combo_adapter_preserves_sequence_and_window() -> None:
    registry = get_default_registry()
    definition = registry.get_combo("storm_limit_verdict_combo")
    attack_definition = registry.get_attack(definition.resulting_attack_id)
    attack = build_legacy_attack(attack_definition, registry.localization.get(attack_definition.display_name_key))
    combo = build_legacy_combo(definition, attack, registry.localization.get(definition.display_name_key))
    assert combo.sequence == ("energy", "heavy_punch", "heavy_kick")
    assert combo.max_age == 0.5
    assert combo.attack.damage == 310


def test_combat_frame_adapter_preserves_every_extended_field() -> None:
    definition=get_default_registry().get_attack("light_punch");frame=build_combat_frame_data(definition)
    assert frame.cancel_start_frame==definition.cancel_start_frame and frame.cancel_end_frame==definition.cancel_end_frame
    assert frame.hit_stop_frames==definition.hit_stop_frames and frame.block_stop_frames==definition.block_stop_frames
    assert frame.movement_x_per_frame==definition.movement_x_per_frame and frame.movement_y_per_frame==definition.movement_y_per_frame
    assert frame.can_turn==definition.can_turn and frame.can_hit_once==definition.can_hit_once
    assert frame.hitboxes_by_frame==definition.hitboxes_by_frame and frame.hurtbox_overrides_by_frame==definition.hurtbox_overrides_by_frame
    assert frame.armor_frames==definition.armor_frames and frame.invulnerability_frames==definition.invulnerability_frames
    assert frame.projectile_definition==definition.projectile_definition and frame.multi_hit_interval_frames==definition.multi_hit_interval_frames and frame.properties==definition.properties
