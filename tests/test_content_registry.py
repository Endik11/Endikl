from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from game.content_errors import ContentValidationError, DuplicateContentIdError, MissingContentReferenceError
from game.content_registry import ContentRegistry
from game.settings import ROOT_DIR


def copy_data(tmp_path: Path) -> Path:
    target = tmp_path / "data"
    shutil.copytree(ROOT_DIR / "data", target)
    return target


def mutate(path: Path, filename: str, callback) -> None:
    target = path / filename
    payload = json.loads(target.read_text(encoding="utf-8"))
    callback(payload)
    target.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def test_successful_load_and_strict_lookup(tmp_path: Path) -> None:
    registry = ContentRegistry(copy_data(tmp_path), allow_fallback=False)
    registry.load_all()
    assert len(registry.fighters) == 6
    assert registry.has_fighter("ren_kaido") and not registry.has_fighter("ryu")
    assert len(registry.attacks) == 11
    assert len(registry.combos) == 4
    assert len(registry.arenas) == 6
    with pytest.raises(MissingContentReferenceError, match="Unknown arena"):
        registry.get_arena("unknown_arena")


def test_duplicate_id_is_rejected(tmp_path: Path) -> None:
    data = copy_data(tmp_path)
    mutate(data, "fighters.json", lambda p: p["fighters"].append(dict(p["fighters"][0])))
    with pytest.raises(DuplicateContentIdError):
        ContentRegistry(data, allow_fallback=False).load_all()


@pytest.mark.parametrize(
    ("filename", "mutation", "error"),
    [
        ("fighters.json", lambda p: p["fighters"][0].pop("name"), ContentValidationError),
        ("fighters.json", lambda p: p["fighters"][0].update(max_health=-1), ContentValidationError),
        ("fighters.json", lambda p: p["fighters"][0]["attack_ids"].append("missing_attack"), MissingContentReferenceError),
        ("attacks.json", lambda p: p["attacks"][0].update(owner_id="missing_owner"), MissingContentReferenceError),
        ("combos.json", lambda p: p["combos"][0].update(resulting_attack_id="missing_attack"), MissingContentReferenceError),
    ],
)
def test_invalid_content_is_rejected(tmp_path: Path, filename, mutation, error) -> None:
    data = copy_data(tmp_path)
    mutate(data, filename, mutation)
    with pytest.raises(error):
        ContentRegistry(data, allow_fallback=False).load_all()


def test_unknown_localization_key_has_readable_fallback() -> None:
    registry = ContentRegistry(ROOT_DIR / "data", allow_fallback=False)
    registry.load_all()
    assert registry.localization.get("missing.key") == "[missing.key]"


def test_missing_data_uses_minimal_fallback(tmp_path: Path) -> None:
    registry = ContentRegistry(tmp_path / "absent", allow_fallback=True)
    registry.load_all()
    assert registry.using_fallback
    assert len(registry.fighters) == 2
    assert len(registry.arenas) == 1


def test_failed_reload_retains_previous_objects(tmp_path: Path) -> None:
    data = copy_data(tmp_path)
    registry = ContentRegistry(data, allow_fallback=False)
    registry.load_all()
    before = registry.fighters
    mutate(data, "fighters.json", lambda p: p["fighters"][0].update(max_health=-10))
    assert not registry.reload()
    assert registry.fighters is before
    assert registry.get_fighter("kael").max_health == 1000


@pytest.mark.parametrize("field,value",[("lifetime_frames",0),("width",0),("durability",0),("priority",-1),("hit_level","invalid"),("chip_damage",9999)])
def test_invalid_projectile_definition_is_rejected(tmp_path: Path,field,value) -> None:
    data=copy_data(tmp_path)
    def change(payload):
        projectile=next(a for a in payload["attacks"] if a["id"]=="thunder_boundary")["projectile_definition"];projectile[field]=value
    mutate(data,"attacks.json",change)
    with pytest.raises(ContentValidationError):ContentRegistry(data,allow_fallback=False).load_all()
