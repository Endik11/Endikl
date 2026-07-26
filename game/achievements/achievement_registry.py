import json
from pathlib import Path
from .achievement_definition import AchievementDefinition
class AchievementRegistry:
    def __init__(self,definitions):self.definitions={d.id:d for d in definitions}
    @classmethod
    def load(cls,path:Path):
        rows=json.loads(path.read_text(encoding="utf-8"))["achievements"];definitions=[AchievementDefinition(**row) for row in rows]
        if len({d.id for d in definitions})!=len(definitions):raise ValueError("Duplicate achievement id")
        return cls(definitions)
