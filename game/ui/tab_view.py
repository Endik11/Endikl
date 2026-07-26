from dataclasses import dataclass
@dataclass(slots=True)
class TabView:
    tabs:tuple[str,...];index:int=0
    def select(self,direction):self.index=(self.index+direction)%len(self.tabs);return self.tabs[self.index]
