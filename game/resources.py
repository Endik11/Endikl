from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import pygame

from .debug import log_warning
from .settings import ASSET_DIR


OPTIONAL_ASSETS = (
    Path("arenas/li_river_guilin.jpg"),
    Path("arenas/zhangjiajie_forest.jpg"),
    Path("fighters/kael_sheet.png"),
    Path("fighters/mira_sheet.png"),
    Path("fighters/orrin_sheet.png"),
    Path("fighters/sable_sheet.png"),
)


@dataclass(frozen=True)
class ResourceReport:
    available: tuple[Path, ...]
    missing: tuple[Path, ...]
    unreadable: tuple[Path, ...]

    @property
    def healthy(self) -> bool:
        return not self.missing and not self.unreadable


def inspect_optional_assets(asset_dir: Path = ASSET_DIR) -> ResourceReport:
    """Inspect optional artwork without making startup depend on it."""
    available: list[Path] = []
    missing: list[Path] = []
    unreadable: list[Path] = []
    for relative_path in OPTIONAL_ASSETS:
        path = asset_dir / relative_path
        if not path.is_file():
            missing.append(relative_path)
            log_warning("Optional asset is missing; procedural fallback will be used: %s", path)
            continue
        try:
            pygame.image.load(path)
        except (OSError, pygame.error) as exc:
            unreadable.append(relative_path)
            log_warning(
                "Optional asset is unreadable; procedural fallback will be used: %s (%s)",
                path,
                exc,
            )
        else:
            available.append(relative_path)
    return ResourceReport(tuple(available), tuple(missing), tuple(unreadable))


def load_optional_image(
    path: Path,
    fallback: Callable[[], pygame.Surface],
) -> pygame.Surface:
    """Load an image or return a caller-provided procedural placeholder."""
    try:
        return pygame.image.load(path)
    except (OSError, pygame.error) as exc:
        log_warning("Unable to load image %s; using fallback (%s)", path, exc)
        return fallback()

