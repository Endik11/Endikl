from dataclasses import dataclass
from .enums import AttackPhase
@dataclass(frozen=True,slots=True)
class FrameData:
    startup_frames:int; active_frames:int; recovery_frames:int; hit_stun_frames:int; block_stun_frames:int; cancel_start_frame:int=0; cancel_end_frame:int=0; hit_stop_frames:int=3; block_stop_frames:int=2; movement_x_per_frame:float=0; movement_y_per_frame:float=0; can_turn:bool=False; can_hit_once:bool=True; multi_hit_interval_frames:int=1; hitboxes_by_frame:tuple=(); hurtbox_overrides_by_frame:tuple=(); armor_frames:tuple[int,...]=(); invulnerability_frames:tuple=(); projectile_definition:dict|None=None; properties:frozenset[str]=frozenset()
    @property
    def total_frames(self): return self.startup_frames+self.active_frames+self.recovery_frames
    def phase(self,frame):
        if frame<self.startup_frames:return AttackPhase.STARTUP
        if frame<self.startup_frames+self.active_frames:return AttackPhase.ACTIVE
        if frame<self.total_frames:return AttackPhase.RECOVERY
        return AttackPhase.COMPLETE
    def can_cancel(self,frame): return self.cancel_start_frame<=frame<=self.cancel_end_frame
    def hitbox_rows(self,frame):return dict(self.hitboxes_by_frame).get(frame,())
    def hurtbox_rows(self,frame):return dict(self.hurtbox_overrides_by_frame).get(frame,())
    def invulnerability(self,frame):return dict(self.invulnerability_frames).get(frame,frozenset())
