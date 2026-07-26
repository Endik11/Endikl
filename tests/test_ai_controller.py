from game.ai import AIController, AIProfile
from game.combat.input_buffer import InputFrame
from game.combat.combat_world import CombatWorld
from game.content_registry import get_default_registry


def test_ai_returns_input_without_mutating_world():
    registry=get_default_registry();world=CombatWorld(registry,"kael","sable","neon_foundry",7);before=world.snapshot().digest()
    controller=AIController(AIProfile("kael",reaction_frames=0,execution_error_probability=0),"medium",registry.get_fighter("kael").attack_ids)
    frame=controller.build_input(world.snapshot(),"kael",20)
    assert isinstance(frame,InputFrame) and world.snapshot().digest()==before


def test_reaction_delay_produces_neutral_input():
    world=CombatWorld(get_default_registry(),"kael","sable","neon_foundry",1);controller=AIController(AIProfile("kael",reaction_frames=20),"novice")
    assert not controller.build_input(world.snapshot(),"kael",5).held
