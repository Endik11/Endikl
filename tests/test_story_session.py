from pathlib import Path
from game.modes.story_runner import StoryRegistry
from game.modes.story_session import StorySession


def make():
    registry=StoryRegistry(Path("data"));registry.load({"kael","sable","orrin","mira","lin","ren_kaido"});story=registry.stories["ren_storm_archive"];return story,StorySession(story.id,"ren_kaido",story.start_node_id)


def test_dialogue_choice_battles_reward_endings_and_restore():
    story,session=make();session.advance(story);assert session.record_battle(story,"r1",True);session.advance(story,"seal")
    session.record_battle(story,"r2",True);session.record_battle(story,"r3",True);assert session.claim_reward(story) and not session.claim_reward(story)
    session.advance(story);assert session.completed and session.ending_id=="archive_sealed"
    restored=StorySession.from_dict(session.to_dict());assert restored.ending_id==session.ending_id


def test_duplicate_battle_result_and_unknown_nodes_are_rejected():
    story,session=make();session.advance(story);assert session.record_battle(story,"same",True) and not session.record_battle(story,"same",True)
    session.current_node_id="missing"
    try:session.node(story)
    except ValueError:pass
    else:assert False
