from pathlib import Path
from game.modes.story_runner import StoryRegistry


def test_story_data_loads_and_has_individual_and_fallback_paths():
    registry=StoryRegistry(Path("data"));registry.load({"kael","sable","orrin","mira","lin","ren_kaido"})
    assert registry.for_fighter("ren_kaido").id=="ren_storm_archive" and registry.for_fighter("lin").id=="fallback"
    for key in ("ren_storm_archive","kael_ember_oath"):
        story=registry.stories[key];nodes=[n for c in story.chapters for n in c.nodes]
        assert len([n for n in nodes if n.type=="battle"])>=3 and len([n for n in nodes if n.type=="ending"])>=2
