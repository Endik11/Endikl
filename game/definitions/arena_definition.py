from __future__ import annotations

from dataclasses import dataclass


Color = tuple[int, int, int]


@dataclass(slots=True, frozen=True)
class ArenaDefinition:
    id: str
    name_key: str
    description_key: str
    preview: str
    background_layers: tuple[str, ...]
    ground_y: float
    left_boundary: float
    right_boundary: float
    music: str
    ambience: str
    hazards_enabled_by_default: bool
    procedural_style: str
    unlocked_by_default: bool
    palette: tuple[Color, Color, Color]
    hazard: str
    localized_name: str = ""
    localized_description: str = ""

    @property
    def key(self) -> str:
        return self.id

    @property
    def name(self) -> str:
        return self.localized_name or self.name_key

    @property
    def subtitle(self) -> str:
        return self.localized_description or self.description_key
