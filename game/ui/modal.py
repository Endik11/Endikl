from dataclasses import dataclass,field
@dataclass(slots=True)
class Modal:
    id:str;widgets:list=field(default_factory=list);open:bool=False;critical:bool=False
    def show(self,focus):self.open=True;focus.open_modal(self.widgets)
    def close(self,focus):self.open=False;focus.close_modal()
