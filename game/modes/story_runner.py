from __future__ import annotations
import json
from pathlib import Path
from ..definitions.story_definition import *


class StoryRegistry:
    def __init__(self, data_dir: Path): self.data_dir=data_dir;self.stories={};self.dialogues={}
    def load(self, fighter_ids: set[str]) -> None:
        raw=json.loads((self.data_dir/"stories.json").read_text(encoding="utf-8"));dialogs=json.loads((self.data_dir/"dialogues.json").read_text(encoding="utf-8"))
        self.dialogues={row["id"]:DialogueNodeDefinition(row["id"],row["speaker_key"],row["text_key"]) for row in dialogs["dialogues"]}
        built={}
        for row in raw["stories"]:
            chapters=[]
            for chapter in row["chapters"]:
                nodes=[]
                for item in chapter["nodes"]:
                    choices=tuple(StoryChoiceDefinition(c["id"],c["text_key"],c["next_node_id"]) for c in item.get("choices",[]))
                    reward=StoryRewardDefinition(**item["reward"]) if item.get("reward") else None
                    nodes.append(StoryNodeDefinition(item["id"],item["type"],item.get("next_node_id",""),item.get("dialogue_id",""),item.get("opponent_id",""),choices,reward,item.get("ending_id","")))
                chapters.append(StoryChapterDefinition(chapter["id"],tuple(nodes)))
            story=StoryDefinition(row["id"],row["fighter_id"],row["start_node_id"],tuple(chapters));self._validate(story,fighter_ids);built[story.id]=story
        self.stories=built
    def _validate(self, story, fighter_ids):
        nodes={node.id:node for chapter in story.chapters for node in chapter.nodes}
        if story.start_node_id not in nodes: raise ValueError(f"Unknown start node: {story.start_node_id}")
        for node in nodes.values():
            targets=[node.next_node_id,*[choice.next_node_id for choice in node.choices]]
            if any(target and target not in nodes for target in targets): raise ValueError(f"Unknown story node from {node.id}")
            if node.type=="battle" and node.opponent_id not in fighter_ids: raise ValueError(f"Unknown battle fighter: {node.opponent_id}")
            if node.dialogue_id and node.dialogue_id not in self.dialogues: raise ValueError(f"Unknown dialogue: {node.dialogue_id}")
    def for_fighter(self,fighter_id): return next((s for s in self.stories.values() if s.fighter_id==fighter_id),self.stories["fallback"])
