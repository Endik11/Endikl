from dataclasses import dataclass
@dataclass(slots=True)
class AchievementProgress:value:int=0;unlocked:bool=False
