from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AiDifficultyDefinition:
    id: str
    reaction_modifier: int
    decision_modifier: int
    error_modifier: float
    combo_depth: int
    defense_modifier: float
    punish_modifier: float
    adaptation_modifier: float


AI_DIFFICULTIES = {
    "novice": AiDifficultyDefinition("novice", 12, 8, 0.22, 1, 0.55, 0.35, 0.25),
    "easy": AiDifficultyDefinition("easy", 7, 5, 0.14, 2, 0.72, 0.52, 0.45),
    "medium": AiDifficultyDefinition("medium", 3, 2, 0.07, 3, 0.88, 0.72, 0.70),
    "hard": AiDifficultyDefinition("hard", 1, 0, 0.025, 4, 1.0, 0.90, 0.90),
    "expert": AiDifficultyDefinition("expert", 0, -1, 0.008, 5, 1.08, 1.0, 1.0),
}
