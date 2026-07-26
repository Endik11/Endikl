class RewardManager:
    def __init__(self,received_reward_ids=None,processed_result_ids=None):self.received_reward_ids=set(received_reward_ids or ());self.processed_result_ids=set(processed_result_ids or ())
    def grant(self,reward_id,result_id,profile,kind,value):
        if reward_id in self.received_reward_ids or result_id in self.processed_result_ids:return False
        self.received_reward_ids.add(reward_id);self.processed_result_ids.add(result_id)
        if kind=="currency":profile.currency+=max(0,int(value))
        elif kind=="fighter" and value not in profile.unlocked_fighters:profile.unlocked_fighters.append(value)
        elif kind=="arena" and value not in profile.unlocked_arenas:profile.unlocked_arenas.append(value)
        return True
