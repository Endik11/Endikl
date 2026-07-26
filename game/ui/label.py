from dataclasses import dataclass
from .widget import Widget
@dataclass(slots=True)
class Label(Widget):text_key:str=""
