from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class Hurtbox:
    offset_x:float=-45; offset_y:float=-218; width:float=90; height:float=218; region:str="body"; enabled:bool=True
    def rect(self,x,y,facing=1): return (x+self.offset_x,y+self.offset_y,self.width,self.height)
