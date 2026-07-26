from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
import shutil

from .debug import log_warning
from .json_io import read_json_object, write_json_atomic
from .settings import SAVE_DIR


SAVE_FILE = SAVE_DIR / "profile.json"
SAVE_VERSION = 3
LEGACY_FIGHTER_ID = "ryu"
ORIGINAL_FIGHTER_ID = "ren_kaido"


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
    version: int = SAVE_VERSION
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
    favorite_fighter: str = "kael"
    player_one_fighter: str = "kael"
    player_two_fighter: str = "sable"
    fighter_stats: dict[str, dict[str, object]] = field(default_factory=dict)
    arcade_progress: dict[str, object] = field(default_factory=dict)
    story_progress: dict[str, object] = field(default_factory=dict)
    tournament_progress: dict[str, object] = field(default_factory=dict)
    training_preferences: dict[str, object] = field(default_factory=dict)
    statistics: dict[str, object] = field(default_factory=dict)
    processed_result_ids: list[str] = field(default_factory=list)
    received_reward_ids: list[str] = field(default_factory=list)
    record: MatchRecord = field(default_factory=MatchRecord)


class SaveManager:
    def __init__(
        self,
        path: Path = SAVE_FILE,
        fighter_keys: set[str] | None = None,
        arena_keys: set[str] | None = None,
    ) -> None:
        self.path = path
        self.profile = ProfileData()
        self.fighter_keys = fighter_keys
        self.arena_keys = arena_keys

    def load(self) -> ProfileData:
        data = read_json_object(self.path, "profile")
        if data is None:
            self.save()
            return self.profile
        data, migrated = migrate_profile_data(data)
        if migrated:
            self._backup_before_migration()
        defaults = ProfileData()
        selected_fighter = _valid_key(
            data.get("selected_fighter"),
            defaults.selected_fighter,
            self.fighter_keys,
        )
        selected_arena = _valid_key(
            data.get("selected_arena"),
            defaults.selected_arena,
            self.arena_keys,
        )
        unlocked_fighters = _string_list(
            data.get("unlocked_fighters"),
            defaults.unlocked_fighters,
            self.fighter_keys,
        )
        unlocked_arenas = _string_list(
            data.get("unlocked_arenas"),
            defaults.unlocked_arenas,
            self.arena_keys,
        )
        record_data = data.get("record")
        if not isinstance(record_data, dict):
            record_data = {}
        record = MatchRecord(
            wins=_non_negative_int(record_data.get("wins")),
            losses=_non_negative_int(record_data.get("losses")),
            perfects=_non_negative_int(record_data.get("perfects")),
            fatalities=_non_negative_int(record_data.get("fatalities")),
            brutalities=_non_negative_int(record_data.get("brutalities")),
            stage_fatalities=_non_negative_int(record_data.get("stage_fatalities")),
        )
        self.profile = ProfileData(
            version=SAVE_VERSION,
            selected_fighter=selected_fighter,
            selected_arena=selected_arena,
            unlocked_fighters=unlocked_fighters,
            unlocked_arenas=unlocked_arenas,
            arcade_clears=_non_negative_int(data.get("arcade_clears")),
            story_chapter=max(1, _non_negative_int(data.get("story_chapter"), 1)),
            currency=_non_negative_int(data.get("currency")),
            purchased_items=_string_list(data.get("purchased_items"), []),
            equipped_items=_string_mapping(data.get("equipped_items")),
            favorite_fighter=_valid_key(data.get("favorite_fighter"), defaults.favorite_fighter, self.fighter_keys),
            player_one_fighter=_valid_key(data.get("player_one_fighter"), defaults.player_one_fighter, self.fighter_keys),
            player_two_fighter=_valid_key(data.get("player_two_fighter"), defaults.player_two_fighter, self.fighter_keys),
            fighter_stats=_object_mapping(data.get("fighter_stats")),
            arcade_progress=_object(data.get("arcade_progress")),
            story_progress=_object(data.get("story_progress")),
            tournament_progress=_object(data.get("tournament_progress")),
            training_preferences=_object(data.get("training_preferences")),
            statistics=_object(data.get("statistics")),
            processed_result_ids=_string_list(data.get("processed_result_ids"), []),
            received_reward_ids=_string_list(data.get("received_reward_ids"), []),
            record=record,
        )
        if migrated or data.get("version") != SAVE_VERSION:
            log_warning(
                "Profile data migrated from version %r to %s",
                data.get("version"),
                SAVE_VERSION,
            )
            self.save()
        return self.profile

    def _backup_before_migration(self) -> None:
        backup = self.path.with_suffix(self.path.suffix + ".v1.bak")
        if backup.exists() or not self.path.is_file():
            return
        try:
            shutil.copy2(self.path, backup)
        except OSError as exc:
            log_warning("Could not create pre-migration backup %s: %s", backup, exc)

    def save(self) -> None:
        write_json_atomic(self.path, asdict(self.profile), "profile")

    def record_win(self, finisher: str | None, perfect: bool) -> None:
        self.profile.record.wins += 1
        if perfect:
            self.profile.record.perfects += 1
        if finisher == "shadow_finish":
            self.profile.record.fatalities += 1
        elif finisher == "final_strike":
            self.profile.record.brutalities += 1
        elif finisher == "stage_finish":
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


