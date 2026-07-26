from game.modes.tournament_session import TournamentSession
from game.modes.tournament_simulation import simulate_ai_match
from game.content_registry import get_default_registry


def test_results_advance_to_final_and_are_idempotent_and_restorable():
    session=TournamentSession(["kael","sable","orrin","mira"],"kael",8,True)
    assert session.record_result("r0-m0","one","kael") and not session.record_result("r0-m0","one","kael")
    assert session.record_result("r0-m1","two","mira");assert session.current_match.id=="r1-m0"
    assert session.record_result("r1-m0","final","kael") and session.completed and session.champion=="kael"
    restored=TournamentSession.from_dict(session.to_dict());assert restored.champion=="kael"


def test_ai_match_is_deterministic():
    registry=get_default_registry();a=simulate_ai_match(registry,"kael","sable","neon_foundry",11,1000);b=simulate_ai_match(registry,"kael","sable","neon_foundry",11,1000)
    assert a==b
