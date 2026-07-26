"""Compatibility exports for screens moved during architecture stage 2.

New code should import from ``game.screens`` or ``game.arena_catalog`` directly.
This module remains temporarily so existing integrations keep working.
"""

from .arena_catalog import ARENAS, ArenaDefinition
from .screens.arena_select_screen import ArenaSelectScreen
from .screens.character_select_screen import CharacterSelectScreen
from .screens.collection_screen import CollectionScreen
from .screens.main_menu_screen import MainMenuScreen, MenuScreen
from .screens.settings_screen import SettingsScreen
from .screens.stats_screen import StatsScreen
from .screens.ui_helpers import (
    MenuItem,
    accept_pressed,
    back_pressed,
    build_pause_menu_items,
    draw_arena_preview,
    draw_background,
    draw_text,
)

__all__ = [
    "ARENAS",
    "ArenaDefinition",
    "ArenaSelectScreen",
    "CharacterSelectScreen",
    "CollectionScreen",
    "MainMenuScreen",
    "MenuItem",
    "MenuScreen",
    "SettingsScreen",
    "StatsScreen",
    "accept_pressed",
    "back_pressed",
    "build_pause_menu_items",
    "draw_arena_preview",
    "draw_background",
    "draw_text",
]

