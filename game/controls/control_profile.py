from dataclasses import dataclass,field
from .control_action import ControlAction,REQUIRED_ACTIONS
from .control_binding import ControlBinding
@dataclass(slots=True)
class ControlProfile:
    player:str;bindings:dict[ControlAction,ControlBinding]=field(default_factory=dict);device:str="keyboard"
    def validate(self):
        missing=REQUIRED_ACTIONS-set(self.bindings)
        if missing:raise ValueError("Missing required controls: "+",".join(sorted(x.value for x in missing)))
        return True
    def to_dict(self):return {"player":self.player,"device":self.device,"bindings":{a.value:{"device":b.device,"code":b.code,"direction":b.direction} for a,b in self.bindings.items()}}
    @classmethod
    def from_dict(cls,data):return cls(str(data.get("player","p1")),{ControlAction(k):ControlBinding(**v) for k,v in data.get("bindings",{}).items()},str(data.get("device","keyboard")))
