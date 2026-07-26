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


def test_existing_unverified_assets_are_blocked_by_default(tmp_path) -> None:
    for relative in OPTIONAL_ASSETS:
        path = tmp_path / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        pygame.image.save(pygame.Surface((2, 2)), path)

    report = inspect_optional_assets(tmp_path)

    assert report.available == ()
    assert set(report.blocked) == set(OPTIONAL_ASSETS)


def test_unverified_asset_loader_requires_explicit_opt_in(tmp_path) -> None:
    image_path = tmp_path / "asset.png"
    pygame.image.save(pygame.Surface((3, 4)), image_path)
    fallback = pygame.Surface((1, 1), pygame.SRCALPHA)

    blocked = load_optional_image(image_path, lambda: fallback)
    loaded = load_optional_image(image_path, lambda: fallback, allow_unverified_assets=True)

    assert blocked is fallback
    assert loaded.get_size() == (3, 4)

