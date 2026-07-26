from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class ControlBinding:
    device:str;code:int;direction:int=0
    def __post_init__(self):
        if self.device not in {"keyboard","gamepad_button","gamepad_axis"}:raise ValueError("Unknown control device")
        if self.device=="gamepad_axis" and self.direction not in {-1,1}:raise ValueError("Axis binding needs direction")
    @property
    def identity(self):return self.device,self.code,self.direction
