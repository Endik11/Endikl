from dataclasses import dataclass
@dataclass(frozen=True,slots=True)
class PurchaseResult:success:bool;code:str;transaction_id:str="";item_id:str=""
