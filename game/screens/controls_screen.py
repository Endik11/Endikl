from pathlib import Path
import pygame
from ..controls import ControlsManager,RebindingSession,ControlAction,ControlBinding
from ..settings import COLORS
from ..user_data_manager import get_user_data_manager
from .base_screen import BaseScreen
from .ui_helpers import draw_background,draw_text
class ControlsScreen(BaseScreen):
    def __init__(self,context=None):
        super().__init__(context);self.fonts=None;self.time=0;self.player="p1";self.actions=list(ControlAction);self.index=0;self.manager=ControlsManager(get_user_data_manager().paths.controls);self.manager.load();self.rebinding=None;self.message=""
    def handle_event(self,event):
        if self.rebinding and self.rebinding.waiting_for:
            binding=None
            if event.type==pygame.KEYDOWN:binding=ControlBinding("keyboard",event.key)
            elif event.type==pygame.JOYBUTTONDOWN:binding=ControlBinding("gamepad_button",event.button)
            elif event.type==pygame.JOYAXISMOTION and abs(event.value)>.6:binding=ControlBinding("gamepad_axis",event.axis,1 if event.value>0 else -1)
            if binding:self.message="conflict" if not self.rebinding.capture(binding) else "ready"
        else:super().handle_event(event)
    def update(self,dt):
        self.time+=dt;pressed=self.context.input.pressed_for("p1")
        if self.rebinding and self.rebinding.waiting_for:
            if pressed.get("block"):self.rebinding.cancel();self.rebinding=None
            elif pressed.get("light_punch") and self.rebinding.pending:
                if self.rebinding.apply(True):self.manager.save();self.rebinding=None
            return
        if pressed.get("down"):self.index=(self.index+1)%len(self.actions)
        elif pressed.get("up"):self.index=(self.index-1)%len(self.actions)
        elif pressed.get("left") or pressed.get("right"):self.player="p2" if self.player=="p1" else "p1"
        elif pressed.get("light_punch"):
            self.rebinding=RebindingSession(self.manager.profiles[self.player],[self.manager.profiles["p2" if self.player=="p1" else "p1"]]);self.rebinding.begin(self.actions[self.index])
        elif pressed.get("energy"):self.manager.restore_defaults(self.player);self.manager.save()
        elif pressed.get("block"):self.context.state_manager.go_back()
    def draw(self,surface):
        if not self.fonts:return
        draw_background(surface,self.time);draw_text(surface,self.fonts["title"],"Controls",(80,60),COLORS["white"]);draw_text(surface,self.fonts["menu"],self.player.upper(),(100,150),COLORS["gold"])
        for i,action in enumerate(self.actions[:9]):draw_text(surface,self.fonts["small"],action.value,(120,220+i*42),COLORS["gold"] if i==self.index else COLORS["white"])
