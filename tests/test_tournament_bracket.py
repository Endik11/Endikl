import pytest
from game.modes.tournament_bracket import build_bracket


def test_four_and_eight_participant_brackets_have_semis_and_final():
    four=build_bracket(list("abcd"),True);eight=build_bracket(list("abcdefgh"))
    assert len(four)==4 and any(m.id=="third-place" for m in four)
    assert len(eight)==7 and sum(m.round_index==1 for m in eight)==2


def test_duplicate_participants_rejected():
    with pytest.raises(ValueError):build_bracket(["a","a","b","c"])
