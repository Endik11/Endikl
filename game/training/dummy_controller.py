from ..combat.input_buffer import InputFrame
from ..ai.ai_random import AIRandom


class TrainingDummyController:
    def __init__(self,behavior="standing",recorder=None,seed=1):self.behavior=behavior;self.recorder=recorder;self.rng=AIRandom(seed);self._last_random=False
    def reset(self,seed):self.rng.reset(seed);self._last_random=False
    def build_input(self,snapshot,fighter_id,frame_number):
        own=snapshot.fighter_one if snapshot.fighter_one.fighter_id==fighter_id else snapshot.fighter_two
        if self.behavior=="recording" and self.recorder:return self.recorder.build_input(frame_number,own.facing)
        held=set()
        if self.behavior in {"crouching","block_low"}:held.add("down")
        if self.behavior in {"always_block","block_high","block_low"}:held.add("block")
        if self.behavior=="random_block":
            if frame_number%30==0:self._last_random=self.rng.chance(.5)
            if self._last_random:held.add("block")
        if self.behavior=="jump" and frame_number%90==0:held.add("up")
        if self.behavior=="repeat_attack" and frame_number%45==0:held.add("light_punch")
        return InputFrame(**{key:key in held for key in ("left","right","up","down","light_punch","heavy_punch","light_kick","heavy_kick","block","throw","special")},pressed=frozenset(held),held=frozenset(held),frame_number=frame_number)
