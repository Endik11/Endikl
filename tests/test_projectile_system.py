from types import SimpleNamespace
from game.combat.combat_world import CombatWorld
from game.combat.enums import AttackLevel,CombatEventType,HitResult
from game.combat.hitbox import Hitbox
from game.combat.input_buffer import InputFrame
from game.combat.projectile import Projectile
from game.combat.projectile_system import ProjectileSystem
from game.content_registry import ContentRegistry


def p(i,owner,x,y=100,v=2,**kwargs):return Projectile(i,owner,x,y,v,kwargs.pop("lifetime_frames",30),Hitbox(0,0,20,20,properties=kwargs.get("properties",frozenset())),kwargs.pop("damage",30),kwargs.pop("chip_damage",3),**kwargs)
def combat_world():
    r=ContentRegistry(allow_fallback=False);r.load_all();return CombatWorld(r,"kael","sable",next(iter(r.arenas)))


def test_create_move_lifetime_boundary_and_clash():
    w=SimpleNamespace(projectiles=[],frame_number=0,left_boundary=0,right_boundary=500);s=ProjectileSystem();assert s.create(w,p("a","p1",100)).type is CombatEventType.PROJECTILE_CREATED;s.create(w,p("b","p2",100,v=-2));events=s.update(w);assert sum(e.type is CombatEventType.PROJECTILE_CLASH for e in events)==1 and not w.projectiles


def test_projectile_hit_uses_resolver_has_no_self_hit_and_destroys():
    w=combat_world();a,b=w.fighter_one,w.fighter_two;before_a=a.health;before_b=b.health
    w.projectiles=[p("bolt",a.combat_id,b.x,b.y-100,v=0)];events=w.projectile_system.update(w)
    assert b.health<before_b and a.health==before_a and any(e.type is CombatEventType.PROJECTILE_HIT for e in events) and not w.projectiles


def test_projectile_block_chip_no_kill_and_block_stun():
    w=combat_world();a,b=w.fighter_one,w.fighter_two;b.health=2
    w.projectiles=[p("bolt",a.combat_id,b.x,b.y-100,v=0,chip_damage=5,destroy_on_block=True)]
    events=w.projectile_system.update(w,InputFrame(),InputFrame(right=True,block=True));assert b.health==1 and b.block_stun_remaining==10 and any(e.type is CombatEventType.PROJECTILE_BLOCKED for e in events)


def test_unblockable_invulnerability_armor_and_armor_break():
    w=combat_world();a,b=w.fighter_one,w.fighter_two
    unblock=p("u",a.combat_id,b.x,b.y-100,v=0);unblock.hit_level=AttackLevel.UNBLOCKABLE;before=b.health;w.projectiles=[unblock];w.projectile_system.update(w,InputFrame(),InputFrame(right=True,block=True));assert b.health<before
    b.invulnerability_flags={"projectile"};before=b.health;w.projectiles=[p("i",a.combat_id,b.x,b.y-100,v=0)];w.projectile_system.update(w);assert b.health==before
    b.invulnerability_flags.clear();b.armor_hits_remaining=1;w.projectiles=[p("a",a.combat_id,b.x,b.y-100,v=0)];w.projectile_system.update(w);assert b.health==before and b.armor_hits_remaining==0
    b.armor_hits_remaining=1;w.projectiles=[p("break",a.combat_id,b.x,b.y-100,v=0,properties=frozenset({"armor_break"}))];w.projectile_system.update(w);assert b.health<before


def test_multi_hit_interval_and_persistent_projectile():
    w=combat_world();a,b=w.fighter_one,w.fighter_two;shot=p("multi",a.combat_id,b.x,b.y-100,v=0,multi_hit=True,multi_hit_interval_frames=2,destroy_on_hit=False);w.projectiles=[shot]
    before=b.health;w.projectile_system.update(w);first=b.health;w.frame_number=1;w.projectile_system.update(w);assert b.health==first;w.frame_number=2;w.projectile_system.update(w);assert b.health<first<before


def test_clash_is_independent_of_list_order_and_uses_durability_priority():
    def outcome(reverse):
        w=SimpleNamespace(projectiles=[],frame_number=0,left_boundary=0,right_boundary=500);items=[p("a","p1",100,v=0,durability=2,priority=1),p("b","p2",100,v=0,durability=1,priority=4)];w.projectiles=list(reversed(items)) if reverse else items;ProjectileSystem().update(w);return sorted((x.id,x.durability) for x in w.projectiles)
    assert outcome(False)==outcome(True)==[("a",1)]
