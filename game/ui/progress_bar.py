from dataclasses import dataclass
@dataclass(slots=True)
class ProgressBar:
    value:float=0;maximum:float=1
    @property
    def ratio(self):return max(0,min(1,self.value/max(.0001,self.maximum)))
