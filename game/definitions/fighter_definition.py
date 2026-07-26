from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]


@dataclass(slots=True, frozen=True)
class FighterDefinition:
    id: str
    name: str
    title: str
    biography: str
    archetype: str
    max_health: int
    walk_speed: float
    back_walk_speed: float
    air_speed: float
    jump_velocity: float
    weight: float
    defense: float
    difficulty: int
    palette: tuple[Color, Color, Color]
    portrait: str
    sprite_sheet: str
    procedural_model: dict[str, object]
    attack_ids: tuple[str, ...]
    combo_ids: tuple[str, ...]
    special_ids: tuple[str, ...]
    super_attack_id: str
    victory_animation: str
    defeat_animation: str
    ai_profile: dict[str, object]
    unlocked_by_default: bool

    # Compatibility properties consumed by the Stage 2 runtime and renderer.
    @property
    def key(self) -> str:
        return self.id

    @property
    def speed(self) -> float:
        return self.walk_speed

    @property
    def jump_speed(self) -> float:
        return self.jump_velocity

    @property
    def story(self) -> str:
        return self.biography
