from __future__ import annotations
import pygame
from .combat.constants import DEBUG_COLORS,SIMULATION_FPS
from .settings import COLORS,VIRTUAL_WIDTH


class CombatRenderer:
    def __init__(self,registry):
        self.registry=registry;self.previous=None;self.debug={i:False for i in range(1,9)};self.font=None;self.render_fps=0;self.simulation_frame_ms=0;self.clock=None
    def handle_event(self,event):
        if event.type==pygame.KEYDOWN and pygame.K_F1<=event.key<=pygame.K_F8:self.debug[event.key-pygame.K_F1+1]=not self.debug[event.key-pygame.K_F1+1]
    def draw(self,surface,snapshot,alpha=0,world=None):
        surface.fill((16,20,24));pygame.draw.line(surface,COLORS["gold"],(0,584),(VIRTUAL_WIDTH,584),4)
        for snap in (snapshot.fighter_one,snapshot.fighter_two):
            definition=self.registry.get_fighter(snap.fighter_id);rect=pygame.Rect(int(snap.x-45),int(snap.y-218),90,218);pygame.draw.rect(surface,definition.palette[0],rect,border_radius=22);pygame.draw.rect(surface,definition.palette[1],rect,4,border_radius=22)
        self._bar(surface,70,38,snapshot.fighter_one.health,self.registry.get_fighter(snapshot.fighter_one.fighter_id).max_health);self._bar(surface,850,38,snapshot.fighter_two.health,self.registry.get_fighter(snapshot.fighter_two.fighter_id).max_health)
        if world:self._geometry(surface,world)
        if any(self.debug.values()):self._overlay(surface,snapshot,world,alpha)
        self.previous=snapshot
    def _geometry(self,surface,world):
        for fighter in (world.fighter_one,world.fighter_two):
            if self.debug[2] and fighter.active_attack:
                for box in fighter.active_attack.active_hitboxes():pygame.draw.rect(surface,DEBUG_COLORS["hitbox"],box.rect(fighter.x,fighter.y,fighter.facing),2)
            if self.debug[3]:
                for box in fighter.hurtboxes:pygame.draw.rect(surface,DEBUG_COLORS["hurtbox"],box.rect(fighter.x,fighter.y),2)
            if self.debug[4]:pygame.draw.rect(surface,DEBUG_COLORS["pushbox"],fighter.pushbox.rect(fighter.x,fighter.y),2)
        if self.debug[4]:pygame.draw.line(surface,DEBUG_COLORS["pushbox"],(world.left_boundary,0),(world.left_boundary,720),1);pygame.draw.line(surface,DEBUG_COLORS["pushbox"],(world.right_boundary,0),(world.right_boundary,720),1)
    def _overlay(self,surface,snapshot,world,alpha):
        if self.font is None:self.font=pygame.font.Font(None,18)
        lines=[]
        if self.debug[1]:lines.append(f"F1 render {self.render_fps:.1f} sim {SIMULATION_FPS} accumulator {getattr(self.clock,'accumulator',0):.5f} skipped {getattr(self.clock,'skipped_frames',0)} frame_ms {self.simulation_frame_ms:.3f} alpha {alpha:.2f}")
        if world:
            fighters=(world.fighter_one,world.fighter_two)
            if self.debug[2]:
                for f in fighters:
                    lines.append(f"F2 {f.combat_id}/{f.fighter_id} attack={f.active_attack.attack_id if f.active_attack else '-'}")
                    if f.active_attack:lines.extend(f"  hit_id={b.hit_id} priority={b.priority} level={b.hit_level.name}" for b in f.active_attack.active_hitboxes())
            if self.debug[3]:lines.extend(f"F3 {f.fighter_id} hurtboxes="+",".join(f"{h.region}:{'on' if h.enabled else 'off'}" for h in f.hurtboxes) for f in fighters)
            if self.debug[4]:lines.append(f"F4 bounds={world.left_boundary:.0f}..{world.right_boundary:.0f} separation={world.last_separation_correction:.2f}")
            if self.debug[5]:
                for f in fighters:
                    a=f.active_attack;fd=a.frame_data if a else None;lines.append(f"F5 {f.fighter_id} {f.state.name}[{f.state_frame}] attack={a.attack_id if a else '-'} frame={a.current_frame if a else 0} data={fd.startup_frames if fd else 0}/{fd.active_frames if fd else 0}/{fd.recovery_frames if fd else 0} cancel={fd.cancel_start_frame if fd else 0}-{fd.cancel_end_frame if fd else 0} invuln={sorted(f.invulnerability_flags)} armor={f.armor_hits_remaining}")
            if self.debug[6]:
                for f in fighters:
                    lines.append(f"F6 {f.fighter_id} input history command={f.input_buffer.last_command or '-'}")
                    lines.extend(f"  {x.frame_number}: {x.direction(f.facing)} p={sorted(x.pressed)} r={sorted(x.released)} h={sorted(x.held)}" for x in f.input_buffer.recent(14))
            if self.debug[7]:lines.extend(f"F7 {f.fighter_id} hp={f.health}+{f.recoverable_health} meter={f.meter} hit={f.hit_stun_remaining} block={f.block_stun_remaining} combo={f.combo_tracker.hit_count}/{f.combo_tracker.total_damage} scale={f.combo_tracker.current_scaling:.2f}" for f in fighters);lines.append(f"hit stop={world.hit_stop.remaining} frame_advantage={fighters[1].hit_stun_remaining-fighters[0].hit_stun_remaining}")
            if self.debug[8]:lines.append(f"F8 seed={snapshot.seed} frame={snapshot.frame_number} digest={snapshot.digest()[:12]} projectiles={len(world.projectiles)} phase={world.round_controller.phase.name} timer={world.round_controller.timer_frames} draws={world.round_controller.draw_retries}")
        for i,line in enumerate(lines[:32]):surface.blit(self.font.render(line,True,COLORS["white"]),(12,90+i*18))
    def _bar(self,surface,x,y,value,maximum):pygame.draw.rect(surface,(40,40,45),(x,y,360,20));pygame.draw.rect(surface,COLORS["red"],(x,y,int(360*max(0,value)/maximum),20))
