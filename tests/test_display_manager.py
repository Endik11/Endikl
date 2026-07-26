from types import SimpleNamespace

import pygame

from game.display_manager import DisplayManager


def make_display(size=(1280, 720)) -> DisplayManager:
    video = SimpleNamespace(width=size[0], height=size[1], fullscreen=False)
    return DisplayManager(SimpleNamespace(video=video))


def test_viewport_preserves_sixteen_by_nine() -> None:
    assert DisplayManager.calculate_viewport((1280, 720)) == pygame.Rect(0, 0, 1280, 720)
    assert DisplayManager.calculate_viewport((1920, 1080)) == pygame.Rect(0, 0, 1920, 1080)
    assert DisplayManager.calculate_viewport((1024, 768)) == pygame.Rect(0, 96, 1024, 576)
    assert DisplayManager.calculate_viewport((1600, 1200)) == pygame.Rect(0, 150, 1600, 900)


def test_mouse_mapping_accounts_for_letterbox_offsets() -> None:
    display = make_display((1024, 768))
    assert display.viewport_rect == pygame.Rect(0, 96, 1024, 576)
    assert display.screen_to_virtual((0, 95)) is None
    assert display.screen_to_virtual((512, 384)) == (640, 360)
    assert display.virtual_to_screen((640, 360)) == (512, 384)


def test_resize_updates_physical_size_without_a_window() -> None:
    display = make_display()
    display.handle_resize((800, 800))
    assert display.physical_size == (800, 800)
    assert display.viewport_rect == pygame.Rect(0, 175, 800, 450)

