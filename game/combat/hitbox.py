from dataclasses import dataclass
from .enums import AttackLevel
@dataclass(frozen=True, slots=True)
class Hitbox:
    offset_x:float; offset_y:float; width:float; height:float; damage_multiplier:float=1; hit_id:str="main"; priority:int=1; hit_level:AttackLevel=AttackLevel.MID; knockback:tuple[float,float]=(0,0); properties:frozenset[str]=frozenset()
    def rect(self,x,y,facing): return (x+self.offset_x if facing>0 else x-self.offset_x-self.width,y+self.offset_y,self.width,self.height)
def intersects(a,b): return a[0]<b[0]+b[2] and a[0]+a[2]>b[0] and a[1]<b[1]+b[3] and a[1]+a[3]>b[1]
