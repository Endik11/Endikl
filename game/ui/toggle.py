from dataclasses import dataclass
from .widget import Widget
@dataclass(slots=True)
class Toggle(Widget):
    value:bool=False
    def activate(self):
        if not super().activate():return False
        self.value=not self.value;return True
