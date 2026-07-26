from types import SimpleNamespace
from game.combat.enums import HitResult,CombatEventType
from game.combat.input_buffer import InputFrame
from game.combat.throw_system import ThrowSystem
def f(i,x):return SimpleNamespace(fighter_id=i,x=x,health=1000,meter=0,grounded=True,throw_invulnerability=0,state=None)
def test_throw_whiff_tech_airborne_and_once():
    s=ThrowSystem();a,b=f("a",100),f("b",180);result=s.attempt(1,a,b,InputFrame(throw=True),InputFrame());assert result.connected and result.request.base_damage==120 and b.health==1000
    a,b=f("a",100),f("b",180);result=s.attempt(1,a,b,InputFrame(throw=True),InputFrame(throw=True));assert result.teched and result.events[0].type is CombatEventType.THROW_TECHED;b.grounded=False;assert not s.attempt(2,a,b,InputFrame(throw=True),InputFrame()).connected
