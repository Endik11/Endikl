from dataclasses import dataclass
from .widget import Widget
@dataclass(slots=True)
class Button(Widget):
    label_key:str="";action:str=""
