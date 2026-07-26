from dataclasses import dataclass
from .ui_theme import UITheme

@dataclass(slots=True)
class UIContext:
    theme:UITheme;scale:float=1.0;reduced_motion:bool=False;virtual_size:tuple[int,int]=(1280,720);modal:object|None=None
