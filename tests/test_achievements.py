from pathlib import Path
from game.achievements import AchievementRegistry,AchievementManager
def test_unlock_progress_duplicate_reward_and_toast():
    registry=AchievementRegistry.load(Path("data/achievements.json"));rewards=[];toasts=[];manager=AchievementManager(registry);stats={"matches_played":1,"wins":1}
    fresh=manager.evaluate("event1",stats,lambda rid,points:rewards.append((rid,points)),toasts.append);assert {"first_match","first_win"}<=set(fresh);assert not manager.evaluate("event1",stats);assert len(rewards)==2 and len(toasts)==2
def test_restore_hidden_multistage_and_unknown_data():
    registry=AchievementRegistry.load(Path("data/achievements.json"));manager=AchievementManager(registry,{"combo_ten":{"value":5,"unlocked":False},"missing":{"value":9}});manager.evaluate("two",{"longest_combo":10});assert manager.progress["combo_ten"].unlocked and registry.definitions["combo_ten"].hidden and "missing" not in manager.progress
