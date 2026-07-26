from __future__ import annotations

import shutil
from dataclasses import fields
from pathlib import Path
from types import SimpleNamespace

import pygame

from game.combat.combat_event import CombatEvent
from game.combat.combat_world import CombatWorld
from game.combat.enums import CombatEventType
from game.combat_renderer import CombatRenderer
from game.content_registry import ContentRegistry
from game.settings import ROOT_DIR
from game.visual.animation_clip import AnimationClip
from game.visual.animation_graph import AnimationGraph
from game.visual.animation_player import AnimationPlayer
from game.visual.camera_controller import CameraController
from game.visual.effects_manager import EffectsManager
from game.visual.fighter_renderer import FighterRenderer
from game.visual.hud_renderer import HudRenderer
from game.visual.lighting import LightingRenderer
from game.visual.particle_system import ParticleSystem
from game.visual.screen_effects import ScreenEffects
from game.visual.skeleton import Skeleton
from game.visual.visual_constants import MAX_SHAKE_PIXELS


def registry() -> ContentRegistry:
    content = ContentRegistry(ROOT_DIR / "data", allow_fallback=False)
    content.load_all()
    return content


def copy_data(tmp_path: Path) -> Path:
    target = tmp_path / "data"
    shutil.copytree(ROOT_DIR / "data", target)
    return target


def test_visual_definitions_load_without_surfaces() -> None:
    content = registry()
    assert len(content.fighter_visuals) == len(content.fighters) == 6
    assert len(content.arena_visuals) == len(content.arenas) == 6
    assert "default_humanoid" in content.rigs
    assert content.hud is not None and content.hud.meter_segments == 3
    assert not any(isinstance(getattr(visual, field.name), pygame.Surface) for visual in content.fighter_visuals.values() for field in fields(visual))


def test_missing_visual_files_use_generated_fallback(tmp_path: Path) -> None:
    data = copy_data(tmp_path)
    (data / "visuals.json").unlink()
    content = ContentRegistry(data, allow_fallback=False)
    content.load_all()
    assert content.fighter_visuals.keys() == content.fighters.keys()
    assert content.arena_visuals.keys() == content.arenas.keys()


def test_invalid_visual_reload_retains_previous_content(tmp_path: Path) -> None:
    data = copy_data(tmp_path)
    content = ContentRegistry(data, allow_fallback=False)
    content.load_all()
    before = content.fighter_visuals
    (data / "visuals.json").write_text('{"fighters":[],"rigs":[],"arenas":[]}', encoding="utf-8")
    assert not content.reload()
    assert content.fighter_visuals is before
    assert "kael" in content.fighter_visuals


def test_animation_interpolation_graph_hit_stop_and_facing_flip() -> None:
    content = registry()
    idle = AnimationClip(content.animations["idle"])
    halfway = idle.sample(13.5).bone("torso_upper")
    assert -2 < halfway.rotation < 2
    attack = AnimationClip(content.animations["strike_flash"])
    forward = attack.sample(8, facing=1).bone("right_forearm")
    flipped = attack.sample(8, facing=-1).bone("right_forearm")
    assert forward.translation[0] > 0 and flipped.translation[0] < 0
    player = AnimationPlayer({"idle": idle})
    player.update(5, hit_stop=True)
    assert player.frame == 0
    visual = content.fighter_visuals["kael"]
    snap = SimpleNamespace(state="IDLE", attack_id="")
    assert AnimationGraph().clip_for_snapshot(visual, snap) == "idle"
    snap.attack_id = "light_punch"
    assert AnimationGraph().clip_for_snapshot(visual, snap) == "strike_flash"


def test_rig_hierarchy_computes_child_world_transform() -> None:
    content = registry()
    rig = content.rigs["default_humanoid"]
    transforms = Skeleton(rig).world_transforms(AnimationClip(content.animations["idle"]).sample(0), (640, 584))
    assert transforms["torso_upper"].y < transforms["pelvis"].y < 584
    assert transforms["right_hand"].x > transforms["left_hand"].x


