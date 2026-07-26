from __future__ import annotations
from dataclasses import dataclass
import pygame

@dataclass(slots=True)
class Widget:
    id:str;rect:pygame.Rect;accessible_label:str;enabled:bool=True;visible:bool=True;selected:bool=False;pressed:bool=False;hovered:bool=False;tooltip:str=""
    @property
    def focusable(self):return self.enabled and self.visible
    def contains(self,pos):return self.visible and self.rect.collidepoint(pos)
    def set_pointer(self,pos,down=False):self.hovered=self.contains(pos);self.pressed=self.hovered and down and self.enabled;return self.pressed
    def activate(self):return self.enabled and self.visible
