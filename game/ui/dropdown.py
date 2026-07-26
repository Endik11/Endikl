from dataclasses import dataclass,field
from .widget import Widget
@dataclass(slots=True)
class Dropdown(Widget):
    options:tuple[str,...]=()
    index:int=0

    def choose(self,direction):
        if self.options:self.index=(self.index+direction)%len(self.options)
        return self.options[self.index] if self.options else None
