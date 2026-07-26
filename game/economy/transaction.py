from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class Transaction:id:str;item_id:str;amount:int
