from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import pygame

from .debug import log_warning
from .json_io import read_json_object, write_json_atomic


ROOT_DIR = Path(__file__).resolve().parent.parent
ASSET_DIR = ROOT_DIR / "assets"
SAVE_DIR = ROOT_DIR / "saves"
SETTINGS_FILE = SAVE_DIR / "settings.json"

GAME_TITLE = "Mortal End: Наследие"
VIRTUAL_WIDTH = 1280
VIRTUAL_HEIGHT = 720
FPS = 60
RESOLUTIONS = ["1280x720", "1366x768", "1600x900", "1920x1080", "2560x1440"]
FPS_OPTIONS = [30, 60, 90, 120, 144, 165, 240, 0]

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
        "left": pygame.K_a,
        "right": pygame.K_d,
        "up": pygame.K_w,
        "down": pygame.K_s,
        "light_punch": pygame.K_t,
        "heavy_punch": pygame.K_u,
        "light_kick": pygame.K_g,
        "heavy_kick": pygame.K_j,
        "block": pygame.K_SPACE,
        "throw": pygame.K_LCTRL,
        "stance": pygame.K_LALT,
        "tag": pygame.K_TAB,
        "energy": pygame.K_q,
        "pause": pygame.K_1,
    },
    "p2": {
        "left": pygame.K_LEFT,
        "right": pygame.K_RIGHT,
        "up": pygame.K_UP,
        "down": pygame.K_DOWN,
        "light_punch": pygame.K_KP_1,
        "heavy_punch": pygame.K_KP_2,
        "light_kick": pygame.K_KP_3,
        "heavy_kick": pygame.K_KP_4,
        "block": pygame.K_RSHIFT,
        "throw": pygame.K_RCTRL,
        "stance": pygame.K_RALT,
        "tag": pygame.K_SLASH,
        "energy": pygame.K_KP_5,
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
    "throw",
    "stance",
    "tag",
    "energy",
    "pause",
)


@dataclass
class VideoSettings:
    width: int = VIRTUAL_WIDTH
    height: int = VIRTUAL_HEIGHT
    fullscreen: bool = False
    display_mode: str = "windowed"
    camera_shake: bool = True
    particles: bool = True
    trails: bool = True
    shadows: bool = True
    flashes: bool = True
    dynamic_zoom: bool = True
    background_animation: bool = True
    damage_numbers: bool = True
    colorblind_indicators: bool = False
    reduced_motion: bool = False
    reduced_flashes: bool = False
    allow_unverified_assets: bool = False
    fps_limit: int = 60
    ui_scale: float = 1.0
    render_scale: float = 1.0
    vsync: bool = False
    borderless: bool = False
    screen_shake_strength: float = 1.0


@dataclass
class AudioSettings:
    master_volume: float = 0.75
    music_volume: float = 0.45
    sfx_volume: float = 0.85
    interface_volume: float = 0.75
    mute: bool = False
    announcer_volume: float = 0.8
    ambience_volume: float = 0.6
    mute_when_unfocused: bool = False


@dataclass
class GameplaySettings:
    difficulty: str = "normal"
    rounds_to_win: int = ROUNDS_TO_WIN
    round_seconds: int = ROUND_SECONDS
    training_infinite_energy: bool = True
    pause_on_focus_loss: bool = True
    input_history: bool = False
    language: str = "ru"

