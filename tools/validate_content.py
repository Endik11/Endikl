from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from game.achievements import AchievementRegistry
from game.content_registry import ContentRegistry
from game.economy import Catalog
from game.modes.story_runner import StoryRegistry
from game.platform_paths import data_path


def main() -> None:
    content = ContentRegistry(data_path(), allow_fallback=False)
    content.load_all()
    StoryRegistry(data_path()).load(set(content.fighters))
    Catalog.load(data_path("shop_catalog.json"))
    AchievementRegistry.load(data_path("achievements.json"))
    if content.using_fallback:
        raise SystemExit("fallback content is not valid for release")
    print(f"content_valid fighters={len(content.fighters)} attacks={len(content.attacks)} combos={len(content.combos)} arenas={len(content.arenas)}")


if __name__ == "__main__":
    main()
