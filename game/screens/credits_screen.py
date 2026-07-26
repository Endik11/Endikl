from ..settings import COLORS,GAME_TITLE
from ..version import VERSION,BUILD_CHANNEL
from .base_screen import BaseScreen
from .ui_helpers import draw_background,draw_text
class CreditsScreen(BaseScreen):
    def __init__(self,context=None):super().__init__(context);self.fonts=None;self.time=0
    def update(self,dt):self.time+=dt;self.context.state_manager.go_back() if self.context.input.pressed_for("p1").get("block") else None
    def draw(self,surface):
        if not self.fonts:return
        draw_background(surface,self.time);lines=(self.context.localization.get("credits.title"),GAME_TITLE,"Python / pygame","Original procedural project","Unverified assets are disabled by default",f"Version {VERSION} ({BUILD_CHANNEL})")
        for i,line in enumerate(lines):draw_text(surface,self.fonts["menu"] if i else self.fonts["title"],line,(90,80+i*72),COLORS["gold"] if i==0 else COLORS["white"])
