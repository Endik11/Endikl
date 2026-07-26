from __future__ import annotations

import pygame

from game.resources import OPTIONAL_ASSETS, inspect_optional_assets, load_optional_image


def test_missing_optional_assets_use_procedural_fallback(tmp_path) -> None:
    report = inspect_optional_assets(tmp_path)

    assert not report.healthy
    assert report.available == ()
    assert set(report.missing) == set(OPTIONAL_ASSETS)


def test_optional_image_loader_returns_fallback_for_missing_file(tmp_path) -> None:
    fallback = pygame.Surface((7, 9), pygame.SRCALPHA)

    loaded = load_optional_image(tmp_path / "missing.png", lambda: fallback)

    assert loaded is fallback

