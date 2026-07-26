import pygame
from ..enums import GameState,MatchMode
from ..settings import COLORS
from .base_screen import BaseScreen
from .ui_helpers import accept_pressed,back_pressed,draw_background,draw_text


class ModeSelectScreen(BaseScreen):
    modes=((MatchMode.LOCAL_VS,"mode.local"),(MatchMode.ARCADE,"mode.arcade"),(MatchMode.STORY,"mode.story"),(MatchMode.TOURNAMENT,"mode.tournament"),(MatchMode.TRAINING,"mode.training"))
    def __init__(self,context=None):super().__init__(context);self.selected=0;self.fonts=None;self.time=0
    def update(self,dt):
        self.time+=dt;pressed=self.context.input.pressed_for("p1")
        for event in self._consume_events():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                position = self.context.display.screen_to_virtual(event.pos)
                for index in range(len(self.modes)):
                    if pygame.Rect(90, 190 + index * 72, 560, 60).collidepoint(position):
                        self.selected = index
                        pressed = {**pressed, "light_punch": True}
                        break
        if pressed.get("down"):self.selected=(self.selected+1)%len(self.modes)
        elif pressed.get("up"):self.selected=(self.selected-1)%len(self.modes)
        elif back_pressed(pressed):self.context.state_manager.go_back()
        elif accept_pressed(pressed):
            mode=self.modes[self.selected][0];self.context.session.selected_mode=mode
            target={MatchMode.ARCADE:GameState.ARCADE_SELECT,MatchMode.STORY:GameState.STORY_SELECT,MatchMode.TOURNAMENT:GameState.TOURNAMENT_SETUP,MatchMode.TRAINING:GameState.TRAINING_SETUP}.get(mode,GameState.CHARACTER_SELECT)
            self.context.state_manager.request_change(target)
    def draw(self,surface):
        if not self.fonts:return
        draw_background(surface,self.time);draw_text(surface,self.fonts["title"],self.context.localization.get("mode.select.title"),(80,70),COLORS["white"])
        for index,(_,key) in enumerate(self.modes):draw_text(surface,self.fonts["menu"],self.context.localization.get(key),(140,210+index*72),COLORS["gold"] if index==self.selected else COLORS["white"])
