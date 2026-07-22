from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pygame


ROOT_DIR = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT_DIR / "assets"
SAVE_DIR = ROOT_DIR / "saves"
SETTINGS_FILE = SAVE_DIR / "settings.json"

GAME_TITLE = "Mortal End: Наследие"
VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
FPS = 60

GROUND_Y = 584
LEFT_WALL = 70
RIGHT_WALL = VIRTUAL_WIDTH - 70

GRAVITY = 2500.0
MOVE_SPEED = 470.0
AIR_MOVE_SPEED = 270.0
JUMP_SPEED = -920.0
FRICTION = 0.82

MAX_HEALTH = 1000
MAX_ENERGY = 1000
ROUND_SECONDS = 99
ROUNDS_TO_WIN = 2


COLORS = {
    "black": (8, 9, 12),
    "white": (238, 241, 244),
    "paper": (229, 231, 222),
    "ink": (28, 31, 36),
    "muted": (132, 141, 151),
    "red": (207, 53, 63),
    "red_dark": (112, 24, 33),
    "gold": (232, 181, 82),
    "blue": (79, 150, 214),
    "cyan": (63, 201, 197),
    "green": (90, 191, 118),
    "violet": (142, 104, 207),
    "panel": (26, 30, 36),
    "panel_light": (42, 48, 57),
    "shadow": (0, 0, 0),
}


DEFAULT_KEYBOARD = {
    "p1": {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "light_punch": pygame.K_a,
        "heavy_punch": pygame.K_s,
        "light_kick": pygame.K_z,
        "heavy_kick": pygame.K_x,
        "block": pygame.K_d,
        "energy": pygame.K_q,
        "pause": pygame.K_RETURN,
    },
    "p2": {
        "left": pygame.K_j,
        "right": pygame.K_l,
        "up": pygame.K_i,
        "down": pygame.K_k,
        "light_punch": pygame.K_u,
        "heavy_punch": pygame.K_o,
        "light_kick": pygame.K_m,
        "heavy_kick": pygame.K_PERIOD,
        "block": pygame.K_p,
        "energy": pygame.K_RSHIFT,
        "pause": pygame.K_ESCAPE,
    },
}


COMMANDS = (
    "left",
    "right",
    "up",
    "down",
    "light_punch",
    "heavy_punch",
    "light_kick",
    "heavy_kick",
    "block",
    "energy",
    "pause",
)


@dataclass
class VideoSettings:
    width: int = VIRTUAL_WIDTH
    height: int = VIRTUAL_HEIGHT
    fullscreen: bool = False
    camera_shake: bool = True
    particles: bool = True


@dataclass
class AudioSettings:
    master_volume: float = 0.75
    music_volume: float = 0.45
    sfx_volume: float = 0.85
    mute: bool = False


@dataclass
class GameplaySettings:
    difficulty: str = "normal"
    rounds_to_win: int = ROUNDS_TO_WIN
    round_seconds: int = ROUND_SECONDS
    training_infinite_energy: bool = True


@dataclass
class ControlSettings:
    keyboard: dict[str, dict[str, int]] = field(
        default_factory=lambda: {
            player: dict(mapping) for player, mapping in DEFAULT_KEYBOARD.items()
        }
    )
    gamepad_enabled: bool = True


@dataclass
class GameSettings:
    video: VideoSettings = field(default_factory=VideoSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    gameplay: GameplaySettings = field(default_factory=GameplaySettings)
    controls: ControlSettings = field(default_factory=ControlSettings)


class SettingsManager:
    """Loads and saves user settings while keeping sane defaults."""

    def __init__(self, path: Path = SETTINGS_FILE) -> None:
        self.path = path
        self.settings = GameSettings()

    def load(self) -> GameSettings:
        if not self.path.exists():
            self.save()
            return self.settings

        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            self.settings = self._from_dict(data)
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            self.settings = GameSettings()
            self.save()
        return self.settings

    def save(self) -> None:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        self.path.write_text(
            json.dumps(asdict(self.settings), indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def _from_dict(self, data: dict[str, Any]) -> GameSettings:
        base = GameSettings()
        video = VideoSettings(**{**asdict(base.video), **data.get("video", {})})
        audio = AudioSettings(**{**asdict(base.audio), **data.get("audio", {})})
        gameplay = GameplaySettings(
            **{**asdict(base.gameplay), **data.get("gameplay", {})}
        )
        controls_data = data.get("controls", {})
        keyboard = {
            player: {
                command: int(
                    controls_data.get("keyboard", {})
                    .get(player, {})
                    .get(command, DEFAULT_KEYBOARD[player][command])
                )
                for command in COMMANDS
            }
            for player in ("p1", "p2")
        }
        controls = ControlSettings(
            keyboard=keyboard,
            gamepad_enabled=bool(controls_data.get("gamepad_enabled", True)),
        )
        return GameSettings(video=video, audio=audio, gameplay=gameplay, controls=controls)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))

