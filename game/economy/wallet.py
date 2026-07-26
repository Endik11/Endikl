from dataclasses import dataclass
@dataclass(slots=True)
class Wallet:
    points:int=0
    def __post_init__(self):self.points=max(0,int(self.points))
    def can_spend(self,amount):return 0<=amount<=self.points
    def spend(self,amount):
        if not self.can_spend(amount):return False
        self.points-=amount;return True
    def credit(self,amount):self.points+=max(0,int(amount))