@dataclass
class AccessibilitySettings:
    reduced_motion: bool = False
    reduced_flashes: bool = False
    high_contrast: bool = False
    colorblind_indicators: bool = False
    large_text: bool = False
    subtitles: bool = True
    visual_sound_indicators: bool = False
    hold_assistance: bool = False
    background_movement: bool = True
    screen_shake_strength: float = 1.0


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
    version: int = 2
    video: VideoSettings = field(default_factory=VideoSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    gameplay: GameplaySettings = field(default_factory=GameplaySettings)
    controls: ControlSettings = field(default_factory=ControlSettings)
    accessibility: AccessibilitySettings = field(default_factory=AccessibilitySettings)


class SettingsManager:
    """Loads and saves user settings while keeping sane defaults."""

    def __init__(self, path: Path = SETTINGS_FILE) -> None:
        self.path = path
        self.settings = GameSettings()

    def load(self) -> GameSettings:
        data = read_json_object(self.path, "settings")
        if data is None:
            self.save()
            return self.settings
        self.settings = self._from_dict(data)
        return self.settings

    def save(self) -> None:
        write_json_atomic(self.path, asdict(self.settings), "settings")

    def _from_dict(self, data: dict[str, Any]) -> GameSettings:
        base = GameSettings()
        video_data = _object(data.get("video"))
        audio_data = _object(data.get("audio"))
        gameplay_data = _object(data.get("gameplay"))
        accessibility_data = _object(data.get("accessibility"))
        video = VideoSettings(
            width=_resolution_dimension(video_data.get("width"), base.video.width),
            height=_resolution_dimension(video_data.get("height"), base.video.height),
            fullscreen=_boolean(video_data.get("fullscreen"), base.video.fullscreen),
            display_mode=_choice(
                video_data.get("display_mode"),
                base.video.display_mode,
                {"windowed", "fullscreen"},
            ),
            camera_shake=_boolean(video_data.get("camera_shake"), base.video.camera_shake),
            particles=_boolean(video_data.get("particles"), base.video.particles),
            trails=_boolean(video_data.get("trails"), base.video.trails),
            shadows=_boolean(video_data.get("shadows"), base.video.shadows),
            flashes=_boolean(video_data.get("flashes"), base.video.flashes),
            dynamic_zoom=_boolean(video_data.get("dynamic_zoom"), base.video.dynamic_zoom),
            background_animation=_boolean(video_data.get("background_animation"), base.video.background_animation),
            damage_numbers=_boolean(video_data.get("damage_numbers"), base.video.damage_numbers),
            colorblind_indicators=_boolean(video_data.get("colorblind_indicators"), base.video.colorblind_indicators),
            reduced_motion=_boolean(video_data.get("reduced_motion"), base.video.reduced_motion),
            reduced_flashes=_boolean(video_data.get("reduced_flashes"), base.video.reduced_flashes),
            allow_unverified_assets=_boolean(video_data.get("allow_unverified_assets"), base.video.allow_unverified_assets),
            fps_limit=_choice_int(video_data.get("fps_limit"), base.video.fps_limit, set(FPS_OPTIONS)),
            ui_scale=_bounded_float(video_data.get("ui_scale"), base.video.ui_scale, 0.75, 2.0),
            render_scale=_bounded_float(video_data.get("render_scale"),base.video.render_scale,.5,1.0),
            vsync=_boolean(video_data.get("vsync"),base.video.vsync),
            borderless=_boolean(video_data.get("borderless"),base.video.borderless),
            screen_shake_strength=_bounded_float(video_data.get("screen_shake_strength"),base.video.screen_shake_strength,0,1),
        )
        audio = AudioSettings(
            master_volume=_bounded_float(audio_data.get("master_volume"), base.audio.master_volume, 0.0, 1.0),
            music_volume=_bounded_float(audio_data.get("music_volume"), base.audio.music_volume, 0.0, 1.0),
            sfx_volume=_bounded_float(audio_data.get("sfx_volume"), base.audio.sfx_volume, 0.0, 1.0),
            interface_volume=_bounded_float(
                audio_data.get("interface_volume"),
                base.audio.interface_volume,
                0.0,
                1.0,
            ),
            mute=_boolean(audio_data.get("mute"), base.audio.mute),
            announcer_volume=_bounded_float(audio_data.get("announcer_volume"),base.audio.announcer_volume,0,1),
            ambience_volume=_bounded_float(audio_data.get("ambience_volume"),base.audio.ambience_volume,0,1),
            mute_when_unfocused=_boolean(audio_data.get("mute_when_unfocused"),base.audio.mute_when_unfocused),
        )
        gameplay = GameplaySettings(
            difficulty=_choice(
                gameplay_data.get("difficulty"),
                base.gameplay.difficulty,
                {"easy", "normal", "hard"},
            ),
            rounds_to_win=_bounded_int(
                gameplay_data.get("rounds_to_win"),
                base.gameplay.rounds_to_win,
                1,
                5,
            ),
            round_seconds=_bounded_int(
                gameplay_data.get("round_seconds"),
                base.gameplay.round_seconds,
                10,
                999,
            ),
            training_infinite_energy=_boolean(
                gameplay_data.get("training_infinite_energy"),
                base.gameplay.training_infinite_energy,
            ),
            pause_on_focus_loss=_boolean(gameplay_data.get("pause_on_focus_loss"),base.gameplay.pause_on_focus_loss),
            input_history=_boolean(gameplay_data.get("input_history"),base.gameplay.input_history),
            language=_choice(gameplay_data.get("language"),base.gameplay.language,{"ru","en"}),
        )
        controls_data = _object(data.get("controls"))
        keyboard_data = _object(controls_data.get("keyboard"))
        keyboard = {
            player: {
                command: _pygame_key(
                    _object(keyboard_data.get(player)).get(command),
                    DEFAULT_KEYBOARD[player][command],
                )
                for command in COMMANDS
            }
            for player in ("p1", "p2")
        }
        controls = ControlSettings(
            keyboard=keyboard,
            gamepad_enabled=_boolean(
                controls_data.get("gamepad_enabled"),
                base.controls.gamepad_enabled,
            ),
        )
        accessibility=AccessibilitySettings(
            reduced_motion=_boolean(accessibility_data.get("reduced_motion"),video.reduced_motion),reduced_flashes=_boolean(accessibility_data.get("reduced_flashes"),video.reduced_flashes),high_contrast=_boolean(accessibility_data.get("high_contrast"),False),colorblind_indicators=_boolean(accessibility_data.get("colorblind_indicators"),video.colorblind_indicators),large_text=_boolean(accessibility_data.get("large_text"),False),subtitles=_boolean(accessibility_data.get("subtitles"),True),visual_sound_indicators=_boolean(accessibility_data.get("visual_sound_indicators"),False),hold_assistance=_boolean(accessibility_data.get("hold_assistance"),False),background_movement=_boolean(accessibility_data.get("background_movement"),video.background_animation),screen_shake_strength=_bounded_float(accessibility_data.get("screen_shake_strength"),video.screen_shake_strength,0,1))
        return GameSettings(version=2,video=video, audio=audio, gameplay=gameplay, controls=controls,accessibility=accessibility)


def clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _object(value: object) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _boolean(value: object, default: bool) -> bool:
    return value if isinstance(value, bool) else default


def _choice(value: object, default: str, allowed: set[str]) -> str:
    return value if isinstance(value, str) and value in allowed else default


def _bounded_int(value: object, default: int, low: int, high: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return max(low, min(high, parsed))


def _resolution_dimension(value: object, default: int) -> int:
    if isinstance(value, bool):
        return default
    try:
        parsed = int(value)
    except (TypeError, ValueError, OverflowError):
        return default
    return parsed if 640 <= parsed <= 7680 else default


def _choice_int(value: object, default: int, allowed: set[int]) -> int:
    parsed = _bounded_int(value, default, min(allowed), max(allowed))
    return parsed if parsed in allowed else default


def _pygame_key(value: object, default: int) -> int:
    return _bounded_int(value, default, 0, 2**31 - 1)


def _bounded_float(value: object, default: float, low: float, high: float) -> float:
    if isinstance(value, bool):
        return default
    try:
        parsed = float(value)
    except (TypeError, ValueError, OverflowError):
        return default
    if parsed != parsed:
        log_warning("Ignoring NaN setting value")
        return default
    return max(low, min(high, parsed))
