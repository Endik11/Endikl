from dataclasses import dataclass
@dataclass(slots=True)
class HitStopController:
    remaining:int=0
    def start(self,frames):self.remaining=max(self.remaining,frames)
    def tick(self):
        if self.remaining>0:self.remaining-=1;return True
        return False
    @property
    def active(self):return self.remaining>0
