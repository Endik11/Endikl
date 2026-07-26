from dataclasses import dataclass


@dataclass(slots=True)
class TrainingMetrics:
    combo_damage:int=0;combo_hits:int=0;scaling:float=1.0;attacker_recovery:int=0;defender_stun:int=0
    @property
    def frame_advantage(self):return self.defender_stun-self.attacker_recovery
    def reset_combo(self):self.combo_damage=0;self.combo_hits=0;self.scaling=1.0
