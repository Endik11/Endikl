from game.reward_manager import RewardManager
from game.save import ProfileData


def test_rewards_are_idempotent_for_reward_and_result_ids():
    profile=ProfileData();manager=RewardManager();assert manager.grant("reward-1","result-1",profile,"currency",100)
    assert not manager.grant("reward-1","result-2",profile,"currency",100) and not manager.grant("reward-2","result-1",profile,"currency",100) and profile.currency==100


def test_unlock_rewards_are_unique_and_restore_sets():
    profile=ProfileData();manager=RewardManager(["old"],["done"]);assert manager.grant("new","fresh",profile,"fighter","orrin") and profile.unlocked_fighters.count("orrin")==1
