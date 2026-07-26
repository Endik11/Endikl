from __future__ import annotations
import pygame
import time
from .combat.combat_world import CombatWorld
from .combat.input_buffer import InputFrame
from .combat.simulation_clock import SimulationClock
from .combat.enums import CombatEventType
from .combat_renderer import CombatRenderer
from .ai import AIController, AIProfile
from .input_controllers import HumanController
class CombatMatchRuntime:
    def __init__(self,registry,input_manager,audio,settings,on_match_result=None):
        self.registry=registry;self.input=input_manager;self.audio=audio;self.settings=settings;self.on_match_result=on_match_result;self.world=None;self.clock=SimulationClock();self.renderer=CombatRenderer(registry,settings);self.renderer.clock=self.clock;self.paused=False;self.session=None;self._last_snapshot=None;self.controllers={}
    @property
    def uses_legacy_fighter(self):return False
    def start_match(self,session):
        if not session.ready_for_match:raise ValueError("Incomplete match selection")
        self.registry.get_fighter(session.player_one_fighter);self.registry.get_fighter(session.player_two_fighter);self.registry.get_arena(session.selected_arena);self.session=session
        seed=int(session.match_options.get("seed",1));self.world=CombatWorld(self.registry,session.player_one_fighter,session.player_two_fighter,session.selected_arena,seed,self.settings.gameplay.round_seconds,self.settings.gameplay.rounds_to_win);self.renderer.set_arena(session.selected_arena);self.clock.reset();self.paused=False;self._last_snapshot=self.world.snapshot();self.controllers=self._build_controllers(session,seed)
    def _build_controllers(self,session,seed):
        result={}
        for index,(slot,fighter_id) in enumerate((("p1",session.player_one_fighter),("p2",session.player_two_fighter))):
            kind=session.controller_types.get(slot,"human")
            if kind=="ai":
                fighter=self.registry.get_fighter(fighter_id);profile=AIProfile.from_dict(fighter_id,fighter.ai_profile);controller=AIController(profile,session.match_options.get("difficulty","medium"),fighter.attack_ids);controller.reset(seed+index);result[slot]=controller
            else:result[slot]=HumanController(self.input,slot)
        return result
    def handle_match_event(self,event):self.renderer.handle_event(event)
    def _frame(self,player):
        number=self.world.frame_number if self.world else 0;snapshot=self.world.snapshot();fighter_id=self.world.fighter_one.fighter_id if player=="p1" else self.world.fighter_two.fighter_id
        return self.controllers[player].build_input(snapshot,fighter_id,number)
    def update_match(self,dt):
        if not self.world or self.paused:return
        self.renderer.render_fps=1/dt if dt>0 else 0
        for _ in range(self.clock.consume(dt)):
            started=time.perf_counter();events=self.world.simulate_frame(self._frame("p1"),self._frame("p2"));self.renderer.simulation_frame_ms=(time.perf_counter()-started)*1000;self._dispatch(events)
        self._last_snapshot=self.world.snapshot()
        if self.world.round_controller.result and self.world.round_controller.phase.name=="MATCH_OVER":
            self.session.last_match_result={"result":self.world.round_controller.result,"snapshot":self._last_snapshot.digest()}
            if self.on_match_result:self.on_match_result()
    def _dispatch(self,events):
        self.renderer.handle_combat_events(events)
        for event in events:
            if hasattr(self.audio,"play_combat_event"):self.audio.play_combat_event(event)
            elif event.type is CombatEventType.ATTACK_HIT:self.audio.play_sfx("hit")
            elif event.type is CombatEventType.ATTACK_BLOCKED:self.audio.play_sfx("block")
    def draw_match(self,surface):
        if self.world:self.renderer.draw(surface,self.world.snapshot(),self.clock.alpha,self.world)
        else:surface.fill((8,9,12))
    def pause_match(self):self.paused=not self.paused
    def stop_match(self):self.world=None;self.clock.reset()
    def update_pause(self,dt):return None
    def draw_pause(self,surface):self.draw_match(surface)
    def update_result(self,dt):return None
    def draw_result(self,surface):self.draw_match(surface)
