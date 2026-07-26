from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Protocol

if TYPE_CHECKING:
    from .audio_manager import AudioManager
    from .content_registry import ContentRegistry
    from .display_manager import DisplayManager
    from .match_runtime import MatchRuntime
    from .localization import LocalizationManager
    from .resources import ResourceReport
    from .save import SaveManager
    from .session import GameSession
    from .settings import SettingsManager
    from .state_manager import StateManager


class InputView(Protocol):
    def pressed_for(self, player: str) -> dict[str, bool]: ...

    def controls_for(self, player: str) -> dict[str, bool]: ...


@dataclass(slots=True)
class ScreenContext:
    state_manager: StateManager
    settings: SettingsManager
    saves: SaveManager
    resources: ResourceReport
    audio: AudioManager
    display: DisplayManager
    request_exit: Callable[[], None]
    session: GameSession
    match_runtime: MatchRuntime
    input: InputView
    content: ContentRegistry
    localization: LocalizationManager