def _non_negative_int(value: object, default: int = 0) -> int:
    if isinstance(value, bool):
        return default
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return default


def _valid_key(value: object, default: str, allowed: set[str] | None) -> str:
    if not isinstance(value, str):
        return default
    if allowed is not None and value not in allowed:
        return default
    return value


def _string_list(
    value: object,
    default: list[str],
    allowed: set[str] | None = None,
) -> list[str]:
    if not isinstance(value, list):
        return list(default)
    result: list[str] = []
    for item in value:
        if not isinstance(item, str) or (allowed is not None and item not in allowed):
            continue
        if item not in result:
            result.append(item)
    return result or list(default)


def _string_mapping(value: object) -> dict[str, str]:
    if not isinstance(value, dict):
        return {}
    return {
        key: item
        for key, item in value.items()
        if isinstance(key, str) and isinstance(item, str)
    }


def migrate_profile_data(data: dict[str, object]) -> tuple[dict[str, object], bool]:
    """Idempotently replace the retired fighter id while preserving statistics."""
    if _non_negative_int(data.get("version")) >= SAVE_VERSION:
        return dict(data), False
    migrated = _migrate_value(data)
    assert isinstance(migrated, dict)
    migrated["version"] = SAVE_VERSION
    return migrated, True


def _migrate_value(value: object) -> object:
    if isinstance(value, str):
        return ORIGINAL_FIGHTER_ID if value == LEGACY_FIGHTER_ID else value
    if isinstance(value, list):
        result: list[object] = []
        for item in value:
            migrated = _migrate_value(item)
            if migrated not in result:
                result.append(migrated)
        return result
    if isinstance(value, dict):
        result: dict[str, object] = {}
        for key, item in value.items():
            migrated_key = ORIGINAL_FIGHTER_ID if key == LEGACY_FIGHTER_ID else key
            migrated_item = _migrate_value(item)
            if migrated_key in result:
                result[migrated_key] = _merge_migrated_values(result[migrated_key], migrated_item)
            else:
                result[migrated_key] = migrated_item
        return result
    return value


def _merge_migrated_values(left: object, right: object) -> object:
    if isinstance(left, dict) and isinstance(right, dict):
        result = dict(left)
        additive = {"wins", "losses", "draws", "damage", "damage_dealt"}
        maxima = {"best_combo"}
        timestamps = {"timestamp", "last_played", "updated_at"}
        for key, value in right.items():
            if key in additive and isinstance(result.get(key), (int, float)) and isinstance(value, (int, float)):
                result[key] = result[key] + value
            elif key in maxima and isinstance(result.get(key), (int, float)) and isinstance(value, (int, float)):
                result[key] = max(result[key], value)
            elif key in timestamps and isinstance(result.get(key), str) and isinstance(value, str):
                result[key] = max(result[key], value)
            elif key in result:
                result[key] = _merge_migrated_values(result[key], value)
            else:
                result[key] = value
        return result
    if isinstance(left, list) and isinstance(right, list):
        return list(dict.fromkeys([*left, *right]))
    return right


def _object(value: object) -> dict[str, object]:
    return dict(value) if isinstance(value, dict) else {}


def _object_mapping(value: object) -> dict[str, dict[str, object]]:
    if not isinstance(value, dict):
        return {}
    return {key: dict(item) for key, item in value.items() if isinstance(key, str) and isinstance(item, dict)}
