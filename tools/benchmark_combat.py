from __future__ import annotations
import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from game.combat.combat_world import CombatWorld
from game.combat.input_buffer import InputFrame
from game.content_registry import get_default_registry
def main():
    r=get_default_registry();ids=list(r.fighters);arena=next(iter(r.arenas));world=CombatWorld(r,ids[0],ids[1],arena,seed=42,round_seconds=999999);start=time.perf_counter()
    for frame in range(10000):world.simulate_frame(InputFrame(right=frame%120<40,frame_number=frame),InputFrame(left=frame%120<40,frame_number=frame))
    elapsed=time.perf_counter()-start;print(f"frames=10000 elapsed={elapsed:.4f}s fps={10000/elapsed:.0f} avg_ms={elapsed*1000/10000:.5f}")
if __name__=="__main__":main()
