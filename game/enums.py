from __future__ import annotations

from enum import Enum, auto


class GameState(Enum):
    SPLASH = auto()
    MAIN_MENU = auto()
    MODE_SELECT = auto()
    CHARACTER_SELECT = auto()
    ARENA_SELECT = auto()
    LOADING = auto()
    FIGHT = auto()
    PAUSE = auto()
    RESULT = auto()
    SETTINGS = auto()
    CONTROLS = auto()
    COLLECTION = auto()
    SHOP = auto()
    STATS = auto()
    PROFILE = auto()
    ARCADE_LADDER = auto()
    ARCADE_SELECT = auto()
    STORY_SELECT = auto()
    STORY_DIALOGUE = auto()
    STORY_PROGRESS = auto()
    TOURNAMENT_SETUP = auto()
    TOURNAMENT_BRACKET = auto()
    TRAINING_SETUP = auto()
    TRAINING = auto()
    MODE_RESULT = auto()
    CREDITS = auto()
    EXIT = auto()
    STORY = STORY_PROGRESS
    TOURNAMENT = TOURNAMENT_BRACKET
    TRAINING_SETTINGS = TRAINING_SETUP


class MatchMode(Enum):
    LOCAL_VS = auto()
    ARCADE = auto()
    STORY = auto()
    TOURNAMENT = auto()
    TRAINING = auto()


class RoundPhase(Enum):
    INTRO = auto()
    READY = auto()
    FIGHT = auto()
    ROUND_OVER = auto()
    FINISHER = auto()
    PAUSED_SETTINGS = auto()
    MATCH_OVER = auto()
    DRAW = auto()
    DOUBLE_KO = auto()
    SUDDEN_DEATH = auto()


class FighterState(Enum):
    IDLE = auto()
    WALK = auto()
    JUMP = auto()
    CROUCH = auto()
    BLOCK = auto()
    ATTACK = auto()
    HIT = auto()
    DOWN = auto()
    VICTORY = auto()


class AttackLevel(Enum):
    HIGH = auto()
    MID = auto()
    LOW = auto()
    THROW = auto()


class HitResult(Enum):
    MISS = auto()
    HIT = auto()
    BLOCKED = auto()


_GAME_STATE_ALIASES = {
    "menu": GameState.MAIN_MENU,
    "main_menu": GameState.MAIN_MENU,
    "character_select": GameState.CHARACTER_SELECT,
    "arena_select": GameState.ARENA_SELECT,
    "fight": GameState.FIGHT,
    "pause": GameState.PAUSE,
    "match_over": GameState.RESULT,
    "result": GameState.RESULT,
    "settings": GameState.SETTINGS,
    "collection": GameState.COLLECTION,
    "shop": GameState.SHOP,
    "stats": GameState.STATS,
    "profile": GameState.PROFILE,
    "exit": GameState.EXIT,
}

_MATCH_MODE_ALIASES = {
    "vs": MatchMode.LOCAL_VS,
    "local_vs": MatchMode.LOCAL_VS,
    "arcade": MatchMode.ARCADE,
    "story": MatchMode.STORY,
    "tournament": MatchMode.TOURNAMENT,
    "training": MatchMode.TRAINING,
}


def parse_game_state(value: GameState | str) -> GameState:
    if isinstance(value, GameState):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _GAME_STATE_ALIASES:
            return _GAME_STATE_ALIASES[normalized]
        try:
            return GameState[normalized.upper()]
        except KeyError as exc:
            raise ValueError(f"Unknown game state: {value!r}") from exc
    raise TypeError(f"Game state must be GameState or str, got {type(value).__name__}")


def parse_match_mode(value: MatchMode | str) -> MatchMode:
    if isinstance(value, MatchMode):
        return value
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in _MATCH_MODE_ALIASES:
            return _MATCH_MODE_ALIASES[normalized]
        try:
            return MatchMode[normalized.upper()]
        except KeyError as exc:
            raise ValueError(f"Unknown match mode: {value!r}") from exc
    raise TypeError(f"Match mode must be MatchMode or str, got {type(value).__name__}")


def match_mode_to_legacy(mode: MatchMode) -> str:
    return {
        MatchMode.LOCAL_VS: "vs",
        MatchMode.ARCADE: "arcade",
        MatchMode.STORY: "story",
        MatchMode.TOURNAMENT: "tournament",
        MatchMode.TRAINING: "training",
    }[mode]

