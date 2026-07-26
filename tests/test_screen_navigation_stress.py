from game.state_manager import StateManager
from game.enums import GameState
from game.screens.base_screen import BaseScreen
def test_thousand_typed_screen_transitions():
    manager=StateManager();manager.register(GameState.MAIN_MENU,BaseScreen());manager.register(GameState.MODE_SELECT,BaseScreen());manager.request_change(GameState.MAIN_MENU,remember_current=False);manager.apply_pending_change()
    for index in range(1000):manager.request_change(GameState.MODE_SELECT if index%2==0 else GameState.MAIN_MENU,remember_current=False);assert manager.apply_pending_change()
