from dataclasses import dataclass
@dataclass(slots=True)
class ScrollView:
    content_height:int;viewport_height:int;offset:int=0
    def scroll(self,amount):self.offset=max(0,min(max(0,self.content_height-self.viewport_height),self.offset+amount));return self.offset
