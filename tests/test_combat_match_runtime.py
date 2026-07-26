from types import SimpleNamespace
from game.combat.combat_fighter import CombatFighter
from game.combat_match_runtime import CombatMatchRuntime
from game.content_registry import get_default_registry
from game.enums import MatchMode
from game.session import GameSession
from pathlib import Path
class Input:
    def controls_for(self,p):return {}
    def pressed_for(self,p):return {}
class Audio:
    def play_sfx(self,name):pass
def test_runtime_starts_updates_pauses_and_stops_without_legacy_fighter():
    settings=SimpleNamespace(gameplay=SimpleNamespace(round_seconds=99,rounds_to_win=2));runtime=CombatMatchRuntime(get_default_registry(),Input(),Audio(),settings)
    session=GameSession(MatchMode.LOCAL_VS,"kael","sable","neon_foundry");runtime.start_match(session)
    assert isinstance(runtime.world.fighter_one,CombatFighter) and not runtime.uses_legacy_fighter
    runtime.update_match(1/30);assert runtime.world.frame_number==2
    runtime.pause_match();before=runtime.world.frame_number;runtime.update_match(1);assert runtime.world.frame_number==before
    runtime.pause_match();runtime.stop_match();assert runtime.world is None

def test_production_runtime_has_no_legacy_or_callback_construction():
    root=Path(__file__).parents[1];engine=(root/"game"/"engine.py").read_text(encoding="utf-8");runtime=(root/"game"/"combat_match_runtime.py").read_text(encoding="utf-8");adapter=(root/"game"/"match_runtime.py").read_text(encoding="utf-8")
    assert "from .fighter" not in engine and "CallbackMatchRuntime(" not in engine+runtime+adapter
    assert "ComboSystem(" not in engine+runtime and "BASE_ATTACKS" not in engine+runtime
