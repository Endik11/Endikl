from ..settings import COLORS
from .base_screen import BaseScreen
from .ui_helpers import accept_pressed,back_pressed,draw_background,draw_text


class ModeProgressScreen(BaseScreen):
    title_key="mode.select.title";next_state=None
    def __init__(self,context=None):super().__init__(context);self.fonts=None;self.time=0
    def update(self,dt):
        self.time+=dt;pressed=self.context.input.pressed_for("p1")
        if back_pressed(pressed):self.context.state_manager.go_back()
        elif accept_pressed(pressed) and self.next_state:self.context.state_manager.request_change(self.next_state)
    def draw(self,surface):
        if self.fonts:draw_background(surface,self.time);draw_text(surface,self.fonts["title"],self.context.localization.get(self.title_key),(80,70),COLORS["white"])
