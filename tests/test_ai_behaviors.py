from types import SimpleNamespace
from game.ai.ai_decision import decide
from game.ai import AI_DIFFICULTIES, AIProfile
from game.ai.ai_memory import AIMemory
from game.ai.ai_random import AIRandom


def test_decision_covers_spacing_defense_and_projectiles():
    profile=AIProfile("x",execution_error_probability=0,block_probability=1,projectile_probability=0)
    base=dict(in_corner=False,projectile_incoming=False,opponent_airborne=False,opponent_attacking=False,own_state="IDLE",opponent_state="IDLE",own_meter=0)
    assert decide(SimpleNamespace(distance=500,**base),profile,AI_DIFFICULTIES["medium"],AIRandom(1),AIMemory()).name=="approach"
    assert decide(SimpleNamespace(distance=150,**{**base,"projectile_incoming":True}),profile,AI_DIFFICULTIES["medium"],AIRandom(1),AIMemory()).name.startswith("projectile_")
    assert decide(SimpleNamespace(distance=100,**{**base,"opponent_attacking":True}),profile,AI_DIFFICULTIES["hard"],AIRandom(1),AIMemory()).name.startswith("block_")


def test_visible_state_enables_punish_throw_tech_wakeup_and_meter_actions():
    difficulty=AI_DIFFICULTIES["expert"];memory=AIMemory();base=dict(distance=120,in_corner=False,projectile_incoming=False,opponent_airborne=False,opponent_attacking=False,own_state="IDLE",opponent_state="IDLE",own_meter=0)
    profile=AIProfile("x",punish_probability=1,throw_tech_probability=1,meter_usage=1,execution_error_probability=0)
    assert decide(SimpleNamespace(**{**base,"opponent_state":"ATTACK_RECOVERY"}),profile,difficulty,AIRandom(1),memory).name=="punish"
    assert decide(SimpleNamespace(**{**base,"opponent_state":"THROW_STARTUP"}),profile,difficulty,AIRandom(1),memory).name=="throw_tech"
    assert decide(SimpleNamespace(**{**base,"own_state":"WAKE_UP"}),profile,difficulty,AIRandom(1),memory).name=="wake_up_block"
    meter_view=SimpleNamespace(**{**base,"distance":profile.preferred_distance,"own_meter":1000})
    assert decide(meter_view,profile,difficulty,AIRandom(1),memory).name in {"super","meter_special"}
