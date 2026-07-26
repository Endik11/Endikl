from collections import Counter


DEFAULT_STATISTICS={"matches_played":0,"wins":0,"losses":0,"draws":0,"knockouts":0,"double_knockouts":0,"rounds_won":0,"rounds_lost":0,"damage_dealt":0,"damage_received":0,"longest_combo":0,"highest_combo_damage":0,"total_combo_hits":0,"successful_blocks":0,"chip_damage_dealt":0,"throws":0,"throw_techs":0,"projectiles_created":0,"projectiles_hit":0,"projectiles_blocked":0,"projectile_clashes":0,"favorite_fighter":"","fighter_usage":{},"arena_usage":{},"arcade_completions":0,"story_endings":{},"tournament_wins":0,"training_frames":0}


class StatisticsManager:
    def __init__(self,data=None,processed_result_ids=None):self.data={**DEFAULT_STATISTICS,**(data if isinstance(data,dict) else {})};self.processed_result_ids=set(processed_result_ids or ())
    def process(self,stats):
        if stats.result_id in self.processed_result_ids:return False
        self.processed_result_ids.add(stats.result_id);self.data["matches_played"]+=1;self.data[{"win":"wins","loss":"losses"}.get(stats.outcome,"draws")]+=1
        for key in ("knockouts","double_knockouts","rounds_won","rounds_lost","damage_dealt","damage_received","total_combo_hits","successful_blocks","chip_damage_dealt","throws","throw_techs","projectiles_created","projectiles_hit","projectiles_blocked","projectile_clashes"):self.data[key]+=getattr(stats,key)
        self.data["longest_combo"]=max(self.data["longest_combo"],stats.longest_combo);self.data["highest_combo_damage"]=max(self.data["highest_combo_damage"],stats.highest_combo_damage)
        for key,value in (("fighter_usage",stats.fighter_id),("arena_usage",stats.arena_id)):
            mapping=self.data.setdefault(key,{});mapping[value]=mapping.get(value,0)+1
        usage=self.data["fighter_usage"];self.data["favorite_fighter"]=max(usage,key=lambda x:(usage[x],x))
        return True
    def mode_complete(self,mode,value=""):
        if mode=="arcade":self.data["arcade_completions"]+=1
        elif mode=="story":mapping=self.data.setdefault("story_endings",{});mapping[value]=mapping.get(value,0)+1
        elif mode=="tournament":self.data["tournament_wins"]+=1
