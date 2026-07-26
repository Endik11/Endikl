from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .enums import MatchMode


@dataclass(slots=True)
class GameSession:
    selected_mode: MatchMode | None = None
    player_one_fighter: str | None = None
    player_two_fighter: str | None = None
    selected_arena: str | None = None
    arcade_progress: int = 0
    story_progress: int = 0
    tournament_progress: int = 0
    last_match_result: dict[str, Any] | None = None
    match_options: dict[str, Any] = field(default_factory=dict)

    def reset_character_selection(self) -> None:
        self.player_one_fighter = None
        self.player_two_fighter = None

    def reset_match_selection(self) -> None:
        self.reset_character_selection()
        self.selected_arena = None
        self.clear_transient_match_data()

    def prepare_local_match(self, player_one: str, player_two: str) -> None:
        if not player_one or not player_two:
            raise ValueError("Both fighters are required for a local match")
        self.selected_mode = MatchMode.LOCAL_VS
        self.player_one_fighter = player_one
        self.player_two_fighter = player_two
        self.selected_arena = None
        self.clear_transient_match_data()

    def clear_transient_match_data(self) -> None:
        self.last_match_result = None
        self.match_options.clear()

    @property
    def fighters_selected(self) -> bool:
        return bool(self.player_one_fighter and self.player_two_fighter)

    @property
    def ready_for_match(self) -> bool:
        return self.selected_mode is not None and self.fighters_selected and bool(self.selected_arena)

