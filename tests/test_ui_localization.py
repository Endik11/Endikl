import unittest

from game.menu import ARENAS, MenuScreen


class UILocalizationTests(unittest.TestCase):
    def test_menu_items_are_russian(self) -> None:
        screen = MenuScreen()
        labels = [item.label for item in screen.items]
        self.assertIn("История", labels)
        self.assertIn("Аркада", labels)
        self.assertIn("Турнир", labels)
        self.assertIn("Локальный VS", labels)
        self.assertIn("Тренировка", labels)
        self.assertIn("Настройки", labels)
        self.assertIn("Выход", labels)

    def test_chinese_inspired_arenas_exist(self) -> None:
        arena_keys = set(ARENAS.keys())
        self.assertTrue({"great_wall", "dragon_mountains", "pagoda_ridge"} <= arena_keys)


if __name__ == "__main__":
    unittest.main()
