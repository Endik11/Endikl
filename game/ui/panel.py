from dataclasses import dataclass,field
from .widget import Widget
@dataclass(slots=True)
class Panel(Widget):children:list[Widget]=field(default_factory=list)
