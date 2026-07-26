from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StoryConditionDefinition: key: str; value: str
@dataclass(frozen=True, slots=True)
class StoryRewardDefinition: id: str; kind: str; value: str
@dataclass(frozen=True, slots=True)
class StoryChoiceDefinition: id: str; text_key: str; next_node_id: str; condition: StoryConditionDefinition | None = None
@dataclass(frozen=True, slots=True)
class StoryNodeDefinition:
    id: str; type: str; next_node_id: str = ""; dialogue_id: str = ""; opponent_id: str = ""; choices: tuple[StoryChoiceDefinition, ...] = (); reward: StoryRewardDefinition | None = None; ending_id: str = ""
@dataclass(frozen=True, slots=True)
class StoryChapterDefinition: id: str; nodes: tuple[StoryNodeDefinition, ...]
@dataclass(frozen=True, slots=True)
class StoryDefinition: id: str; fighter_id: str; start_node_id: str; chapters: tuple[StoryChapterDefinition, ...]
@dataclass(frozen=True, slots=True)
class DialogueNodeDefinition: id: str; speaker_key: str; text_key: str
