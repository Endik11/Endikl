from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]
Point = tuple[float, float]


@dataclass(slots=True, frozen=True)
class BoneDefinition:
    id: str
    parent: str
    local_position: Point
    rotation: float
    scale: Point
    length: float
    thickness: float
    pivot: Point
    shape: str
    draw_order: int
    palette_role: str
    attachment: str = ""


@dataclass(slots=True, frozen=True)
class RigDefinition:
    id: str
    bones: tuple[BoneDefinition, ...]


@dataclass(slots=True, frozen=True)
class FighterVisualDefinition:
    id: str
    fighter_id: str
    rig_id: str
    silhouette: str
    stance: str
    scale: float
    idle_clip: str
    walk_clip: str
    attack_clip: str
    victory_clip: str
    defeat_clip: str
    palette_roles: dict[str, Color]
    attachments: tuple[str, ...]
    effect_style: str


@dataclass(slots=True, frozen=True)
class ArenaVisualDefinition:
    id: str
    arena_id: str
    style: str
    palette: tuple[Color, Color, Color]
    layers: tuple[dict[str, object], ...]
    particle_style: str
    light_color: Color
    shadow_color: Color


@dataclass(slots=True, frozen=True)
class AnimationKeyframeDefinition:
    frame: int
    bone_id: str
    translation: Point
    rotation: float
    scale: Point
    alpha: float = 1.0


@dataclass(slots=True, frozen=True)
class AnimationDefinition:
    id: str
    state: str
    duration_frames: int
    loop: bool
    playback_speed: float
    priority: int
    blend_frames: int
    restart: bool
    freeze_on_hit_stop: bool
    keyframes: tuple[AnimationKeyframeDefinition, ...]
    events: tuple[dict[str, object], ...] = ()


@dataclass(slots=True, frozen=True)
class EffectDefinition:
    id: str
    event: str
    particle_count: int
    lifetime_frames: int
    speed: float
    color: Color
    secondary_color: Color
    radius: float
    pooled: bool = True


@dataclass(slots=True, frozen=True)
class HudDefinition:
    id: str
    health_width: int
    meter_segments: int
    meter_max: int
    font_family: str
    palette: dict[str, Color]
    announcer_keys: dict[str, str]
