from __future__ import annotations

import math

import pygame

from .animation_clip import AnimationClip
from .animation_graph import AnimationGraph
from .animation_player import AnimationPlayer
from .fighter_visual import FighterVisualState
from .procedural_rig import build_skeleton
from .shadow_renderer import ShadowRenderer


class FighterRenderer:
    def __init__(self, registry) -> None:
        self.registry = registry
        self.graph = AnimationGraph()
        self.shadow = ShadowRenderer()
        self.states: dict[str, FighterVisualState] = {}

    def draw(self, surface: pygame.Surface, snapshot, camera, *, hit_stop: bool = False, settings=None) -> None:
        for fighter in (snapshot.fighter_one, snapshot.fighter_two):
            self._draw_fighter(surface, fighter, camera, hit_stop=hit_stop, settings=settings)

    def _state(self, fighter_id: str) -> FighterVisualState:
        state = self.states.get(fighter_id)
        if state is None:
            clips = {clip_id: AnimationClip(defn) for clip_id, defn in self.registry.animations.items()}
            state = FighterVisualState(fighter_id, AnimationPlayer(clips))
            self.states[fighter_id] = state
        return state

    def _draw_fighter(self, surface: pygame.Surface, snap, camera, *, hit_stop: bool, settings) -> None:
        visual = self.registry.fighter_visuals[snap.fighter_id]
        rig = self.registry.rigs[visual.rig_id]
        state = self._state(snap.fighter_id)
        state.player.play(self.graph.clip_for_snapshot(visual, snap))
        state.player.update(1, hit_stop=hit_stop)
        pose = state.player.sample(facing=snap.facing)
        skeleton = build_skeleton(rig)
        origin = camera.world_to_screen(snap.x, snap.y)
        if getattr(getattr(settings, "video", settings), "shadows", True):
            self.shadow.draw(surface, origin[0], origin[1], int(118 * visual.scale), visual.palette_roles.get("shadow", (0, 0, 0)))
        transforms = sorted(skeleton.world_transforms(pose, origin, snap.facing, visual.scale).values(), key=lambda item: item.draw_order)
        for transform in transforms:
            if transform.id not in visual.attachments and transform.shape in {"cape", "blade"}:
                continue
            color = visual.palette_roles.get(transform.palette_role, visual.palette_roles.get("primary", (220, 220, 220)))
            self._draw_bone(surface, transform, color)

    def _draw_bone(self, surface: pygame.Surface, transform, color) -> None:
        if transform.thickness <= 0 and transform.length <= 0:
            return
        radians = math.radians(transform.rotation - 90)
        end = (
            transform.x + math.cos(radians) * transform.length,
            transform.y + math.sin(radians) * transform.length,
        )
        width = max(2, int(transform.thickness))
        if transform.shape in {"circle", "ellipse"}:
            rect = pygame.Rect(0, 0, max(width, int(transform.length)), width)
            rect.center = (int(transform.x), int(transform.y))
            pygame.draw.ellipse(surface, color, rect)
        elif transform.shape == "plate":
            rect = pygame.Rect(0, 0, max(8, int(transform.length)), max(8, width))
            rect.center = (int(transform.x), int(transform.y))
            pygame.draw.rect(surface, color, rect, border_radius=4)
        else:
            pygame.draw.line(surface, color, (int(transform.x), int(transform.y)), (int(end[0]), int(end[1])), width)
            pygame.draw.circle(surface, color, (int(end[0]), int(end[1])), max(2, width // 2))
