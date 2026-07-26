from __future__ import annotations


EVENT_EFFECTS = {
    "ATTACK_HIT": "light_hit_spark",
    "ATTACK_BLOCKED": "block_spark",
    "PROJECTILE_HIT": "projectile_impact",
    "PROJECTILE_BLOCKED": "projectile_block",
    "PROJECTILE_CLASH": "projectile_clash",
    "THROW_CONNECTED": "throw_impact",
    "THROW_DAMAGE_APPLIED": "throw_impact",
    "ARMOR_ABSORBED": "armor_spark",
    "ROUND_ENDED": "ko_bloom",
}
