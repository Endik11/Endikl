from __future__ import annotations
import sys,time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from game.ai import AIController,AIProfile
from game.combat.combat_world import CombatWorld
from game.content_registry import get_default_registry


def run(seed=1701,frames=10000):
    registry=get_default_registry();world=CombatWorld(registry,"kael","sable","neon_foundry",seed,999,99);controllers=[]
    for index,key in enumerate(("kael","sable")):
        fighter=registry.get_fighter(key);controller=AIController(AIProfile.from_dict(key,fighter.ai_profile),"medium",fighter.attack_ids);controller.reset(seed+index);controllers.append(controller)
    decision_time=0.0;started=time.perf_counter()
    for _ in range(frames):
        snapshot=world.snapshot();tick=time.perf_counter();one=controllers[0].build_input(snapshot,"kael",world.frame_number);two=controllers[1].build_input(snapshot,"sable",world.frame_number);decision_time+=time.perf_counter()-tick;world.simulate_frame(one,two)
    elapsed=time.perf_counter()-started;return world.snapshot().digest(),elapsed,decision_time/(frames*2)


if __name__=="__main__":
    first,elapsed,average=run();second,_,_=run()
    if first!=second:raise SystemExit("AI determinism digest mismatch")
    print(f"frames=10000 elapsed={elapsed:.4f}s simulation_fps={10000/elapsed:.0f} avg_decision_ms={average*1000:.5f} digest={first[:16]}")
