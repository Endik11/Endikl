from __future__ import annotations

import random

from .arcade_rules import ArcadeRules


def build_arcade_ladder(fighter_id: str, available: list[str], seed: int, rules: ArcadeRules = ArcadeRules()) -> tuple[str, ...]:
    candidates = sorted({item for item in available if item != fighter_id})
    if len(candidates) < 2:
        raise ValueError("Arcade requires at least two valid opponents")
    rng = random.Random(seed)
    rng.shuffle(candidates)
    count = max(rules.minimum_matches, len(candidates))
    ladder = [candidates[index % len(candidates)] for index in range(count)]
    for index in range(1, len(ladder)):
        if ladder[index] == ladder[index - 1]:
            ladder[index] = candidates[(candidates.index(ladder[index]) + 1) % len(candidates)]
    return tuple(ladder)


def validate_ladder(ladder, fighter_id: str, available: set[str], rules: ArcadeRules = ArcadeRules()) -> bool:
    return isinstance(ladder, (list, tuple)) and len(ladder) >= rules.minimum_matches and all(item in available and item != fighter_id for item in ladder) and all(a != b for a, b in zip(ladder, ladder[1:]))
