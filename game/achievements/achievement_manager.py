from .achievement_progress import AchievementProgress
class AchievementManager:
    def __init__(self,registry,progress=None,unlocked=None,processed_events=None):
        self.registry=registry;self.progress={key:AchievementProgress(**value) if isinstance(value,dict) else AchievementProgress() for key,value in (progress or {}).items() if key in registry.definitions};self.unlocked=set(unlocked or ());self.processed_events=set(processed_events or ())
    def evaluate(self,event_id,statistics,reward=None,toast=None):
        if event_id in self.processed_events:return []
        self.processed_events.add(event_id);fresh=[]
        for definition in self.registry.definitions.values():
            state=self.progress.setdefault(definition.id,AchievementProgress());value=statistics.get(definition.stat_key,0)
            if isinstance(value,dict):value=len(value)
            state.value=max(state.value,int(value or 0))
            if not state.unlocked and state.value>=definition.target:
                state.unlocked=True;self.unlocked.add(definition.id);fresh.append(definition.id)
                if reward:reward(definition.reward_id,definition.reward_points)
                if toast:toast(definition.id)
        return fresh
    def to_dict(self):return {"progress":{key:{"value":v.value,"unlocked":v.unlocked} for key,v in self.progress.items()},"unlocked":sorted(self.unlocked),"processed_events":sorted(self.processed_events)}
