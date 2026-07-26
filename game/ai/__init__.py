from .ai_controller import AIController
from .ai_difficulty import AI_DIFFICULTIES, AiDifficultyDefinition
from .ai_profile import AIProfile

COMMANDS = (
    "left", "right", "up", "down", "light_punch", "heavy_punch",
    "light_kick", "heavy_kick", "block", "throw", "energy", "pause",
)

__all__ = ["AIController", "AIProfile", "AiDifficultyDefinition", "AI_DIFFICULTIES", "COMMANDS"]
