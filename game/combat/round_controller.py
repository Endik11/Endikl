from dataclasses import dataclass
from ..enums import RoundPhase
@dataclass(slots=True)
class RoundController:
    timer_frames:int;round_number:int=1;wins_one:int=0;wins_two:int=0;rounds_to_win:int=2;maximum_draw_retries:int=2;draw_retries:int=0;sudden_death_active:bool=False;phase:RoundPhase=RoundPhase.FIGHT;result:str=""
    def tick(self):
        if self.phase in {RoundPhase.FIGHT,RoundPhase.SUDDEN_DEATH}:self.timer_frames=max(0,self.timer_frames-1)
    def evaluate(self,h1,h2):
        if self.phase not in {RoundPhase.FIGHT,RoundPhase.SUDDEN_DEATH}:return self.result
        if h1<=0 and h2<=0:return self._draw(True)
        winner=1 if h2<=0 else 2 if h1<=0 else 0
        if not winner and self.timer_frames==0:
            if h1==h2:return self._draw(False)
            winner=1 if h1>h2 else 2
        if winner:
            if winner==1:self.wins_one+=1
            else:self.wins_two+=1
            self.result=f"PLAYER_{winner}";self.phase=RoundPhase.MATCH_OVER if max(self.wins_one,self.wins_two)>=self.rounds_to_win else RoundPhase.ROUND_OVER
        return self.result
    def _draw(self,double):
        self.result="DOUBLE_KO" if double else "DRAW";self.phase=RoundPhase.DOUBLE_KO if double else RoundPhase.DRAW;self.draw_retries+=1
        if self.draw_retries>self.maximum_draw_retries:self.sudden_death_active=True;self.phase=RoundPhase.SUDDEN_DEATH
        return self.result
    def begin_next_round(self,timer_frames):
        self.round_number+=1;self.timer_frames=timer_frames;self.result=""
        self.phase=RoundPhase.SUDDEN_DEATH if self.sudden_death_active else RoundPhase.FIGHT
