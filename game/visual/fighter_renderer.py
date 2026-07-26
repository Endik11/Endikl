from __future__ import annotations

import math

import pygame

from .animation_clip import AnimationClip
from .animation_graph import AnimationGraph
from .animation_player import AnimationPlayer
from .character_art import CharacterArtRenderer
from .fighter_visual import FighterVisualState
from ..platform_paths import asset_path
from .pose import BonePose, Pose
from .procedural_rig import build_skeleton
from .shadow_renderer import ShadowRenderer


class FighterRenderer:
    USE_STICKMAN_COMBAT = True
    # These verified renders are visual-only. Combat coordinates still come
    # from the simulation snapshot and remain independent from the artwork.
    COMBAT_RENDER_SPECS = {
        "kael": {"height": 360, "source_facing": 1},
        "sable": {"height": 400, "source_facing": -1},
    }
    REACTION_STATES = frozenset({"HIT_STUN", "BLOCK_STUN", "THROWN", "LAUNCHED", "KNOCKDOWN", "DEFEAT", "DEAD"})

    def __init__(self, registry) -> None:
        self.registry = registry
        self.graph = AnimationGraph()
        self.shadow = ShadowRenderer()
        self.character_art = CharacterArtRenderer()
        self.states: dict[str, FighterVisualState] = {}
        self.combat_renders: dict[tuple[str, str], pygame.Surface | None] = {}
        self.combat_render_variants: dict[tuple[str, str, int], pygame.Surface] = {}

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
        origin = camera.world_to_screen(snap.x, snap.y)
        if getattr(getattr(settings, "video", settings), "shadows", True):
            self.shadow.draw(surface, origin[0], origin[1], int(118 * visual.scale), visual.palette_roles.get("shadow", (0, 0, 0)))
        render_mode = self._combat_render_mode(snap)
        pose = self._combat_pose(state.player.sample(facing=1), snap, state)
        skeleton = build_skeleton(rig)
        if self.USE_STICKMAN_COMBAT:
            transforms = sorted(skeleton.world_transforms(pose, origin, snap.facing, visual.scale).values(), key=lambda item: item.draw_order)
            self.character_art.draw(surface, transforms, visual, snap, origin[1])
            if snap.attack_id:
                self._draw_attack_flash(surface, origin, snap.attack_id, snap.facing, visual.scale)
            self._draw_combat_state_effect(surface, snap, origin, state, render_mode)
            return
        combat_render = self._load_combat_render(snap.fighter_id, render_mode)
        if combat_render is None and render_mode != "idle":
            render_mode = "idle"
            combat_render = self._load_combat_render(snap.fighter_id, render_mode)
        if combat_render is None:
            # Skeleton owns world-space mirroring. Applying facing in the
            # animation clip as well mirrors local offsets twice.
            transforms = sorted(skeleton.world_transforms(pose, origin, snap.facing, visual.scale).values(), key=lambda item: item.draw_order)
            for transform in transforms:
                if transform.id not in visual.attachments and transform.shape in {"cape", "blade"}:
                    continue
                color = visual.palette_roles.get(transform.palette_role, visual.palette_roles.get("primary", (220, 220, 220)))
                self._draw_bone(surface, transform, color)
        else:
            self._draw_combat_render(surface, combat_render, snap, origin, state, render_mode)
        if snap.attack_id:
            self._draw_attack_flash(surface, origin, snap.attack_id, snap.facing, visual.scale)
        self._draw_combat_state_effect(surface, snap, origin, state, render_mode)

    def _combat_pose(self, pose: Pose, snap, state: FighterVisualState) -> Pose:
        """Add combat-specific limb motion to the authored animation clip."""
        bones = dict(pose.bones)
        progress = max(0.0, min(1.0, state.player.frame / 24.0))
        drive = math.sin(progress * math.pi)

        def add(bone_id: str, translation: tuple[float, float], rotation: float) -> None:
            current = pose.bone(bone_id)
            bones[bone_id] = BonePose(
                (current.translation[0] + translation[0], current.translation[1] + translation[1]),
                current.rotation + rotation,
                current.scale,
                current.alpha,
            )

        attack_id = getattr(snap, "attack_id", "")
        state_name = getattr(snap, "state", "IDLE")
        if attack_id:
            if "kick" in attack_id:
                add("right_thigh", (20.0 * drive, -10.0 * drive), -44.0 * drive)
                add("right_shin", (12.0 * drive, -8.0 * drive), 52.0 * drive)
            else:
                add("right_upper_arm", (14.0 * drive, -8.0 * drive), -34.0 * drive)
                add("right_forearm", (20.0 * drive, -12.0 * drive), -58.0 * drive)
                if "special" in attack_id or "super" in attack_id:
                    add("left_forearm", (12.0 * drive, -8.0 * drive), -24.0 * drive)
        elif state_name in {"BLOCK_HIGH", "BLOCK_LOW", "BLOCK_STUN"}:
            add("left_forearm", (14.0, -18.0), -58.0)
            add("right_forearm", (-14.0, -18.0), 58.0)
        elif state_name in self.REACTION_STATES:
            recovery = max(0.0, 1.0 - min(1.0, state.player.frame / 22.0))
            add("torso_upper", (0.0, 16.0 * recovery), 28.0 * recovery)
            add("head", (10.0 * recovery, 8.0 * recovery), 18.0 * recovery)
        return Pose(bones)

    @staticmethod
    def _stickman_end(transform) -> tuple[float, float]:
        radians = math.radians(transform.rotation - 90)
        return (
            transform.x + math.cos(radians) * transform.length,
            transform.y + math.sin(radians) * transform.length,
        )

    @staticmethod
    def _stickman_floor_point(point: tuple[float, float], floor_y: int) -> tuple[int, int]:
        return int(point[0]), min(int(point[1]), int(floor_y))

    def _draw_stickman(self, surface: pygame.Surface, transforms, visual, snap, floor_y: int) -> None:
        roles = visual.palette_roles
        outline = (7, 10, 15)
        primary = roles.get("primary", (220, 220, 220))
        secondary = roles.get("secondary", primary)
        accent = roles.get("accent", (240, 240, 240))
        skin = roles.get("skin", (190, 145, 115))
        for transform in transforms:
            if transform.id == "root":
                continue
            color = roles.get(transform.palette_role, primary)
            if transform.id in {"left_upper_arm", "right_upper_arm", "left_thigh", "right_thigh"}:
                color = primary
            elif transform.id in {"left_forearm", "right_forearm", "left_shin", "right_shin"}:
                color = secondary
            elif transform.id in {"left_hand", "right_hand", "left_foot", "right_foot", "energy_core"}:
                color = accent

            if transform.id == "head":
                center = self._stickman_floor_point((transform.x, transform.y), floor_y - 18)
                radius = max(13, int(transform.thickness * 0.62))
                pygame.draw.circle(surface, outline, center, radius + 4)
                pygame.draw.circle(surface, skin, center, radius)
                facing = 1 if snap.facing >= 0 else -1
                eye = (center[0] + facing * max(4, radius // 2), center[1] - max(2, radius // 4))
                pygame.draw.circle(surface, outline, eye, 2)
                pygame.draw.line(surface, outline, (center[0] + facing * radius // 2, center[1] + 5), (center[0] + facing * radius, center[1] + 3), 2)
                continue
            if transform.id in {"left_foot", "right_foot"}:
                x = int(transform.x)
                y = int(floor_y - 7)
                shoe = pygame.Rect(x - 15, y - 7, 30, 13)
                pygame.draw.ellipse(surface, outline, shoe.inflate(6, 5))
                pygame.draw.ellipse(surface, color, shoe)
                continue
            if transform.id == "pelvis":
                center = self._stickman_floor_point((transform.x, transform.y), floor_y)
                pelvis = pygame.Rect(0, 0, 48, 24)
                pelvis.center = center
                pygame.draw.ellipse(surface, outline, pelvis.inflate(8, 8))
                pygame.draw.ellipse(surface, color, pelvis)
                continue
            if transform.shape == "blade":
                self._draw_blade(surface, transform, accent)
                continue
            if transform.shape == "plate":
                self._draw_plate(surface, transform, secondary)
                continue
            if transform.shape == "ribbon":
                self._draw_ribbon(surface, transform, color)
                continue

            start = self._stickman_floor_point((transform.x, transform.y), floor_y)
            end = self._stickman_floor_point(self._stickman_end(transform), floor_y)
            width = max(5, int(transform.thickness * 0.72))
            if transform.shape in {"circle", "ellipse"}:
                radius = max(5, width // 2 + 2)
                pygame.draw.circle(surface, outline, start, radius + 3)
                pygame.draw.circle(surface, color, start, radius)
            else:
                pygame.draw.line(surface, outline, start, end, width + 7)
                pygame.draw.line(surface, color, start, end, width)
                pygame.draw.circle(surface, outline, start, width // 2 + 3)
                pygame.draw.circle(surface, color, start, width // 2)
                pygame.draw.circle(surface, outline, end, width // 2 + 3)
                pygame.draw.circle(surface, color, end, width // 2)

    @staticmethod
    def _combat_render_mode(snap) -> str:
        state = getattr(snap, "state", "IDLE")
        if getattr(snap, "attack_id", ""):
            return "attack"
        if state in {"BLOCK_HIGH", "BLOCK_LOW", "BLOCK_STUN"}:
            return "block"
        if state in FighterRenderer.REACTION_STATES:
            return "hit"
        return "idle"

    def _load_combat_render(self, fighter_id: str, mode: str = "idle") -> pygame.Surface | None:
        cache_key = (fighter_id, mode)
        if cache_key in self.combat_renders:
            return self.combat_renders[cache_key]
        spec = self.COMBAT_RENDER_SPECS.get(fighter_id)
        if spec is None:
            self.combat_renders[cache_key] = None
            return None
        suffix = "_render.png" if mode == "idle" else f"_{mode}_render.png"
        path = asset_path("fighters", f"{fighter_id}{suffix}")
        try:
            image = pygame.image.load(str(path))
            source_height = max(1, image.get_height())
            target_height = int(spec["height"])
            target_width = max(1, round(image.get_width() * target_height / source_height))
            render = pygame.transform.smoothscale(image, (target_width, target_height))
        except (OSError, pygame.error):
            render = None
        self.combat_renders[cache_key] = render
        return render

    def _draw_combat_render(self, surface: pygame.Surface, render: pygame.Surface, snap, origin: tuple[int, int], state: FighterVisualState, mode: str) -> None:
        facing = 1 if snap.facing >= 0 else -1
        source_facing = int(self.COMBAT_RENDER_SPECS[snap.fighter_id]["source_facing"])
        key = (snap.fighter_id, mode, facing)
        variant = self.combat_render_variants.get(key)
        if variant is None:
            variant = render if facing == source_facing else pygame.transform.flip(render, True, False)
            self.combat_render_variants[key] = variant

        phase = state.player.frame * 0.14 + (0.8 if snap.fighter_id == "sable" else 0.0)
        bob = math.sin(phase) * 1.5
        offset_x = 0
        image = variant
        if mode == "attack":
            # The action render is a real sword/blade pose. The small lunge
            # follows the same attack animation that owns the hitbox.
            bob -= abs(math.sin(phase * 0.7)) * 4.0
            offset_x = facing * int(7 + abs(math.sin(phase * 0.55)) * 8)
        elif mode == "block":
            offset_x = -facing * 3
            bob -= 2
        elif mode == "hit":
            recovery = max(0.0, 1.0 - min(1.0, state.player.frame / 22.0))
            offset_x = -facing * int(12 * recovery)
            bob -= 4 * recovery
            image = pygame.transform.rotozoom(variant, -facing * 5 * recovery, 1.0)
        rect = image.get_rect(midbottom=(int(origin[0] + offset_x), int(origin[1] + bob)))
        surface.blit(image, rect)

    def _draw_combat_state_effect(self, surface: pygame.Surface, snap, origin: tuple[int, int], state: FighterVisualState, mode: str) -> None:
        facing = 1 if snap.facing >= 0 else -1
        phase = state.player.frame * 0.18
        if mode == "block":
            color = (92, 224, 238) if snap.fighter_id == "sable" else (246, 198, 92)
            rect = pygame.Rect(origin[0] - 82, origin[1] - 282, 164, 224)
            pygame.draw.arc(surface, (*color, 210), rect, 0.65 if facing > 0 else 2.5, 2.45 if facing > 0 else 4.3, 5)
            pygame.draw.line(surface, color, (origin[0] + facing * 62, origin[1] - 225), (origin[0] + facing * 86, origin[1] - 250), 3)
        elif mode == "hit":
            impact = (origin[0] + facing * 62, origin[1] - 178)
            for index in range(4):
                angle = phase + index * math.pi / 2
                end = (impact[0] + int(math.cos(angle) * 24), impact[1] + int(math.sin(angle) * 24))
                pygame.draw.line(surface, (255, 105, 91), impact, end, 3)
            pygame.draw.circle(surface, (255, 225, 164), impact, 7, 2)
        elif mode == "attack" and getattr(snap, "state", "") == "ATTACK_ACTIVE":
            # A short active-frame streak makes the generated action pose read
            # as a hitbox window instead of a pose swap.
            trail_color = (255, 132, 68) if snap.fighter_id == "kael" else (86, 232, 255)
            start = (origin[0] + facing * 44, origin[1] - 202)
            end = (origin[0] + facing * 142, origin[1] - 238)
            pygame.draw.line(surface, trail_color, start, end, 4)

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
