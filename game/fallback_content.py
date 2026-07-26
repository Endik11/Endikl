"""Minimal original emergency content; never used when data JSON is valid."""

FALLBACK_LOCALIZATION = {
    "arena.fallback.name": "Зал рассвета",
    "arena.fallback.description": "Безопасная процедурная тренировочная площадка.",
    "attack.fallback.straight": "Прямой удар",
    "attack.fallback.arc": "Дуговой удар",
    "combo.fallback.pulse": "Импульс рассвета",
}

FALLBACK_ATTACKS = [
    {"id": "fallback_straight", "owner_id": "common", "display_name_key": "attack.fallback.straight", "animation": "attack", "startup_frames": 4, "active_frames": 5, "recovery_frames": 8, "damage": 40, "chip_damage": 5, "hit_stun_frames": 11, "block_stun_frames": 7, "hit_level": "mid", "knockback_x": 150, "knockback_y": -20, "energy_gain": 40, "energy_cost": 0, "cancel_on_hit": [], "cancel_on_block": [], "properties": [], "legacy_action_name": "light_punch", "hitbox": [36, -162, 78, 43]},
    {"id": "fallback_arc", "owner_id": "common", "display_name_key": "attack.fallback.arc", "animation": "attack", "startup_frames": 8, "active_frames": 8, "recovery_frames": 16, "damage": 85, "chip_damage": 12, "hit_stun_frames": 18, "block_stun_frames": 11, "hit_level": "mid", "knockback_x": 300, "knockback_y": -80, "energy_gain": 65, "energy_cost": 0, "cancel_on_hit": [], "cancel_on_block": [], "properties": ["knockdown"], "legacy_action_name": "heavy_punch", "hitbox": [40, -174, 92, 58]},
]

def _fighter(content_id: str, name: str, palette: list[list[int]]) -> dict[str, object]:
    return {"id": content_id, "name": name, "title": "Страж рассвета", "biography": "Аварийный процедурный боец.", "archetype": "balanced", "max_health": 1000, "walk_speed": 470, "back_walk_speed": 420, "air_speed": 270, "jump_velocity": -920, "weight": 1.0, "defense": 1.0, "difficulty": 2, "palette": palette, "portrait": "", "sprite_sheet": "", "procedural_model": {"style": "guardian"}, "attack_ids": ["fallback_straight", "fallback_arc"], "combo_ids": ["fallback_pulse"], "special_ids": ["fallback_arc"], "super_attack_id": "fallback_arc", "victory_animation": "victory", "defeat_animation": "down", "ai_profile": {"aggression": 0.5, "reaction": 0.5}, "unlocked_by_default": True}

FALLBACK_FIGHTERS = [
    _fighter("aeris", "Аэрис Вейл", [[70, 150, 210], [230, 180, 80], [25, 30, 40]]),
    _fighter("toren", "Торен Мар", [[190, 75, 70], [90, 190, 120], [30, 28, 36]]),
]
FALLBACK_COMBOS = [{"id": "fallback_pulse", "owner_id": "common", "display_name_key": "combo.fallback.pulse", "inputs": ["down", "forward", "light_punch"], "max_gap_frames": 45, "required_state": "any", "resulting_attack_id": "fallback_arc", "meter_cost": 0, "enabled": True, "priority": 0}]
FALLBACK_ARENAS = [{"id": "dawn_hall", "name_key": "arena.fallback.name", "description_key": "arena.fallback.description", "preview": "", "background_layers": [], "ground_y": 584, "left_boundary": 70, "right_boundary": 1210, "music": "", "ambience": "", "hazards_enabled_by_default": False, "procedural_style": "foundry", "unlocked_by_default": True, "palette": [[16, 20, 24], [79, 150, 214], [232, 181, 82]], "hazard": "none"}]
