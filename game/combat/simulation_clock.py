from dataclasses import dataclass
from .constants import FIXED_DT, MAX_FRAME_SKIP

@dataclass(slots=True)
class SimulationClock:
    accumulator: float = 0.0
    skipped_frames: int = 0
    last_steps: int = 0
    def consume(self, real_dt: float) -> int:
        requested=self.accumulator+max(0.0,real_dt)
        if requested>FIXED_DT*MAX_FRAME_SKIP:self.skipped_frames+=max(0,int(requested/FIXED_DT)-MAX_FRAME_SKIP)
        self.accumulator = min(requested, FIXED_DT * MAX_FRAME_SKIP)
        steps = min(int((self.accumulator + 1e-12) / FIXED_DT), MAX_FRAME_SKIP)
        self.accumulator -= steps * FIXED_DT;self.last_steps=steps
        return steps
    @property
    def alpha(self) -> float: return max(0.0, min(1.0, self.accumulator / FIXED_DT))
    def reset(self): self.accumulator=0.0;self.skipped_frames=0;self.last_steps=0
