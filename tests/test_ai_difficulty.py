from game.ai import AI_DIFFICULTIES


def test_five_difficulties_improve_reaction_without_stat_bonuses():
    assert list(AI_DIFFICULTIES)==["novice","easy","medium","hard","expert"]
    assert AI_DIFFICULTIES["novice"].reaction_modifier > AI_DIFFICULTIES["expert"].reaction_modifier
    for item in AI_DIFFICULTIES.values():
        assert not hasattr(item,"health") and not hasattr(item,"damage") and not hasattr(item,"speed")
