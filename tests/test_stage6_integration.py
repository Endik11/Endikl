from game.ai import AIController
from game.combat_match_runtime import CombatMatchRuntime
from game.content_registry import get_default_registry
from game.enums import GameState,MatchMode
from game.session import GameSession
from types import SimpleNamespace
from game.reward_manager import RewardManager
from game.save import ProfileData


class Input:
    def controls_for(self,p):return {}
    def pressed_for(self,p):return {}
class Audio:
    def play_sfx(self,n):pass


def test_production_runtime_builds_new_ai_controller():
    settings=SimpleNamespace(gameplay=SimpleNamespace(round_seconds=99,rounds_to_win=2));runtime=CombatMatchRuntime(get_default_registry(),Input(),Audio(),settings)
    session=GameSession(MatchMode.ARCADE,"kael","sable","neon_foundry",controller_types={"p1":"human","p2":"ai"});runtime.start_match(session)
    assert isinstance(runtime.controllers["p2"],AIController)


def test_stage6_states_are_typed_and_distinct():
    assert GameState.ARCADE_LADDER is not GameState.STORY_PROGRESS and GameState.STORY_PROGRESS is not GameState.TOURNAMENT_BRACKET


def test_result_reward_cannot_be_reissued_by_reopening_result():
    profile=ProfileData();manager=RewardManager();assert manager.grant("arcade_complete","stable-result",profile,"currency",500)
    assert not manager.grant("arcade_complete","stable-result",profile,"currency",500) and profile.currency==500
