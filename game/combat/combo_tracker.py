from dataclasses import dataclass
@dataclass(slots=True)
class ComboTracker:
    hit_count:int=0;total_damage:int=0;start_frame:int=0;last_hit_frame:int=0;attacker_id:str="";victim_id:str="";current_scaling:float=1;juggle_count:int=0;wall_hit_count:int=0
    def add(self,damage,frame,attacker,victim,scaling):
        if not self.hit_count:self.start_frame=frame;self.attacker_id=attacker;self.victim_id=victim
        self.hit_count+=1;self.total_damage+=damage;self.last_hit_frame=frame;self.current_scaling=scaling
    def reset(self):
        self.hit_count=0;self.total_damage=0;self.start_frame=0;self.last_hit_frame=0;self.attacker_id="";self.victim_id="";self.current_scaling=1;self.juggle_count=0;self.wall_hit_count=0
