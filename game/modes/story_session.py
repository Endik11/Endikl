from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class StorySession:
    story_id:str;fighter_id:str;current_node_id:str;seed:int=1;choices:dict[str,str]=field(default_factory=dict);completed_battles:set[str]=field(default_factory=set);rewards:set[str]=field(default_factory=set);ending_id:str="";completed:bool=False;processed_result_ids:set[str]=field(default_factory=set)
    def node(self,story):
        for chapter in story.chapters:
            for node in chapter.nodes:
                if node.id==self.current_node_id:return node
        raise ValueError(f"Unknown story node: {self.current_node_id}")
    def advance(self,story,choice_id=""):
        node=self.node(story)
        if node.type=="choice":
            choice=next((x for x in node.choices if x.id==choice_id),None)
            if choice is None:raise ValueError(f"Unknown choice: {choice_id}")
            self.choices[node.id]=choice.id;target=choice.next_node_id
        elif node.type=="ending":self.ending_id=node.ending_id;self.completed=True;return
        else:target=node.next_node_id
        if not target:raise ValueError(f"Node has no transition: {node.id}")
        self.current_node_id=target
    def record_battle(self,story,result_id,won):
        if result_id in self.processed_result_ids:return False
        node=self.node(story)
        if node.type!="battle":raise ValueError("Current node is not a battle")
        self.processed_result_ids.add(result_id)
        if won:self.completed_battles.add(node.id);self.advance(story)
        return True
    def claim_reward(self,story):
        node=self.node(story)
        if node.type!="reward" or node.reward is None:return False
        fresh=node.reward.id not in self.rewards;self.rewards.add(node.reward.id);self.advance(story);return fresh
    def to_dict(self):
        data=asdict(self)
        for key in ("completed_battles","rewards","processed_result_ids"):data[key]=sorted(data[key])
        return data
    @classmethod
    def from_dict(cls,data):
        return cls(str(data["story_id"]),str(data["fighter_id"]),str(data["current_node_id"]),int(data.get("seed",1)),dict(data.get("choices",{})),set(data.get("completed_battles",[])),set(data.get("rewards",[])),str(data.get("ending_id","")),bool(data.get("completed",False)),set(data.get("processed_result_ids",[])))
