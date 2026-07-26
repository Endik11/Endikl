from game.combat.combat_world import CombatWorld
from game.combat.damage_request import DamageRequest
from game.combat.enums import AttackLevel,DamageSourceType,HitResult
from game.content_registry import ContentRegistry


def world():
    registry=ContentRegistry(allow_fallback=False);registry.load_all()
    return CombatWorld(registry,"ren_kaido","ren_kaido",next(iter(registry.arenas)))


def request(source="strike",properties=frozenset()):
    kind={"strike":DamageSourceType.STRIKE,"projectile":DamageSourceType.PROJECTILE,"throw":DamageSourceType.THROW}[source]
    return DamageRequest("ren_kaido","ren_kaido","test",100,5,AttackLevel.MID,kind,properties,10,5)


def test_full_strike_and_projectile_invulnerability_prevent_damage_and_stun():
    w=world();a,b=w.fighter_one,w.fighter_two
    for flag,kind in (("full","strike"),("strike","strike"),("projectile","projectile")):
        b.invulnerability_flags={flag};before=b.health;result=w.resolver.apply(w,a,b,request(kind));assert result.result is HitResult.INVULNERABLE;assert b.health==before and b.hit_stun_remaining==0


def test_armor_absorbs_depletes_and_armor_break_hits():
    w=world();a,b=w.fighter_one,w.fighter_two;b.armor_hits_remaining=2;before=b.health
    assert w.resolver.apply(w,a,b,request()).result is HitResult.ARMOR;assert w.resolver.apply(w,a,b,request()).result is HitResult.ARMOR;assert b.health==before and b.armor_hits_remaining==0
    b.armor_hits_remaining=1;result=w.resolver.apply(w,a,b,request(properties=frozenset({"armor_break"})));assert result.result is HitResult.HIT and b.health<before


def test_throw_ignores_block_and_armor_but_respects_throw_invulnerability():
    w=world();a,b=w.fighter_one,w.fighter_two;b.blocking=True;b.armor_hits_remaining=2
    result=w.resolver.apply(w,a,b,request("throw"),blocked=True);assert result.result is HitResult.HIT
    b.throw_invulnerability=1;before=b.health;assert w.resolver.apply(w,a,b,request("throw")).result is HitResult.INVULNERABLE;assert b.health==before
