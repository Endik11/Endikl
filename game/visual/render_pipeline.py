from __future__ import annotations

import pygame

from .arena_renderer import ArenaRenderer
from .camera_controller import CameraController
from .effects_manager import EffectsManager
from .fighter_renderer import FighterRenderer
from .hud_renderer import HudRenderer
from .lighting import LightingRenderer
from .projectile_renderer import ProjectileRenderer
from .round_announcer import RoundAnnouncer
from .screen_effects import ScreenEffects
from .transition_renderer import TransitionRenderer


class RenderPipeline:
    def __init__(self, registry, settings=None) -> None:
        self.registry = registry
        self.settings = settings
        self.camera = CameraController()
        self.arena = ArenaRenderer()
        self.fighters = FighterRenderer(registry)
        self.projectiles = ProjectileRenderer()
        self.effects = EffectsManager(registry)
        self.hud = HudRenderer(registry)
        self.announcer = RoundAnnouncer(registry)
        self.lighting = LightingRenderer()
        self.screen_effects = ScreenEffects()
        self.transition = TransitionRenderer()
        self.arena_id = next(iter(registry.arenas), "")

    def set_arena(self, arena_id: str) -> None:
        if arena_id in self.registry.arena_visuals:
            self.arena_id = arena_id

    def handle_events(self, events, settings=None) -> None:
        self.effects.handle_events(events)
        for event in events:
            name = getattr(event.type, "name", str(event.type))
            if name in {"ATTACK_HIT", "PROJECTILE_HIT", "ROUND_ENDED"}:
                self.camera.emphasize(10 if name != "ROUND_ENDED" else 16, settings or self.settings)
                self.screen_effects.flash(60 if name != "ROUND_ENDED" else 90, settings or self.settings)

    def draw(self, surface: pygame.Surface, snapshot, alpha: float = 0.0, world=None, settings=None) -> None:
        settings = settings or self.settings
        arena_id = self.arena_id if self.arena_id in self.registry.arena_visuals else next(iter(self.registry.arena_visuals))
        arena = self.registry.get_arena(arena_id)
        visual = self.registry.arena_visuals[arena_id]
        self.camera.update(snapshot, (arena.left_boundary, arena.right_boundary), 1 / 60, settings)
        surface.fill(visual.palette[0])
        self.arena.draw(surface, visual, self.camera, snapshot.frame_number / 60)
        self.lighting.draw(surface, visual.light_color)
        self.fighters.draw(surface, snapshot, self.camera, hit_stop=bool(getattr(getattr(world, "hit_stop", None), "active", False)), settings=settings)
        self.projectiles.draw(surface, snapshot, self.camera)
        self.effects.update(settings)
        self.effects.draw(surface, self.camera, settings)
        self.hud.draw(surface, snapshot, settings)
        self.announcer.draw(surface, snapshot)
        self.screen_effects.draw(surface)
        self.transition.draw(surface, max(0.0, min(1.0, 1.0 - alpha)) * 0.08)
