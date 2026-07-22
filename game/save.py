from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .debug import log_error
from .settings import SAVE_DIR


SAVE_FILE = SAVE_DIR / "profile.json"


@dataclass
class MatchRecord:
    wins: int = 0
    losses: int = 0
    perfects: int = 0
    fatalities: int = 0
    brutalities: int = 0
    stage_fatalities: int = 0


@dataclass
class ProfileData:
    selected_fighter: str = "kael"
    selected_arena: str = "neon_foundry"
    unlocked_fighters: list[str] = field(default_factory=lambda: ["kael", "sable"])
    unlocked_arenas: list[str] = field(
        default_factory=lambda: ["neon_foundry", "storm_pier"]
    )
    arcade_clears: int = 0
    story_chapter: int = 1
    currency: int = 0
    purchased_items: list[str] = field(default_factory=list)
    equipped_items: dict[str, str] = field(default_factory=dict)
    record: MatchRecord = field(default_factory=MatchRecord)


class SaveManager:
    def __init__(self, path: Path = SAVE_FILE) -> None:
        self.path = path
        self.profile = ProfileData()

    def load(self) -> ProfileData:
        if not self.path.exists():
            self.save()
            return self.profile
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            record = MatchRecord(**{**asdict(MatchRecord()), **data.get("record", {})})
            self.profile = ProfileData(
                selected_fighter=data.get("selected_fighter", "kael"),
                selected_arena=data.get("selected_arena", "neon_foundry"),
                unlocked_fighters=list(
                    data.get("unlocked_fighters", ["kael", "sable"])
                ),
                unlocked_arenas=list(
                    data.get("unlocked_arenas", ["neon_foundry", "storm_pier"])
                ),
                arcade_clears=int(data.get("arcade_clears", 0)),
                story_chapter=int(data.get("story_chapter", 1)),
                currency=int(data.get("currency", 0)),
                purchased_items=list(data.get("purchased_items", [])),
                equipped_items=dict(data.get("equipped_items", {})),
                record=record,
            )
        except (OSError, json.JSONDecodeError, TypeError, ValueError) as exc:
            log_error("Failed to load profile data", exc)
            self.profile = ProfileData()
            self.save()
        return self.profile

    def save(self) -> None:
        SAVE_DIR.mkdir(parents=True, exist_ok=True)
        try:
            self.path.write_text(
                json.dumps(asdict(self.profile), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as exc:
            log_error("Failed to save profile data", exc)

    def record_win(self, finisher: str | None, perfect: bool) -> None:
        self.profile.record.wins += 1
        if perfect:
            self.profile.record.perfects += 1
        if finisher == "fatality":
            self.profile.record.fatalities += 1
        elif finisher == "brutality":
            self.profile.record.brutalities += 1
        elif finisher == "stage":
            self.profile.record.stage_fatalities += 1
        self.save()

    def record_loss(self) -> None:
        self.profile.record.losses += 1
        self.save()

    def unlock(self, key: str, kind: str) -> None:
        target = (
            self.profile.unlocked_fighters
            if kind == "fighter"
            else self.profile.unlocked_arenas
        )
        if key not in target:
            target.append(key)
            self.save()

    def award_currency(self, amount: int) -> None:
        self.profile.currency += amount
        self.save()

    def purchase_item(self, item_id: str, category: str, cost: int) -> None:
        if self.profile.currency < cost:
            return
        self.profile.currency -= cost
        if item_id not in self.profile.purchased_items:
            self.profile.purchased_items.append(item_id)
        self.profile.equipped_items[category] = item_id
        self.save()

    def equip_item(self, category: str, item_id: str) -> None:
        self.profile.equipped_items[category] = item_id
        self.save()

