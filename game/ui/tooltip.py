from dataclasses import dataclass
@dataclass(slots=True)
class Tooltip:text_key:str;delay:float=.45;elapsed:float=0;visible:bool=False