def test_camera_boundaries_smoothing_shake_and_reduced_motion() -> None:
    camera = CameraController(x=0)
    snap = SimpleNamespace(
        fighter_one=SimpleNamespace(x=350, y=584),
        fighter_two=SimpleNamespace(x=930, y=584),
    )
    settings = SimpleNamespace(video=SimpleNamespace(dynamic_zoom=True, reduced_motion=False, camera_shake=True))
    camera.update(snap, (70, 1210), 1 / 60, settings)
    half_width = (1280 / camera.zoom) * 0.5
    assert camera.x >= 70 + half_width
    camera.emphasize(999, settings)
    assert camera.shake <= MAX_SHAKE_PIXELS
    reduced = SimpleNamespace(video=SimpleNamespace(dynamic_zoom=True, reduced_motion=True, camera_shake=True))
    camera.shake = 0
    camera.emphasize(12, reduced)
    assert camera.shake < 12


def test_hud_health_meter_segments_and_font_cache() -> None:
    pygame.font.init()
    hud = HudRenderer(registry())
    assert hud.font(18) is hud.font(18)
    assert hud.health_view("kael", 1000) == 1000
    smoothed = hud.health_view("kael", 500)
    assert 500 < smoothed < 1000
    assert hud.meter_segments(1500) == (1.0, 0.5, 0.0)


def test_particle_pooling_and_combat_event_effect_mapping() -> None:
    content = registry()
    particles = ParticleSystem(pool_size=4)
    particles.emit(100, 100, content.effects["light_hit_spark"])
    assert particles.active_count() == 4
    manager = EffectsManager(content)
    event = CombatEvent(1, CombatEventType.ATTACK_HIT, position=(300, 420))
    manager.handle_events([event])
    assert manager.particles.active_count() > 0
    assert manager.last_events == ["ATTACK_HIT"]


def test_reduced_flashes_disable_screen_flash() -> None:
    effects = ScreenEffects()
    settings = SimpleNamespace(video=SimpleNamespace(flashes=True, reduced_flashes=True))
    effects.flash(100, settings)
    assert effects.flash_alpha == 0


def test_lighting_overlay_preserves_scene_contrast() -> None:
    pygame.init()
    surface = pygame.Surface((32, 32))
    surface.fill((10, 10, 10))
    LightingRenderer().draw(surface, (255, 255, 255))
    color = surface.get_at((0, 0))
    assert color.r < 80 and color.g < 80 and color.b < 80


def test_verified_combat_renders_load_and_draw_over_procedural_fallback() -> None:
    pygame.init()
    content = registry()
    renderer = FighterRenderer(content)
    kael = renderer._load_combat_render("kael")
    sable = renderer._load_combat_render("sable")
    kael_attack = renderer._load_combat_render("kael", "attack")
    sable_attack = renderer._load_combat_render("sable", "attack")
    assert kael is not None and sable is not None and kael_attack is not None and sable_attack is not None
    assert kael.get_flags() & pygame.SRCALPHA
    assert sable.get_flags() & pygame.SRCALPHA
    assert renderer._combat_render_mode(SimpleNamespace(state="ATTACK_ACTIVE", attack_id="light_punch")) == "attack"
    assert renderer._combat_render_mode(SimpleNamespace(state="BLOCK_HIGH", attack_id="")) == "block"
    assert renderer._combat_render_mode(SimpleNamespace(state="HIT_STUN", attack_id="")) == "hit"
    surface = pygame.Surface((1280, 720), pygame.SRCALPHA)
    surface.fill((8, 10, 16, 255))
    world = CombatWorld(content, "kael", "sable", "neon_foundry")
    renderer.draw(surface, world.snapshot(), CameraController())
    assert surface.get_at((350, 405)).a > 0


def test_combat_renderer_is_headless_and_does_not_mutate_world() -> None:
    pygame.init()
    content = registry()
    world = CombatWorld(content, "kael", "sable", "neon_foundry")
    before = world.snapshot().digest()
    surface = pygame.Surface((1280, 720))
    renderer = CombatRenderer(content, SimpleNamespace(video=SimpleNamespace(
        dynamic_zoom=True,
        reduced_motion=False,
        camera_shake=True,
        shadows=True,
        particles=True,
        trails=True,
        flashes=True,
        reduced_flashes=False,
        ui_scale=1.0,
    )))
    renderer.set_arena("neon_foundry")
    renderer.draw(surface, world.snapshot(), 1.0, world)
    assert world.snapshot().digest() == before
    assert surface.get_at((10, 10)) != pygame.Color(0, 0, 0, 255)
