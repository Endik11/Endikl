import pygame
from types import SimpleNamespace

from game.enums import GameState, MatchMode
from game.screens.mode_select_screen import ModeSelectScreen


class InputStub:
    def pressed_for(self, player):
        return {}


class StateStub:
    def __init__(self):
        self.requested = None

    def request_change(self, state):
        self.requested = state

    def go_back(self):
        return True


class DisplayStub:
    def screen_to_virtual(self, position):
        return position


def test_mode_selection_click_starts_local_vs_flow():
    context = SimpleNamespace(
        input=InputStub(),
        state_manager=StateStub(),
        display=DisplayStub(),
        session=SimpleNamespace(selected_mode=None),
    )
    screen = ModeSelectScreen(context)
    screen.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(120, 215)))

    screen.update(0.016)

    assert context.session.selected_mode is MatchMode.LOCAL_VS
    assert context.state_manager.requested is GameState.CHARACTER_SELECT
