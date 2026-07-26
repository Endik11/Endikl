from game.combat.combat_world import CombatWorld
from game.combat.input_buffer import InputFrame
from game.content_registry import get_default_registry
def run(seed):
    r=get_default_registry();w=CombatWorld(r,"kael","sable","neon_foundry",seed);w.fighter_one.x=500;w.fighter_two.x=570
    for i in range(60):w.simulate_frame(InputFrame(light_punch=i==0,pressed=frozenset({"light_punch"}) if i==0 else frozenset(),frame_number=i),InputFrame(frame_number=i))
    return w.snapshot()
def test_same_seed_and_inputs_same_snapshot():assert run(42).digest()==run(42).digest()
