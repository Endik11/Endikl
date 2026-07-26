import pygame

from ..settings import COLORS
from .base_screen import BaseScreen
from .ui_helpers import draw_background,draw_text
class ProfileScreen(BaseScreen):
    def __init__(self,context=None):super().__init__(context);self.fonts=None;self.time=0
    def update(self,dt):
        self.time+=dt
        pressed = self.context.input.pressed_for("p1")
        if pressed.get("cancel") or pressed.get("block"):
            self.context.state_manager.go_back()
            return
        for event in self._consume_events():
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                self.context.state_manager.go_back()
                return
    def draw(self,surface):
        if not self.fonts:return
        profile=self.context.saves.profile;stats=profile.statistics;matches=int(stats.get("matches_played",0));wins=int(stats.get("wins",0));rate=0 if not matches else wins*100/matches
        draw_background(surface,self.time);draw_text(surface,self.fonts["title"],self.context.localization.get("profile.title"),(90,70),COLORS["white"])
        rows=(getattr(profile,"display_name","Player"),f"{wins}/{stats.get('losses',0)}/{stats.get('draws',0)}",f"{rate:.1f}%",str(stats.get("longest_combo",0)),str(profile.currency))
        for i,value in enumerate(rows):draw_text(surface,self.fonts["menu"],value,(120,210+i*58),COLORS["gold"] if i==0 else COLORS["white"])
