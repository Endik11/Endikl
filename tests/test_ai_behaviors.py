from types import SimpleNamespace
from game.ai.ai_decision import decide
from game.ai import AI_DIFFICULTIES, AIProfile
from game.ai.ai_memory import AIMemory
from game.ai.ai_random import AIRandom


def test_decision_covers_spacing_defense_and_projectiles():
    profile=AIProfile("x",execution_error_probability=0,block_probability=1,projectile_probability=0)
    base=dict(in_corner=False,projectile_incoming=False,opponent_airborne=False,opponent_attacking=False)
    assert decide(SimpleNamespace(distance=500,**base),profile,AI_DIFFICULTIES["medium"],AIRandom(1),AIMemory()).name=="approach"
    assert decide(SimpleNamespace(distance=150,**{**base,"projectile_incoming":True}),profile,AI_DIFFICULTIES["medium"],AIRandom(1),AIMemory()).name.startswith("projectile_")
    assert decide(SimpleNamespace(distance=100,**{**base,"opponent_attacking":True}),profile,AI_DIFFICULTIES["hard"],AIRandom(1),AIMemory()).name.startswith("block_")
