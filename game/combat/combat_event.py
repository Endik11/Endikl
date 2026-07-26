from dataclasses import dataclass, field
from .enums import CombatEventType
@dataclass(frozen=True, slots=True)
class CombatEvent:
    frame:int; type:CombatEventType; source_id:str=""; target_id:str=""; attack_id:str=""; value:float=0; position:tuple[float,float]=(0,0); metadata:dict[str,object]=field(default_factory=dict)
