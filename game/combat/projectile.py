from dataclasses import dataclass,field
from .enums import AttackLevel
from .hitbox import Hitbox


@dataclass(slots=True)
class Projectile:
    id:str;owner_id:str;x:float;y:float;velocity_x:float;lifetime_frames:int;hitbox:Hitbox;damage:int;chip_damage:int;hit_level:AttackLevel=AttackLevel.MID;hit_stun:int=15;block_stun:int=10;priority:int=1;durability:int=1;already_hit_targets:set[str]=field(default_factory=set);properties:frozenset[str]=frozenset();velocity_y:float=0;acceleration_x:float=0;acceleration_y:float=0;multi_hit:bool=False;multi_hit_interval_frames:int=1;last_hit_frame:dict[str,int]=field(default_factory=dict);destroy_on_hit:bool=True;destroy_on_block:bool=True;destroy_outside_arena:bool=True

    @classmethod
    def from_definition(cls,spec,owner):
        facing=owner.facing
        return cls(str(spec["projectile_id"]),owner.combat_id,owner.x+float(spec["offset_x"])*facing,owner.y+float(spec["offset_y"]),float(spec["velocity_x"])*facing,int(spec["lifetime_frames"]),Hitbox(0,0,float(spec["width"]),float(spec["height"]),hit_level=AttackLevel[str(spec["hit_level"]).upper()],properties=frozenset(spec["properties"])),int(spec["damage"]),int(spec["chip_damage"]),AttackLevel[str(spec["hit_level"]).upper()],int(spec["hit_stun_frames"]),int(spec["block_stun_frames"]),int(spec["priority"]),int(spec["durability"]),properties=frozenset(spec["properties"]),velocity_y=float(spec["velocity_y"]),acceleration_x=float(spec["acceleration_x"])*facing,acceleration_y=float(spec["acceleration_y"]),multi_hit=bool(spec["multi_hit"]),multi_hit_interval_frames=int(spec["multi_hit_interval_frames"]),destroy_on_hit=bool(spec["destroy_on_hit"]),destroy_on_block=bool(spec["destroy_on_block"]),destroy_outside_arena=bool(spec["destroy_outside_arena"]))

    def can_hit(self,target,frame):return target not in self.already_hit_targets or self.multi_hit and frame-self.last_hit_frame.get(target,-999)>=self.multi_hit_interval_frames
    def mark_hit(self,target,frame):self.already_hit_targets.add(target);self.last_hit_frame[target]=frame
