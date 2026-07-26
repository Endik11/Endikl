from dataclasses import dataclass
from .widget import Widget
@dataclass(slots=True)
class Slider(Widget):
    value:float=0;minimum:float=0;maximum:float=1;step:float=.1
    def adjust(self,direction):self.value=max(self.minimum,min(self.maximum,self.value+self.step*direction));return self.value
