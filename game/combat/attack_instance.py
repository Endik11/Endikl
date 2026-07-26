from dataclasses import dataclass,field
from .frame_data import FrameData
from .hitbox import Hitbox
@dataclass(slots=True)
class AttackInstance:
    attack_id:str; frame_data:FrameData; damage:int; chip_damage:int; hitbox:Hitbox; energy_gain:int=0; current_frame:int=0; hit_targets:set[str]=field(default_factory=set); last_hit_frame:dict[str,int]=field(default_factory=dict); hit_ids:set[tuple[str,str]]=field(default_factory=set); hit_confirmed:bool=False; blocked:bool=False; cancelled:bool=False; projectile_spawned:bool=False
    @property
    def phase(self): return self.frame_data.phase(self.current_frame)
    @property
    def complete(self): return self.current_frame>=self.frame_data.total_frames
    def advance(self): self.current_frame+=1
    def can_hit(self,target):
        if target not in self.hit_targets:return True
        return not self.frame_data.can_hit_once and self.current_frame-self.last_hit_frame.get(target,-999)>=self.frame_data.multi_hit_interval_frames
    def mark_hit(self,target,hit_id="main"): self.hit_targets.add(target);self.hit_ids.add((target,hit_id));self.last_hit_frame[target]=self.current_frame;self.hit_confirmed=True
    def active_hitboxes(self):
        rows=self.frame_data.hitbox_rows(self.current_frame)
        if not rows:return () if self.frame_data.hitboxes_by_frame else (self.hitbox,)
        return tuple(Hitbox(float(r["x"]),float(r["y"]),float(r["width"]),float(r["height"]),float(r.get("damage_multiplier",1)),str(r.get("hit_id","main")),int(r.get("priority",1)),self.hitbox.hit_level,self.hitbox.knockback,self.hitbox.properties) for r in rows)
