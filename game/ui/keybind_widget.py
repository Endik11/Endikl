from dataclasses import dataclass
from .widget import Widget
@dataclass(slots=True)
class KeybindWidget(Widget):action_id:str="";binding_label:str=""
