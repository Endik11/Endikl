from game.combat.combat_event import CombatEvent
from game.combat.enums import CombatEventType
from game.match_statistics import MatchStatistics
from game.statistics_manager import StatisticsManager


def test_statistics_derive_from_events_and_result_is_idempotent():
    events=[CombatEvent(1,CombatEventType.ATTACK_HIT,"p1","p2",value=80),CombatEvent(2,CombatEventType.ATTACK_BLOCKED,"p1","p2",value=5),CombatEvent(3,CombatEventType.THROW_CONNECTED,"p1","p2"),CombatEvent(4,CombatEventType.PROJECTILE_CREATED,"p1"),CombatEvent(5,CombatEventType.PROJECTILE_HIT,"p1","p2",value=40)]
    match=MatchStatistics.from_events("result-1","kael","sable","neon_foundry","win",events);manager=StatisticsManager()
    assert manager.process(match) and not manager.process(match);assert manager.data["matches_played"]==1 and manager.data["damage_dealt"]==120 and manager.data["throws"]==1 and manager.data["projectiles_hit"]==1


def test_corrupt_statistics_falls_back_safely():
    manager=StatisticsManager("bad",["one"]);assert manager.data["matches_played"]==0 and "one" in manager.processed_result_ids
