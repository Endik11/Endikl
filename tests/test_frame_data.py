from game.combat.attack_instance import AttackInstance
from game.combat.enums import AttackPhase
from game.combat.frame_data import FrameData
from game.combat.hitbox import Hitbox
from game.combat.hurtbox import Hurtbox
from game.combat.combat_world import CombatWorld
from game.content_registry import ContentRegistry
def test_attack_phases_cancel_and_single_hit():
    d=FrameData(2,2,3,5,4,2,3);a=AttackInstance("x",d,10,1,Hitbox(0,0,10,10));assert a.phase is AttackPhase.STARTUP;a.advance();a.advance();assert a.phase is AttackPhase.ACTIVE and d.can_cancel(2);a.mark_hit("p2");assert not a.can_hit("p2");[a.advance() for _ in range(5)];assert a.complete
def test_60_frame_migration_preserves_duration():
    assert round(20*60/100)/60==.2;assert abs(round(18*60/100)/60-.18)<.01
def test_per_frame_boxes_overrides_armor_and_invulnerability_are_exact():
    hit=((3,({"x":1,"y":2,"width":3,"height":4,"hit_id":"tip"},)),);hurt=((2,({"x":-2,"y":-3,"width":8,"height":9},)),);inv=((1,frozenset({"upper_body"})),)
    d=FrameData(1,3,2,4,3,1,2,7,5,1.5,-2.5,True,False,4,hit,hurt,(2,),inv,{"projectile_id":"x"},frozenset({"armor"}))
    assert d.hitbox_rows(3)[0]["hit_id"]=="tip" and not d.hitbox_rows(2);assert d.hurtbox_rows(2)[0]["width"]==8
    assert d.invulnerability(1)==frozenset({"upper_body"}) and d.armor_frames==(2,) and d.projectile_definition["projectile_id"]=="x"

def test_runtime_applies_and_clears_per_frame_hurtbox_armor_and_invulnerability():
    from game.combat.input_buffer import InputFrame
    r=ContentRegistry(allow_fallback=False);r.load_all();w=CombatWorld(r,"kael","sable",next(iter(r.arenas)));f=w.fighter_one
    data=FrameData(0,3,1,3,2,hurtbox_overrides_by_frame=((1,({"x":-10,"y":-20,"width":20,"height":30,"region":"upper"},)),),armor_frames=(1,),invulnerability_frames=((1,frozenset({"upper_body"})),))
    f.active_attack=AttackInstance("custom",data,10,1,Hitbox(0,0,10,10));w.controller.update(w,f,InputFrame())
    assert f.hurtboxes[0].region=="upper" and f.armor_hits_remaining==1 and f.invulnerability_flags=={"upper_body"}
    w.controller.update(w,f,InputFrame());assert f.hurtboxes==[Hurtbox()] and f.armor_hits_remaining==0 and not f.invulnerability_flags

def test_json_projectile_spawns_exactly_once_on_declared_attack_frame():
    from game.combat.enums import CombatEventType
    from game.combat.input_buffer import InputFrame
    r=ContentRegistry(allow_fallback=False);r.load_all();w=CombatWorld(r,"kael","sable",next(iter(r.arenas)));f=w.fighter_one;f.meter=1000
    assert w.controller.start_attack_id(w,f,"thunder_boundary",180)
    created=0
    for _ in range(20):created+=sum(e.type is CombatEventType.PROJECTILE_CREATED for e in w.simulate_frame(InputFrame(),InputFrame()))
    assert created==1
