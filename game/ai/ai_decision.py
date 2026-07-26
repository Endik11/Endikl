from .ai_action import AIAction


def decide(view, profile, difficulty, rng, memory) -> AIAction:
    if view.own_state in {"WAKE_UP", "KNOCKDOWN"}:
        return AIAction("wake_up_attack", ("light_punch",), 1) if profile.wake_up_behavior == "attack" else AIAction("wake_up_block", ("block",), 3)
    if view.opponent_state == "THROW_STARTUP" and rng.chance(profile.throw_tech_probability * difficulty.defense_modifier):
        return AIAction("throw_tech", ("throw",), 1)
    if view.opponent_state == "ATTACK_RECOVERY" and view.distance < 190 and rng.chance(profile.punish_probability * difficulty.punish_modifier):
        return AIAction("punish", ("heavy_punch",), 1)
    if view.in_corner and rng.chance(profile.corner_escape_probability):
        return AIAction("corner_escape", ("up",), 2)
    if view.projectile_incoming:
        return AIAction("projectile_block", ("block",), 3) if rng.chance(0.7 * difficulty.defense_modifier) else AIAction("projectile_evade", ("up",), 2)
    if view.opponent_airborne and view.distance < 240 and rng.chance(profile.anti_air_probability):
        return AIAction("anti_air", ("heavy_punch",), 1)
    if view.opponent_attacking and view.distance < 190 and rng.chance(profile.block_probability * difficulty.defense_modifier):
        low = rng.chance(profile.low_block_probability)
        return AIAction("block_low" if low else "block_high", ("block", "down") if low else ("block",), 3)
    if view.distance > profile.preferred_distance + 80:
        if rng.chance(profile.projectile_probability):
            return AIAction("projectile", ("special", "light_punch"), 1)
        return AIAction("approach", ("forward",), 3)
    if view.distance < max(70, profile.preferred_distance - 90):
        if rng.chance(profile.throw_probability):
            return AIAction("throw", ("throw",), 1)
        return AIAction("retreat", ("back",), 2)
    if view.own_meter >= 1000 and rng.chance(profile.meter_usage * 0.45):
        return AIAction("super", ("special", "heavy_punch", "heavy_kick"), 1)
    if view.own_meter >= 180 and rng.chance(profile.meter_usage):
        return AIAction("meter_special", ("special", "light_punch"), 1)
    if rng.chance(profile.jump_probability):
        return AIAction("jump", ("up",), 2)
    if rng.chance(profile.aggression):
        command = rng.choose(profile.preferred_commands or ("light_punch", "light_kick", "heavy_punch"))
        return AIAction("combo" if difficulty.combo_depth > 2 else "poke", (command,), 1)
    if memory.frequency("attack") > 0.45 * difficulty.adaptation_modifier:
        return AIAction("bait", ("back",), 2)
    return AIAction("idle" if rng.chance(0.2) else "maintain_distance", (), 2)
