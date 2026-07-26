from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class Notification:id:str;text_key:str;kind:str="info";duration:float=3
