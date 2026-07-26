from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class AchievementDefinition:id:str;name_key:str;description_key:str;stat_key:str;target:int;reward_id:str;reward_points:int=0;hidden:bool=False
