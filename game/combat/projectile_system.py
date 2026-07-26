from .block_system import BlockSystem
from .combat_event import CombatEvent
from .damage_request import DamageRequest
from .enums import CombatEventType,DamageSourceType,HitResult
from .hitbox import intersects
from .input_buffer import InputFrame


class ProjectileSystem:
    def create(self,world,projectile):
        world.projectiles.append(projectile)
        return CombatEvent(world.frame_number,CombatEventType.PROJECTILE_CREATED,projectile.owner_id,attack_id=projectile.id,position=(projectile.x,projectile.y))

    def update(self,world,input_one=None,input_two=None):
        events=[]
        has_fighters=hasattr(world,"fighter_one") and hasattr(world,"fighter_two")
        inputs={world.fighter_one.combat_id:input_one or InputFrame(),world.fighter_two.combat_id:input_two or InputFrame()} if has_fighters else {}
        alive=list(world.projectiles)
        for p in alive:
            p.velocity_x+=p.acceleration_x;p.velocity_y+=p.acceleration_y;p.x+=p.velocity_x;p.y+=p.velocity_y;p.lifetime_frames-=1
        ordered=sorted(alive,key=lambda p:(p.id,p.owner_id,p.x,p.y))
        for i,a in enumerate(ordered):
            for b in ordered[i+1:]:
                if a.durability<=0 or b.durability<=0 or a.owner_id==b.owner_id or not intersects(a.hitbox.rect(a.x,a.y,1),b.hitbox.rect(b.x,b.y,1)):continue
                self._clash(a,b);events.append(CombatEvent(world.frame_number,CombatEventType.PROJECTILE_CLASH,a.owner_id,b.owner_id,metadata={"a":a.id,"b":b.id}))
        for p in ordered if has_fighters else ():
            if p.durability<=0:continue
            target=world.fighter_two if p.owner_id==world.fighter_one.combat_id else world.fighter_one if p.owner_id==world.fighter_two.combat_id else None
            owner=world.fighter_one if p.owner_id==world.fighter_one.combat_id else world.fighter_two if p.owner_id==world.fighter_two.combat_id else None
            if target is None or owner is None or not p.can_hit(target.combat_id,world.frame_number):continue
            if not any(h.enabled and intersects(p.hitbox.rect(p.x,p.y,1),h.rect(target.x,target.y)) for h in target.hurtboxes):continue
            request=DamageRequest(p.owner_id,target.combat_id,p.id,p.damage,p.chip_damage,p.hit_level,DamageSourceType.PROJECTILE,p.properties,p.hit_stun,p.block_stun,40 if p.velocity_x>=0 else -40,0,0,0,"chip_kill" in p.properties)
            blocked=BlockSystem.is_blocking(target,p.x,p.hit_level,inputs[target.combat_id]);result=world.resolver.apply(world,owner,target,request,blocked=blocked)
            events.extend(result.events)
            if result.result in {HitResult.HIT,HitResult.BLOCKED,HitResult.ARMOR}:p.mark_hit(target.combat_id,world.frame_number)
            if result.result is HitResult.BLOCKED and p.destroy_on_block or result.result in {HitResult.HIT,HitResult.ARMOR} and p.destroy_on_hit:p.durability=0
        survivors=[]
        for p in alive:
            outside=not(world.left_boundary-100<p.x<world.right_boundary+100)
            if p.lifetime_frames>0 and p.durability>0 and not(outside and p.destroy_outside_arena):survivors.append(p)
            else:events.append(CombatEvent(world.frame_number,CombatEventType.PROJECTILE_DESTROYED,p.owner_id,attack_id=p.id))
        world.projectiles[:]=survivors;return events

    @staticmethod
    def _clash(a,b):
        if "pierce" in a.properties and "pierce" not in b.properties:b.durability=0;return
        if "pierce" in b.properties and "pierce" not in a.properties:a.durability=0;return
        if a.durability==b.durability:
            if a.priority==b.priority:a.durability=b.durability=0
            elif a.priority>b.priority:a.durability=1;b.durability=0
            else:b.durability=1;a.durability=0
        elif a.durability>b.durability:a.durability-=b.durability;b.durability=0
        else:b.durability-=a.durability;a.durability=0
