import pygame

from game.screens.profile_screen import ProfileScreen


class FakeStateManager:
    def __init__(self):
        self.back_calls = 0

    def go_back(self):
        self.back_calls += 1


class FakeInput:
    def pressed_for(self, player):
        return {"cancel": False, "block": False}


class FakeContext:
    def __init__(self):
        self.state_manager = FakeStateManager()
        self.input = FakeInput()


def test_profile_escape_returns_to_previous_screen():
    pygame.init()
    context = FakeContext()
    screen = ProfileScreen(context)
    screen.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE))

    screen.update(0.016)

    assert context.state_manager.back_calls == 1
    pygame.quit()
