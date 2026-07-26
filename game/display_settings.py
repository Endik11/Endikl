from copy import deepcopy
from dataclasses import dataclass

@dataclass(slots=True)
class DisplaySettingsSession:
    display:object;settings:object;timeout:float=10;pending:bool=False;remaining:float=0;previous:object=None
    def apply_temporary(self,width,height,mode):
        self.previous=deepcopy(self.settings.video);self.settings.video.width=width;self.settings.video.height=height;self.settings.video.display_mode=mode;self.settings.video.fullscreen=mode=="fullscreen"
        try:self.display.apply_settings()
        except Exception:
            self.settings.video.width=1280;self.settings.video.height=720;self.settings.video.display_mode="windowed";self.settings.video.fullscreen=False;self.display.apply_settings();return False
        self.pending=True;self.remaining=self.timeout;return True
    def update(self,dt):
        if self.pending:
            self.remaining-=dt
            if self.remaining<=0:self.revert()
    def confirm(self):self.pending=False;self.previous=None
    def revert(self):
        if self.previous is not None:self.settings.video=self.previous;self.display.apply_settings()
        self.pending=False;self.previous=None
