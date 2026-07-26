from dataclasses import dataclass
from .combat_event import CombatEvent
from .damage_request import DamageRequest
from .enums import AttackLevel,CombatEventType,DamageSourceType,FighterState


@dataclass(frozen=True,slots=True)
class ThrowResolution:
    request:DamageRequest|None= None
    events:tuple[CombatEvent,...]=()
    connected:bool=False
    teched:bool=False
    side_switch:bool=False


@dataclass(slots=True)
class ThrowSystem:
    range:float=105;tech_window:int=6;damage:int=120;meter_gain:int=150
    def attempt(self,frame,attacker,defender,a_input,d_input,backward=False):
        if not a_input.throw:return None
        if not attacker.grounded or not defender.grounded or defender.throw_invulnerability>0 or abs(attacker.x-defender.x)>self.range:
            return ThrowResolution(events=(CombatEvent(frame,CombatEventType.THROW_WHIFFED,attacker.fighter_id,defender.fighter_id),))
        if d_input.throw:
            attacker.state=defender.state=FighterState.IDLE
            return ThrowResolution(events=(CombatEvent(frame,CombatEventType.THROW_TECHED,attacker.fighter_id,defender.fighter_id),),teched=True)
        attacker.state=FighterState.THROWING
        if backward:attacker.x,defender.x=defender.x,attacker.x
        request=DamageRequest(getattr(attacker,"combat_id",attacker.fighter_id),getattr(defender,"combat_id",defender.fighter_id),"throw",self.damage,0,AttackLevel.THROW,DamageSourceType.THROW,frozenset({"throw"}),18,0,90*getattr(attacker,"facing",1),-30,self.meter_gain,0,ignores_scaling=True)
        events=(CombatEvent(frame,CombatEventType.THROW_STARTED,attacker.fighter_id,defender.fighter_id),CombatEvent(frame,CombatEventType.THROW_CONNECTED,attacker.fighter_id,defender.fighter_id))
        return ThrowResolution(request,events,True,False,backward)
