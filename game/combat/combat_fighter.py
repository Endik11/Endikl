from dataclasses import dataclass,field
from .enums import FighterState
from .hurtbox import Hurtbox
from .pushbox import Pushbox
from .combo_tracker import ComboTracker
from .input_buffer import InputBuffer
@dataclass(slots=True)
class CombatFighter:
    fighter_id:str;health:int;max_health:int;x:float;y:float;defense:float=1;recoverable_health:int=0;meter:int=0;velocity_x:float=0;velocity_y:float=0;facing:int=1;state:FighterState=FighterState.IDLE;state_frame:int=0;active_attack:object=None;current_animation:str="idle";grounded:bool=True;crouching:bool=False;blocking:bool=False;hit_stun_remaining:int=0;block_stun_remaining:int=0;knockdown_remaining:int=0;invulnerability_flags:set[str]=field(default_factory=set);armor_hits_remaining:int=0;combo_tracker:ComboTracker=field(default_factory=ComboTracker);input_buffer:InputBuffer=field(default_factory=InputBuffer);pushbox:Pushbox=field(default_factory=Pushbox);hurtboxes:list[Hurtbox]=field(default_factory=lambda:[Hurtbox()]);throw_invulnerability:int=0;projectile_invulnerability:int=0;last_hit_by:str="";round_wins:int=0;combat_id:str=""
    @property
    def position(self):return (self.x,self.y)
    @property
    def velocity(self):return (self.velocity_x,self.velocity_y)
    def __post_init__(self):
        if not self.combat_id:self.combat_id=self.fighter_id
