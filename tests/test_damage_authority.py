from game.combat.combat_world import CombatWorld
from game.combat.enums import CombatEventType
from game.combat.input_buffer import InputFrame
from game.content_registry import ContentRegistry


def test_throw_system_emits_one_request_and_resolver_applies_it_once():
    registry=ContentRegistry(allow_fallback=False);registry.load_all();w=CombatWorld(registry,"ren_kaido","ren_kaido",next(iter(registry.arenas)))
    a,b=w.fighter_one,w.fighter_two;a.x=500;b.x=570;before=b.health
    result=w.throw_system.attempt(1,a,b,InputFrame(throw=True),InputFrame());assert result.connected and result.request and b.health==before
    resolution=w.resolver.apply(w,a,b,result.request);assert b.health==before-resolution.health_damage
    assert sum(e.type is CombatEventType.THROW_DAMAGE_APPLIED for e in resolution.events)==1


def test_player_two_throw_ko_is_applied_once_and_round_controller_decides_winner():
    registry=ContentRegistry(allow_fallback=False);registry.load_all();w=CombatWorld(registry,"kael","sable",next(iter(registry.arenas)))
    a,b=w.fighter_one,w.fighter_two;a.x=500;b.x=570;a.health=100
    events=w.simulate_frame(InputFrame(),InputFrame(throw=True,pressed=frozenset({"throw"})))
    assert a.health==0 and w.round_controller.result=="PLAYER_2"
    assert sum(e.type is CombatEventType.THROW_DAMAGE_APPLIED for e in events)==1
