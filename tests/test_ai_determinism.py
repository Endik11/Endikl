from game.ai import AIController, AIProfile
from game.combat.combat_world import CombatWorld
from game.content_registry import get_default_registry


def test_same_seed_profile_and_snapshots_produce_same_inputs():
    world=CombatWorld(get_default_registry(),"kael","sable","neon_foundry",4);profile=AIProfile("kael",reaction_frames=0)
    left=AIController(profile);right=AIController(profile);left.reset(99);right.reset(99)
    assert [left.build_input(world.snapshot(),"kael",n) for n in range(30)] == [right.build_input(world.snapshot(),"kael",n) for n in range(30)]
