from .attack_instance import AttackInstance
from .enums import AttackLevel,FighterState
from .frame_data import FrameData
from .hitbox import Hitbox
from .command_parser import CommandParser
from .hurtbox import Hurtbox
from .projectile import Projectile
from ..definition_adapters import build_combat_frame_data
class FighterController:
    def __init__(self,registry):self.registry=registry;self.command_parser=CommandParser()
    def update(self,world,fighter,input_frame):
        fighter.input_buffer.push(input_frame);fighter.state_frame+=1
        if fighter.hit_stun_remaining>0:fighter.hit_stun_remaining-=1;return
        if fighter.block_stun_remaining>0:fighter.block_stun_remaining-=1;return
        if fighter.active_attack:
            fighter.active_attack.advance();phase=fighter.active_attack.phase
            self._apply_frame(world,fighter)
            fighter.state={"STARTUP":FighterState.ATTACK_STARTUP,"ACTIVE":FighterState.ATTACK_ACTIVE,"RECOVERY":FighterState.ATTACK_RECOVERY}.get(phase.name,FighterState.IDLE)
            if fighter.active_attack.complete:fighter.active_attack=None
            return
        fighter.crouching=input_frame.down;fighter.blocking=input_frame.block
        direction=int(input_frame.right)-int(input_frame.left);fighter.velocity_x=direction*self.registry.get_fighter(fighter.fighter_id).walk_speed
        combo=self._matched_combo(fighter)
        attack_name=next((x for x in ("light_punch","heavy_punch","light_kick","heavy_kick") if x in input_frame.pressed),None)
        if combo:self.start_attack_id(world,fighter,combo.resulting_attack_id,combo.meter_cost)
        elif attack_name:self.start_attack(world,fighter,attack_name)
        else:fighter.state=FighterState.CROUCH if fighter.crouching else FighterState.WALK_FORWARD if direction else FighterState.IDLE
    def _matched_combo(self,fighter):
        aliases={"energy":"special"};valid={"light_punch","heavy_punch","light_kick","heavy_kick","special","throw","block"}
        combos=sorted((c for c in self.registry.combos.values() if c.enabled and c.meter_cost<=fighter.meter and c.owner_id in {"common",fighter.fighter_id}),key=lambda c:(-len(c.inputs),-c.priority,-c.meter_cost,-self._specificity(c.inputs),c.id))
        for combo in combos:
            tokens=[]
            for raw in combo.inputs:
                token=aliases.get(raw,raw);tokens.append({"button":token} if token in valid else {"direction":token})
            command={"id":combo.id,"inputs":tokens,"window":combo.max_gap_frames}
            if self.command_parser.match(fighter.input_buffer,command,fighter.facing):return combo
        return None
    @staticmethod
    def _specificity(inputs):
        directions={"down","down_back","down_forward","forward","back","up","neutral"}
        buttons={"light_punch","heavy_punch","light_kick","heavy_kick","special","throw","block","energy"}
        return sum(2 if item in directions else 1 if item in buttons else 0 for item in inputs)
    def start_attack(self,world,fighter,legacy_name):
        definition=next((a for a in self.registry.attacks.values() if a.legacy_action_name==legacy_name),None)
        return self._start_definition(fighter,definition,definition.energy_cost*3 if definition else 0)
    def start_attack_id(self,world,fighter,attack_id,cost):
        return self._start_definition(fighter,self.registry.attacks.get(attack_id),cost)
    def _start_definition(self,fighter,definition,cost):
        if not definition:return False
        if fighter.meter<cost:return False
        fighter.meter-=cost;level=AttackLevel[definition.hit_level.upper()]
        fd=build_combat_frame_data(definition)
        fighter.active_attack=AttackInstance(definition.id,fd,definition.damage,definition.chip_damage,Hitbox(definition.hitbox[0],definition.hitbox[1],definition.hitbox[2],definition.hitbox[3],hit_level=level,knockback=(definition.knockback_x,definition.knockback_y),properties=definition.properties),definition.energy_gain*3)
        fighter.state=FighterState.ATTACK_STARTUP;fighter.state_frame=0;return True
    def _apply_frame(self,world,fighter):
        attack=fighter.active_attack;fd=attack.frame_data;frame=attack.current_frame
        fighter.velocity_x+=fd.movement_x_per_frame*fighter.facing;fighter.velocity_y+=fd.movement_y_per_frame
        fighter.invulnerability_flags=set(fd.invulnerability(frame));fighter.armor_hits_remaining=1 if frame in fd.armor_frames else 0
        rows=fd.hurtbox_rows(frame)
        fighter.hurtboxes=[Hurtbox(float(r.get("x",-45)),float(r.get("y",-218)),float(r.get("width",90)),float(r.get("height",218)),str(r.get("region","body")),bool(r.get("enabled",True))) for r in rows] if rows else [Hurtbox()]
        spec=fd.projectile_definition
        if spec and not attack.projectile_spawned and frame==spec["spawn_frame"]:
            p=Projectile.from_definition(spec,fighter);attack.projectile_spawned=True;world.pending_events.append(world.projectile_system.create(world,p))
