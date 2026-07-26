from __future__ import annotations

import math

import pygame

from .animation_clip import AnimationClip
from .animation_graph import AnimationGraph
from .animation_player import AnimationPlayer
from .fighter_visual import FighterVisualState
from ..platform_paths import asset_path
from .procedural_rig import build_skeleton
from .shadow_renderer import ShadowRenderer


class FighterRenderer:
    # These verified renders are visual-only. Combat coordinates still come
    # from the simulation snapshot and remain independent from the artwork.
    COMBAT_RENDER_SPECS = {
        "kael": {"height": 360, "source_facing": 1},
        "sable": {"height": 400, "source_facing": -1},
    }

    def __init__(self, registry) -> None:
        self.registry = registry
        self.graph = AnimationGraph()
        self.shadow = ShadowRenderer()
        self.states: dict[str, FighterVisualState] = {}
        self.combat_renders: dict[str, pygame.Surface | None] = {}
        self.combat_render_variants: dict[tuple[str, int], pygame.Surface] = {}

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
        # Skeleton owns world-space mirroring. Applying facing in the animation
        # clip as well mirrors local offsets twice and tears the silhouette apart.
        pose = state.player.sample(facing=1)
        skeleton = build_skeleton(rig)
        origin = camera.world_to_screen(snap.x, snap.y)
        if getattr(getattr(settings, "video", settings), "shadows", True):
            self.shadow.draw(surface, origin[0], origin[1], int(118 * visual.scale), visual.palette_roles.get("shadow", (0, 0, 0)))
        combat_render = self._load_combat_render(snap.fighter_id)
        if combat_render is None:
            transforms = sorted(skeleton.world_transforms(pose, origin, snap.facing, visual.scale).values(), key=lambda item: item.draw_order)
            for transform in transforms:
                if transform.id not in visual.attachments and transform.shape in {"cape", "blade"}:
                    continue
                color = visual.palette_roles.get(transform.palette_role, visual.palette_roles.get("primary", (220, 220, 220)))
                self._draw_bone(surface, transform, color)
        else:
            self._draw_combat_render(surface, combat_render, snap, origin, state)
        if snap.attack_id:
            self._draw_attack_flash(surface, origin, snap.attack_id, snap.facing, visual.scale)

    def _load_combat_render(self, fighter_id: str) -> pygame.Surface | None:
        if fighter_id in self.combat_renders:
            return self.combat_renders[fighter_id]
        spec = self.COMBAT_RENDER_SPECS.get(fighter_id)
        if spec is None:
            self.combat_renders[fighter_id] = None
            return None
        path = asset_path("fighters", f"{fighter_id}_render.png")
        try:
            image = pygame.image.load(path)
            source_height = max(1, image.get_height())
            target_height = int(spec["height"])
            target_width = max(1, round(image.get_width() * target_height / source_height))
            render = pygame.transform.smoothscale(image, (target_width, target_height))
        except (OSError, pygame.error):
            render = None
        self.combat_renders[fighter_id] = render
        return render

    def _draw_combat_render(self, surface: pygame.Surface, render: pygame.Surface, snap, origin: tuple[int, int], state: FighterVisualState) -> None:
        facing = 1 if snap.facing >= 0 else -1
        source_facing = int(self.COMBAT_RENDER_SPECS[snap.fighter_id]["source_facing"])
        key = (snap.fighter_id, facing)
        variant = self.combat_render_variants.get(key)
        if variant is None:
            variant = render if facing == source_facing else pygame.transform.flip(render, True, False)
            self.combat_render_variants[key] = variant

        # Keep a little motion in the static concept render while the real
        # animation graph continues to drive the procedural fallback.
        phase = state.player.frame * 0.14 + (0.8 if snap.fighter_id == "sable" else 0.0)
        bob = math.sin(phase) * 1.5
        if snap.attack_id:
            bob -= abs(math.sin(phase * 0.7)) * 3.0
        offset_x = facing * (4 if snap.attack_id else 0)
        rect = variant.get_rect(midbottom=(int(origin[0] + offset_x), int(origin[1] + bob)))
        surface.blit(variant, rect)

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
            self._draw_plate(surface, transform, color)
        elif transform.shape == "blade":
            self._draw_blade(surface, transform, color)
        elif transform.shape == "ribbon":
            self._draw_ribbon(surface, transform, color)
        else:
            pygame.draw.line(surface, color, (int(transform.x), int(transform.y)), (int(end[0]), int(end[1])), width)
            pygame.draw.circle(surface, color, (int(transform.x), int(transform.y)), max(2, width // 2))
            pygame.draw.circle(surface, color, (int(end[0]), int(end[1])), max(2, width // 2))

    def _draw_plate(self, surface: pygame.Surface, transform, color) -> None:
        angle = math.radians(transform.rotation - 90)
        direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        normal = pygame.Vector2(-direction.y, direction.x)
        center = pygame.Vector2(transform.x, transform.y)
        half_length = max(4.0, transform.length * 0.5)
        half_width = max(4.0, transform.thickness * 0.5)
        points = [center - direction * half_length - normal * half_width,
                  center + direction * half_length - normal * half_width,
                  center + direction * half_length + normal * half_width,
                  center - direction * half_length + normal * half_width]
        pygame.draw.polygon(surface, color, [(int(point.x), int(point.y)) for point in points])

    def _draw_blade(self, surface: pygame.Surface, transform, color) -> None:
        angle = math.radians(transform.rotation - 90)
        direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        normal = pygame.Vector2(-direction.y, direction.x)
        start = pygame.Vector2(transform.x, transform.y)
        base = start + direction * max(4.0, transform.length * 0.18)
        tip = start + direction * transform.length
        width = max(3.0, transform.thickness * 1.8)
        points = [start - normal * width, start + normal * width, tip, base + normal * width * 0.35, base - normal * width * 0.35]
        pygame.draw.polygon(surface, color, [(int(point.x), int(point.y)) for point in points])

    def _draw_ribbon(self, surface: pygame.Surface, transform, color) -> None:
        angle = math.radians(transform.rotation - 90)
        direction = pygame.Vector2(math.cos(angle), math.sin(angle))
        normal = pygame.Vector2(-direction.y, direction.x)
        start = pygame.Vector2(transform.x, transform.y)
        end = start + direction * transform.length
        width = max(2.0, transform.thickness * 0.65)
        points = [start - normal * width, start + normal * width, end + normal * width * 0.35, end, end - normal * width * 0.35]
        pygame.draw.polygon(surface, color, [(int(point.x), int(point.y)) for point in points])

    def _draw_attack_flash(self, surface: pygame.Surface, origin: tuple[int, int], attack_id: str, facing: int, scale: float) -> None:
        seed = sum(ord(char) for char in attack_id)
        color = (120 + seed % 120, 80 + (seed * 3) % 150, 100 + (seed * 7) % 140)
        reach = int((58 + seed % 42) * scale)
        height = int((24 + seed % 18) * scale)
        center = (origin[0] + facing * reach, origin[1] - int(122 * scale))
        rect = pygame.Rect(0, 0, reach, height)
        rect.center = center
        pygame.draw.arc(surface, color, rect, -0.9 if facing > 0 else 2.2, 0.9 if facing > 0 else 4.1, max(3, int(5 * scale)))
