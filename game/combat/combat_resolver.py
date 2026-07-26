from .block_system import BlockSystem
from .combat_event import CombatEvent
from .damage_request import CombatResolution, DamageRequest
from .damage_scaling import DamageScaling
from .enums import AttackPhase, CombatEventType, DamageSourceType, FighterState, HitResult
from .hitbox import intersects


class CombatResolver:
    """The only runtime service allowed to subtract combat health."""

    def apply(self, world, attacker, defender, request, *, blocked=False):
        invulnerability=self._is_invulnerable(defender,request)
        if invulnerability:
            event=CombatEvent(world.frame_number,CombatEventType.INVULNERABLE,request.source_id,request.target_id,request.attack_id or "")
            return CombatResolution(HitResult.INVULNERABLE,invulnerable=True,events=(event,))
        armored=request.source_type is not DamageSourceType.THROW and defender.armor_hits_remaining>0 and "armor_break" not in request.properties
        if armored:
            defender.armor_hits_remaining-=1
            event=CombatEvent(world.frame_number,CombatEventType.ARMOR_ABSORBED,request.source_id,request.target_id,request.attack_id or "")
            return CombatResolution(HitResult.ARMOR,armor_absorbed=True,events=(event,))
        if blocked and request.source_type is not DamageSourceType.THROW:
            before=defender.health;minimum=0 if request.can_chip_kill else 1
            defender.health=max(minimum,defender.health-request.chip_damage);damage=before-defender.health
            defender.block_stun_remaining=request.block_stun_frames;defender.state=FighterState.BLOCK_STUN;defender.velocity_x=request.knockback_x*.25
            kind=CombatEventType.PROJECTILE_BLOCKED if request.source_type is DamageSourceType.PROJECTILE else CombatEventType.ATTACK_BLOCKED
            event=CombatEvent(world.frame_number,kind,request.source_id,request.target_id,request.attack_id or "",damage)
            return CombatResolution(HitResult.BLOCKED,chip_damage=damage,blocked=True,block_stun_frames=request.block_stun_frames,applied_knockback=(request.knockback_x*.25,0),events=(event,))
        count=attacker.combo_tracker.hit_count+1
        damage=max(1,round(request.base_damage/max(.01,defender.defense))) if request.ignores_scaling else DamageScaling.damage(request.base_damage,count,defender.defense)
        defender.health=max(0,defender.health-damage);defender.hit_stun_remaining=request.hit_stun_frames;defender.state=FighterState.THROWN if request.source_type is DamageSourceType.THROW else FighterState.HIT_STUN;defender.last_hit_by=request.source_id
        attacker.meter=min(3000,attacker.meter+request.meter_gain_source);defender.meter=min(3000,defender.meter+request.meter_gain_target)
        if request.source_type is not DamageSourceType.THROW:
            attacker.combo_tracker.add(damage,world.frame_number,request.source_id,request.target_id,1 if request.ignores_scaling else DamageScaling.factor(count))
        kind={DamageSourceType.PROJECTILE:CombatEventType.PROJECTILE_HIT,DamageSourceType.THROW:CombatEventType.THROW_DAMAGE_APPLIED}.get(request.source_type,CombatEventType.ATTACK_HIT)
        event=CombatEvent(world.frame_number,kind,request.source_id,request.target_id,request.attack_id or "",damage)
        return CombatResolution(HitResult.HIT,health_damage=damage,hit_stun_frames=request.hit_stun_frames,applied_knockback=(request.knockback_x,request.knockback_y),meter_source=request.meter_gain_source,meter_target=request.meter_gain_target,events=(event,))

    def resolve(self,world,attacker,defender,defender_input):
        attack=attacker.active_attack
        if not attack or attack.phase is not AttackPhase.ACTIVE or not attack.can_hit(defender.combat_id):return CombatResolution(HitResult.MISS)
        boxes=attack.active_hitboxes()
        if not boxes:return CombatResolution(HitResult.MISS)
        box=next((box for box in boxes if (defender.combat_id,box.hit_id) not in attack.hit_ids and any(h.enabled and intersects(box.rect(attacker.x,attacker.y,attacker.facing),h.rect(defender.x,defender.y)) for h in defender.hurtboxes)),None)
        if box is None:return CombatResolution(HitResult.MISS)
        request=DamageRequest(attacker.combat_id,defender.combat_id,attack.attack_id,round(attack.damage*box.damage_multiplier),attack.chip_damage,box.hit_level,DamageSourceType.SUPER if "super" in box.properties else DamageSourceType.STRIKE,box.properties,attack.frame_data.hit_stun_frames,attack.frame_data.block_stun_frames,*box.knockback,attack.energy_gain,0,"chip_kill" in box.properties)
        blocked=BlockSystem.is_blocking(defender,attacker.x,box.hit_level,defender_input)
        result=self.apply(world,attacker,defender,request,blocked=blocked)
        if result.result not in {HitResult.MISS,HitResult.INVULNERABLE}:attack.mark_hit(defender.combat_id,box.hit_id)
        if result.result in {HitResult.HIT,HitResult.BLOCKED}:world.hit_stop.start(attack.frame_data.block_stop_frames if result.blocked else attack.frame_data.hit_stop_frames)
        world.pending_events.extend(result.events);return result

    @staticmethod
    def _is_invulnerable(defender,request):
        flags=defender.invulnerability_flags
        if "full" in flags:return True
        if request.source_type is DamageSourceType.PROJECTILE and ("projectile" in flags or defender.projectile_invulnerability>0):return True
        if request.source_type is DamageSourceType.THROW and ("throw" in flags or defender.throw_invulnerability>0):return True
        if request.source_type in {DamageSourceType.STRIKE,DamageSourceType.SUPER}:
            if "strike" in flags:return True
            if request.hit_level.name in {"HIGH","OVERHEAD"} and "upper_body" in flags:return True
            if request.hit_level.name=="LOW" and "low" in flags:return True
        return False
