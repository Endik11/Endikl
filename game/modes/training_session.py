from dataclasses import asdict,dataclass,field
from ..training.training_settings import TrainingSettings
from ..training.training_metrics import TrainingMetrics


@dataclass(slots=True)
class TrainingSession:
    fighter_id:str;dummy_fighter_id:str;arena_id:str;settings:TrainingSettings=field(default_factory=TrainingSettings);metrics:TrainingMetrics=field(default_factory=TrainingMetrics);frames:int=0;side_swapped:bool=False
    def swap_side(self):self.side_swapped=not self.side_swapped
    def tick(self):self.frames+=1
    def to_dict(self):return {"fighter_id":self.fighter_id,"dummy_fighter_id":self.dummy_fighter_id,"arena_id":self.arena_id,"settings":asdict(self.settings),"frames":self.frames,"side_swapped":self.side_swapped}
    @classmethod
    def from_dict(cls,data):return cls(str(data["fighter_id"]),str(data["dummy_fighter_id"]),str(data["arena_id"]),TrainingSettings(**data.get("settings",{})),frames=max(0,int(data.get("frames",0))),side_swapped=bool(data.get("side_swapped",False)))
