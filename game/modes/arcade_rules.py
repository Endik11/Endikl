from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ArcadeRules:
    minimum_matches: int = 4
    starting_continues: int = 2
    difficulty_order: tuple[str, ...] = ("novice", "easy", "medium", "hard", "expert")
