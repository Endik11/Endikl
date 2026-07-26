from __future__ import annotations
from dataclasses import asdict,dataclass,field
from .tournament_bracket import BracketMatch,build_bracket,next_match


@dataclass(slots=True)
class TournamentSession:
    participants:list[str];player_id:str;seed:int;third_place:bool=False;matches:list[BracketMatch]=field(default_factory=list);processed_result_ids:set[str]=field(default_factory=set);completed:bool=False;champion:str=""
    def __post_init__(self):
        if not self.matches:self.matches=build_bracket(self.participants,self.third_place)
    @property
    def current_match(self):return next_match(self.matches)
    def record_result(self,match_id,result_id,winner):
        if result_id in self.processed_result_ids:return False
        match=next((m for m in self.matches if m.id==match_id),None)
        if match is None or match.winner or winner not in {match.fighter_one,match.fighter_two}:return False
        match.winner=winner;match.loser=match.fighter_two if winner==match.fighter_one else match.fighter_one;match.result_id=result_id;self.processed_result_ids.add(result_id);self._advance(match);return True
    def _advance(self,match):
        main_rounds=2 if len(self.participants)==4 else 3
        if match.round_index==main_rounds-1:
            self.champion=match.winner;self.completed=True;return
        target=next(m for m in self.matches if m.id==f"r{match.round_index+1}-m{match.slot_index//2}")
        if match.slot_index%2==0:target.fighter_one=match.winner
        else:target.fighter_two=match.winner
        if self.third_place and match.round_index==main_rounds-2:
            third=next(m for m in self.matches if m.id=="third-place")
            if match.slot_index%2==0:third.fighter_one=match.loser
            else:third.fighter_two=match.loser
    def to_dict(self):return {"participants":self.participants,"player_id":self.player_id,"seed":self.seed,"third_place":self.third_place,"matches":[asdict(m) for m in self.matches],"processed_result_ids":sorted(self.processed_result_ids),"completed":self.completed,"champion":self.champion}
    @classmethod
    def from_dict(cls,data):return cls(list(data["participants"]),str(data["player_id"]),int(data["seed"]),bool(data.get("third_place",False)),[BracketMatch(**m) for m in data.get("matches",[])],set(data.get("processed_result_ids",[])),bool(data.get("completed",False)),str(data.get("champion","")))
