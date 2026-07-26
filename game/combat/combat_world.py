from dataclasses import dataclass
import hashlib,json,random
from .combat_event import CombatEvent
from .combat_fighter import CombatFighter
from .combat_resolver import CombatResolver
from .fighter_controller import FighterController
from .fighter_physics import FighterPhysics
from .hit_stop import HitStopController
from .input_buffer import InputFrame
from .projectile_system import ProjectileSystem
from .round_controller import RoundController
from ..enums import RoundPhase
from .throw_system import ThrowSystem
@dataclass(frozen=True,slots=True)
class FighterSnapshot:fighter_id:str;health:int;meter:int;x:float;y:float;facing:int;state:str;attack_id:str
@dataclass(frozen=True,slots=True)
class CombatSnapshot:
    frame_number:int;round_timer_frames:int;fighter_one:FighterSnapshot;fighter_two:FighterSnapshot;projectiles:tuple;round_result:str;seed:int
    def digest(self):return hashlib.sha256(json.dumps(self,default=lambda o:o.__dict__ if hasattr(o,"__dict__") else {k:getattr(o,k) for k in o.__slots__},sort_keys=True).encode()).hexdigest()
class CombatWorld:
    def __init__(self,registry,p1_id,p2_id,arena_id,seed=1,round_seconds=99,rounds_to_win=2):
        self.registry=registry;self.frame_number=0;self.match_seed=seed;self.random=random.Random(seed);arena=registry.get_arena(arena_id);self.left_boundary=arena.left_boundary;self.right_boundary=arena.right_boundary;self.ground_y=arena.ground_y
        a=registry.get_fighter(p1_id);b=registry.get_fighter(p2_id);self.fighter_one=CombatFighter(a.id,a.max_health,a.max_health,350,self.ground_y,a.defense,combat_id="p1");self.fighter_two=CombatFighter(b.id,b.max_health,b.max_health,930,self.ground_y,b.defense,facing=-1,combat_id="p2")
        self.projectiles=[];self.last_separation_correction=0;self.round_timer_frames=round_seconds*60;self.round_controller=RoundController(self.round_timer_frames,rounds_to_win=rounds_to_win);self.round_transition_remaining=0;self.hit_stop=HitStopController();self.pending_events=[];self.controller=FighterController(registry);self.resolver=CombatResolver();self.projectile_system=ProjectileSystem();self.throw_system=ThrowSystem()
    def simulate_frame(self,input_one:InputFrame,input_two:InputFrame):
        self.pending_events=[]
        if self.round_controller.phase in {RoundPhase.ROUND_OVER,RoundPhase.DRAW,RoundPhase.DOUBLE_KO}:
            if self.round_transition_remaining<=0:self.round_transition_remaining=90
            self.round_transition_remaining-=1
            if self.round_transition_remaining==0:
                self.reset_round();self.round_controller.begin_next_round(self.round_timer_frames)
            self.frame_number+=1;return []
        if self.round_controller.phase is RoundPhase.MATCH_OVER:
            self.frame_number+=1;return []
        if self.hit_stop.active:
            self.fighter_one.input_buffer.push(input_one);self.fighter_two.input_buffer.push(input_two)
        if self.hit_stop.tick():self.frame_number+=1;return []
        self.controller.update(self,self.fighter_one,input_one);self.controller.update(self,self.fighter_two,input_two)
        throw_result=self.throw_system.attempt(self.frame_number,self.fighter_one,self.fighter_two,input_one,input_two) if "throw" in input_one.pressed else None
        if throw_result:
            self.pending_events.extend(throw_result.events)
            if throw_result.request:self.pending_events.extend(self.resolver.apply(self,self.fighter_one,self.fighter_two,throw_result.request).events)
        elif "throw" in input_two.pressed:
            throw_result=self.throw_system.attempt(self.frame_number,self.fighter_two,self.fighter_one,input_two,input_one)
            self.pending_events.extend(throw_result.events)
            if throw_result.request:self.pending_events.extend(self.resolver.apply(self,self.fighter_two,self.fighter_one,throw_result.request).events)
        desired_one=1 if self.fighter_two.x>=self.fighter_one.x else -1;desired_two=-desired_one
        if not self.fighter_one.active_attack or self.fighter_one.active_attack.frame_data.can_turn:self.fighter_one.facing=desired_one
        if not self.fighter_two.active_attack or self.fighter_two.active_attack.frame_data.can_turn:self.fighter_two.facing=desired_two
        FighterPhysics.update(self.fighter_one,self.left_boundary,self.right_boundary,self.ground_y);FighterPhysics.update(self.fighter_two,self.left_boundary,self.right_boundary,self.ground_y);self.last_separation_correction=FighterPhysics.separate(self.fighter_one,self.fighter_two,self.left_boundary,self.right_boundary)
        self.resolver.resolve(self,self.fighter_one,self.fighter_two,input_two);self.resolver.resolve(self,self.fighter_two,self.fighter_one,input_one);self.pending_events.extend(self.projectile_system.update(self,input_one,input_two))
        for fighter in (self.fighter_one,self.fighter_two):fighter.throw_invulnerability=max(0,fighter.throw_invulnerability-1);fighter.projectile_invulnerability=max(0,fighter.projectile_invulnerability-1)
        self.round_controller.tick();self.round_controller.evaluate(self.fighter_one.health,self.fighter_two.health);self.frame_number+=1;return list(self.pending_events)
    def snapshot(self):
        def snap(f):return FighterSnapshot(f.fighter_id,f.health,f.meter,round(f.x,6),round(f.y,6),f.facing,f.state.name,f.active_attack.attack_id if f.active_attack else "")
        return CombatSnapshot(self.frame_number,self.round_controller.timer_frames,snap(self.fighter_one),snap(self.fighter_two),tuple((p.id,p.owner_id,round(p.x,6),round(p.y,6),p.lifetime_frames,p.durability) for p in self.projectiles),self.round_controller.result,self.match_seed)
    def reset_round(self):
        sudden=self.round_controller.sudden_death_active
        for f,x in ((self.fighter_one,350),(self.fighter_two,930)):
            f.health=1 if sudden else f.max_health;f.x=x;f.y=self.ground_y;f.active_attack=None;f.velocity_x=0;f.velocity_y=0;f.hit_stun_remaining=0;f.block_stun_remaining=0
    def is_round_active(self):return self.round_controller.phase in {RoundPhase.FIGHT,RoundPhase.SUDDEN_DEATH}
