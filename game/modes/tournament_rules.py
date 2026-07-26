from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TournamentRules:
    size:int=4
    third_place:bool=False
    def __post_init__(self):
        if self.size not in (4,8):raise ValueError("Tournament size must be 4 or 8")
