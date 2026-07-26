from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class Pushbox:
    offset:float=-45; width:float=90; height:float=218
    def rect(self,x,y): return (x+self.offset,y-self.height,self.width,self.height)
