from dataclasses import dataclass,field
from .constants import INPUT_BUFFER_FRAMES
BUTTONS=("light_punch","heavy_punch","light_kick","heavy_kick","block","throw","special")
@dataclass(frozen=True,slots=True)
class InputFrame:
    left:bool=False; right:bool=False; up:bool=False; down:bool=False; light_punch:bool=False; heavy_punch:bool=False; light_kick:bool=False; heavy_kick:bool=False; block:bool=False; throw:bool=False; special:bool=False; pressed:frozenset[str]=frozenset(); released:frozenset[str]=frozenset(); held:frozenset[str]=frozenset(); frame_number:int=0
    def direction(self,facing=1):
        x=int(self.right)-int(self.left);y=int(self.up)-int(self.down); x*=facing
        return {(0,0):5,(0,-1):2,(0,1):8,(-1,0):4,(1,0):6,(-1,-1):1,(1,-1):3,(-1,1):7,(1,1):9}[(x,y)]
@dataclass(slots=True)
class InputBuffer:
    capacity:int=INPUT_BUFFER_FRAMES; frames:list[InputFrame]=field(default_factory=list); consumed:set[tuple]=field(default_factory=set);consumed_frames:set[int]=field(default_factory=set);last_command:str=""
    def push(self,frame):
        self.frames.append(frame);self.frames=self.frames[-self.capacity:]
        live={x.frame_number for x in self.frames};self.consumed_frames.intersection_update(live)
    def recent(self,window=None): return self.frames[-(window or self.capacity):]
    def consume(self,key,frame_numbers=()):
        if key in self.consumed:return False
        self.consumed.add(key);self.consumed_frames.update(frame_numbers);self.last_command=str(key[0]);return True
    def clear(self): self.frames.clear();self.consumed.clear();self.consumed_frames.clear();self.last_command=""
