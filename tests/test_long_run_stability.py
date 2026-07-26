from game.combat.combat_world import CombatWorld
from game.combat.input_buffer import InputFrame
from game.content_registry import get_default_registry
def test_ten_thousand_frames_and_one_hundred_match_constructions():
    registry=get_default_registry();world=CombatWorld(registry,"kael","sable","neon_foundry",99,9999,99);neutral=InputFrame()
    for _ in range(10000):world.simulate_frame(neutral,neutral)
    assert world.frame_number==10000
    assert len({CombatWorld(registry,"kael","sable","neon_foundry",seed).snapshot().digest() for seed in range(100)})==100
