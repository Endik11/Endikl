import unittest

import pygame

from game.menu import ARENAS, CollectionScreen, MenuScreen, SettingsScreen, StatsScreen, build_pause_menu_items
from game.save import ProfileData
from game.settings import DEFAULT_KEYBOARD, GameSettings, RESOLUTIONS
from game.shop import ShopItem, build_shop_catalog


class UILocalizationTests(unittest.TestCase):
    def test_menu_items_are_russian(self) -> None:
        screen = MenuScreen()
        labels = [item.label for item in screen.items]
        self.assertIn("Начать бой", labels)
        self.assertIn("Выбор персонажа", labels)
        self.assertIn("Выбор арены", labels)
        self.assertIn("Тренировка", labels)
        self.assertIn("Башня испытаний", labels)
        self.assertIn("Настройки", labels)
        self.assertIn("Выход", labels)

    def test_chinese_inspired_arenas_exist(self) -> None:
        arena_keys = set(ARENAS.keys())
        self.assertTrue({"great_wall", "dragon_mountains", "pagoda_ridge"} <= arena_keys)

    def test_pause_menu_contains_restart_and_exit_actions(self) -> None:
        items = build_pause_menu_items("ru")
        actions = [item.action for item in items]
        self.assertIn("restart", actions)
        self.assertIn("quit_game", actions)
        self.assertIn("menu", actions)

    def test_settings_defaults_include_display_and_audio_options(self) -> None:
        settings = GameSettings()
        self.assertTrue(hasattr(settings.video, "fps_limit"))
        self.assertTrue(hasattr(settings.video, "ui_scale"))
        self.assertTrue(hasattr(settings.audio, "music_volume"))

    def test_shop_catalog_contains_purchaseable_items(self) -> None:
        catalog = build_shop_catalog()
        self.assertTrue(catalog)
        first = catalog[0]
        self.assertIsInstance(first, ShopItem)
        self.assertGreater(first.cost, 0)
        self.assertIn(first.category, {"skin", "costume", "color", "hit_effect", "victory_effect", "arena", "theme", "misc"})

    def test_supported_resolutions_include_common_modes(self) -> None:
        self.assertIn("1280x720", RESOLUTIONS)
        self.assertIn("1920x1080", RESOLUTIONS)

    def test_collection_and_stats_screens_expose_back_navigation(self) -> None:
        collection = CollectionScreen(ProfileData())
        stats = StatsScreen(ProfileData())
        self.assertEqual(collection.update({"block": True}, []), "back")
        self.assertEqual(stats.update({"block": True}, []), "back")

    def test_settings_screen_can_switch_sections(self) -> None:
        screen = SettingsScreen(GameSettings())
        self.assertEqual(screen.sections[0][0], "Видео")
        screen.update({"right": True}, [])
        self.assertEqual(screen.sections[screen.section_index][0], "FPS")
        self.assertEqual(screen.rows[0][0], "FPS")

    def test_settings_screen_can_select_section_directly(self) -> None:
        screen = SettingsScreen(GameSettings())
        screen.select_section(2)
        self.assertEqual(screen.section_index, 2)
        self.assertEqual(screen.sections[screen.section_index][0], "Звук")

    def test_settings_row_value_can_change_with_keyboard(self) -> None:
        screen = SettingsScreen(GameSettings())
        screen.select_section(1)
        screen.selected = 0
        before = screen.settings.video.fps_limit
        screen.update({"right": True}, [])
        self.assertNotEqual(screen.settings.video.fps_limit, before)

    def test_default_keyboard_uses_mk_style_controls(self) -> None:
        p1 = DEFAULT_KEYBOARD["p1"]
        self.assertEqual(p1["left"], pygame.K_a)
        self.assertEqual(p1["right"], pygame.K_d)
        self.assertEqual(p1["up"], pygame.K_w)
        self.assertEqual(p1["down"], pygame.K_s)
        self.assertEqual(p1["light_punch"], pygame.K_t)
        self.assertEqual(p1["heavy_punch"], pygame.K_u)
        self.assertEqual(p1["light_kick"], pygame.K_g)
        self.assertEqual(p1["heavy_kick"], pygame.K_j)
        self.assertEqual(p1["block"], pygame.K_SPACE)
        self.assertEqual(p1["throw"], pygame.K_LCTRL)
        self.assertEqual(p1["stance"], pygame.K_LALT)
        self.assertEqual(p1["tag"], pygame.K_TAB)
        self.assertEqual(p1["pause"], pygame.K_1)

        p2 = DEFAULT_KEYBOARD["p2"]
        self.assertNotEqual(p2["block"], p2["energy"])
        self.assertEqual(p2["energy"], pygame.K_KP_5)

    def test_menu_accepts_pause_key_as_confirm(self) -> None:
        screen = MenuScreen()
        self.assertEqual(screen.update({"pause": True}, []), "story")


if __name__ == "__main__":
    unittest.main()
