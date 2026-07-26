from .ai_action import AIAction


def decide(view, profile, difficulty, rng, memory) -> AIAction:
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
    if rng.chance(profile.aggression):
        command = rng.choose(profile.preferred_commands or ("light_punch", "light_kick", "heavy_punch"))
        return AIAction("combo" if difficulty.combo_depth > 2 else "poke", (command,), 1)
    return AIAction("maintain_distance", (), 2)
