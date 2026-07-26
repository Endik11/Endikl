from __future__ import annotations

import difflib
import re
from pathlib import Path

from .content_errors import ContentError, ContentValidationError, MissingContentReferenceError
from .data_loader import DataLoader
from .debug import log_critical, log_error, log_event, log_warning
from .definitions import ArenaDefinition, AttackDefinition, ComboDefinition, FighterDefinition
from .fallback_content import (
    FALLBACK_ARENAS,
    FALLBACK_ATTACKS,
    FALLBACK_COMBOS,
    FALLBACK_FIGHTERS,
    FALLBACK_LOCALIZATION,
)
from .localization import LocalizationManager
from .settings import MAX_ENERGY, ROOT_DIR


ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
HIT_LEVELS = {"high", "mid", "low", "overhead", "throw", "unblockable"}
ATTACK_PROPERTIES = {"launcher", "knockdown", "projectile", "armor", "invulnerable", "multi_hit", "air_only", "crouch_only", "special", "enhanced", "super"}
PROJECTILE_PROPERTIES = {"pierce","multi_hit","unblockable","armor_break","chip_kill"}
PROCEDURAL_STYLES = {"foundry", "pier", "court", "wall", "mountains", "pagoda"}


class ContentRegistry:
    def __init__(self, data_dir: Path | None = None, *, allow_fallback: bool = True) -> None:
        self.data_dir = Path(data_dir or ROOT_DIR / "data")
        self.allow_fallback = allow_fallback
        self.fighters: dict[str, FighterDefinition] = {}
        self.attacks: dict[str, AttackDefinition] = {}
        self.combos: dict[str, ComboDefinition] = {}
        self.arenas: dict[str, ArenaDefinition] = {}
        self.localization = LocalizationManager()
        self.using_fallback = False
        self.last_error: ContentError | None = None

    def load_all(self) -> None:
        try:
            content = self._load_from_disk()
        except ContentError as exc:
            self.last_error = exc
            if not self.allow_fallback:
                raise
            log_critical("Primary content failed; using minimal emergency content", exc)
            content = self._build_content(
                FALLBACK_FIGHTERS,
                FALLBACK_ATTACKS,
                FALLBACK_COMBOS,
                FALLBACK_ARENAS,
                FALLBACK_LOCALIZATION,
                source="<emergency fallback>",
            )
            self.using_fallback = True
        else:
            self.using_fallback = False
            self.last_error = None
        self._apply(content)
        log_event("content_loaded fighters=%s attacks=%s combos=%s arenas=%s fallback=%s", len(self.fighters), len(self.attacks), len(self.combos), len(self.arenas), self.using_fallback)

    def reload(self) -> bool:
        """Transactional debug reload: old valid content survives any failure."""
        try:
            content = self._load_from_disk()
        except ContentError as exc:
            self.last_error = exc
            log_error("Content reload rejected; previous registry retained", exc)
            return False
        self._apply(content)
        self.using_fallback = False
        self.last_error = None
        log_event("content_reload_success")
        return True

    def _load_from_disk(self):
        loader = DataLoader(self.data_dir)
        return self._build_content(
            loader.load_records("fighters.json", "fighters"),
            loader.load_records("attacks.json", "attacks"),
            loader.load_records("combos.json", "combos"),
            loader.load_records("arenas.json", "arenas"),
            loader.load_mapping("localization_ru.json", "strings"),
            source=str(self.data_dir),
        )

    def _build_content(self, fighter_rows, attack_rows, combo_rows, arena_rows, strings, *, source: str):
        fighter_values = [self._fighter(row, source) for row in fighter_rows]
        attack_values = [self._attack(row, source) for row in attack_rows]
        combo_values = [self._combo(row, source) for row in combo_rows]
        fighters = {item.id: item for item in fighter_values}
        attacks = {item.id: item for item in attack_values}
        combos = {item.id: item for item in combo_values}
        localization = LocalizationManager(strings)
        arena_values = [self._arena(row, localization, source) for row in arena_rows]
        arenas = {item.id: item for item in arena_values}
        self._validate_references(fighters, attacks, combos, arenas, localization, source)
        return fighters, attacks, combos, arenas, strings

    def _apply(self, content) -> None:
        fighters, attacks, combos, arenas, strings = content
        self.fighters.clear(); self.fighters.update(fighters)
        self.attacks.clear(); self.attacks.update(attacks)
        self.combos.clear(); self.combos.update(combos)
        self.arenas.clear(); self.arenas.update(arenas)
        self.localization.replace(strings)

    def _fighter(self, row: dict[str, object], source: str) -> FighterDefinition:
        required = ("id", "name", "title", "biography", "archetype", "super_attack_id")
        for field in required:
            _require_string(row, field, source)
        content_id = str(row["id"])
        _valid_id(content_id, source)
        portrait = _require_string(row, "portrait", source, allow_empty=True)
        sprite_sheet = _require_string(row, "sprite_sheet", source, allow_empty=True)
        health = _number(row, "max_health", source, integer=True)
        if not 1 <= health <= 10000:
            raise ContentValidationError(f"{source}: fighter '{content_id}' max_health must be 1..10000")
        difficulty = int(_number(row, "difficulty", source, integer=True))
        if not 1 <= difficulty <= 5:
            raise ContentValidationError(f"{source}: fighter '{content_id}' difficulty must be 1..5")
        palette = _palette(row.get("palette"), source, content_id)
        ai_profile = row.get("ai_profile")
        if not isinstance(ai_profile, dict) or any(not isinstance(v, (int, float)) for v in ai_profile.values()):
            raise ContentValidationError(f"{source}: fighter '{content_id}' ai_profile must contain numeric values")
        return FighterDefinition(
            id=content_id, name=str(row["name"]), title=str(row["title"]), biography=str(row["biography"]), archetype=str(row["archetype"]),
            max_health=int(health), walk_speed=float(_number(row, "walk_speed", source)), back_walk_speed=float(_number(row, "back_walk_speed", source)), air_speed=float(_number(row, "air_speed", source)), jump_velocity=float(_number(row, "jump_velocity", source)), weight=float(_number(row, "weight", source)), defense=float(_number(row, "defense", source)), difficulty=difficulty, palette=palette,
            portrait=portrait, sprite_sheet=sprite_sheet, procedural_model=_dict(row, "procedural_model", source), attack_ids=_strings(row, "attack_ids", source), combo_ids=_strings(row, "combo_ids", source), special_ids=_strings(row, "special_ids", source), super_attack_id=str(row["super_attack_id"]), victory_animation=_require_string(row, "victory_animation", source), defeat_animation=_require_string(row, "defeat_animation", source), ai_profile=dict(ai_profile), unlocked_by_default=_boolean(row, "unlocked_by_default", source),
        )

    def _attack(self, row: dict[str, object], source: str) -> AttackDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        owner = _require_string(row, "owner_id", source)
        hit_level = _require_string(row, "hit_level", source)
        if hit_level not in HIT_LEVELS:
            raise ContentValidationError(f"{source}: attack '{content_id}' has invalid hit_level '{hit_level}'")
        properties = frozenset(_strings(row, "properties", source))
        unknown = properties - ATTACK_PROPERTIES
        if unknown:
            raise ContentValidationError(f"{source}: attack '{content_id}' has unknown properties {sorted(unknown)}")
        startup = int(_number(row, "startup_frames", source, integer=True)); active = int(_number(row, "active_frames", source, integer=True)); recovery = int(_number(row, "recovery_frames", source, integer=True))
        damage = int(_number(row, "damage", source, integer=True)); chip = int(_number(row, "chip_damage", source, integer=True))
        if startup < 0 or active <= 0 or recovery < 0 or damage < 0 or chip < 0 or chip > damage:
            raise ContentValidationError(f"{source}: invalid timing or damage in attack '{content_id}'")
        energy_cost = int(_number(row, "energy_cost", source, integer=True))
        if not 0 <= energy_cost <= MAX_ENERGY:
            raise ContentValidationError(f"{source}: attack '{content_id}' energy_cost must be 0..{MAX_ENERGY}")
        hitbox = row.get("hitbox")
        if not isinstance(hitbox, list) or len(hitbox) != 4 or any(not isinstance(v, int) for v in hitbox):
            raise ContentValidationError(f"{source}: attack '{content_id}' hitbox must contain four integers")
        hit_stun = int(_number(row, "hit_stun_frames", source, integer=True)); block_stun = int(_number(row, "block_stun_frames", source, integer=True))
        if hit_stun < 0 or block_stun < 0:
            raise ContentValidationError(f"{source}: attack '{content_id}' stun frames cannot be negative")
        total=startup+active+recovery
        movement=row.get("movement",{})
        if not isinstance(movement,dict):raise ContentValidationError(f"{source}: attack '{content_id}' movement must be an object")
        hitboxes=_frame_mapping(row.get("hitboxes_by_frame",{}),source,content_id,total,"hitboxes_by_frame")
        hurtboxes=_frame_mapping(row.get("hurtbox_overrides_by_frame",{}),source,content_id,total,"hurtbox_overrides_by_frame")
        armor=_frame_list(row.get("armor_frames",[]),source,content_id,total,"armor_frames")
        invulnerability=[]
        raw_inv=row.get("invulnerability_frames",[])
        if not isinstance(raw_inv,list):raise ContentValidationError(f"{source}: attack '{content_id}' invulnerability_frames must be a list")
        for entry in raw_inv:
            if isinstance(entry,int):frame,types=entry,{"full"}
            elif isinstance(entry,dict) and isinstance(entry.get("frame"),int):frame,types=entry["frame"],set(entry.get("types",["full"]))
            else:raise ContentValidationError(f"{source}: invalid invulnerability frame in '{content_id}'")
            if not 0<=frame<total:raise ContentValidationError(f"{source}: invulnerability frame outside attack '{content_id}'")
            invulnerability.append((frame,frozenset(types)))
        projectile=_projectile(row.get("projectile_definition"),source,content_id,total)
        return AttackDefinition(content_id, owner, _require_string(row, "display_name_key", source), _require_string(row, "animation", source), startup, active, recovery, damage, chip, hit_stun, block_stun, hit_level, float(_number(row, "knockback_x", source)), float(_number(row, "knockback_y", source)), int(_number(row, "energy_gain", source, integer=True)), energy_cost, _strings(row, "cancel_on_hit", source), _strings(row, "cancel_on_block", source), properties, _require_string(row, "legacy_action_name", source), tuple(hitbox),int(row.get("cancel_start_frame",0)),int(row.get("cancel_end_frame",0)),int(row.get("hit_stop_frames",3)),int(row.get("block_stop_frames",2)),float(movement.get("x_per_frame",0)),float(movement.get("y_per_frame",0)),bool(row.get("can_turn",False)),bool(row.get("can_hit_once",True)),hitboxes,hurtboxes,armor,tuple(invulnerability),projectile,int(row.get("multi_hit_interval_frames",1)))

    def _combo(self, row: dict[str, object], source: str) -> ComboDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        inputs = _strings(row, "inputs", source)
        if not inputs:
            raise ContentValidationError(f"{source}: combo '{content_id}' inputs cannot be empty")
        gap = int(_number(row, "max_gap_frames", source, integer=True))
        meter = int(_number(row, "meter_cost", source, integer=True))
        if not 1 <= gap <= 300 or meter < 0:
            raise ContentValidationError(f"{source}: combo '{content_id}' has invalid gap or meter cost")
        return ComboDefinition(content_id, _require_string(row, "owner_id", source), _require_string(row, "display_name_key", source), inputs, gap, _require_string(row, "required_state", source), _require_string(row, "resulting_attack_id", source), meter, _boolean(row, "enabled", source), int(row.get("priority", 0)))

    def _arena(self, row: dict[str, object], localization: LocalizationManager, source: str) -> ArenaDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        name_key = _require_string(row, "name_key", source); description_key = _require_string(row, "description_key", source)
        style = _require_string(row, "procedural_style", source)
        if style not in PROCEDURAL_STYLES:
            raise ContentValidationError(f"{source}: arena '{content_id}' has unknown procedural_style '{style}'")
        left = float(_number(row, "left_boundary", source)); right = float(_number(row, "right_boundary", source))
        if left >= right:
            raise ContentValidationError(f"{source}: arena '{content_id}' left_boundary must be less than right_boundary")
        return ArenaDefinition(content_id, name_key, description_key, _require_string(row, "preview", source, allow_empty=True), _strings(row, "background_layers", source), float(_number(row, "ground_y", source)), left, right, _require_string(row, "music", source, allow_empty=True), _require_string(row, "ambience", source, allow_empty=True), _boolean(row, "hazards_enabled_by_default", source), style, _boolean(row, "unlocked_by_default", source), _palette(row.get("palette"), source, content_id), _require_string(row, "hazard", source), localization.get(name_key), localization.get(description_key))

    def _validate_references(self, fighters, attacks, combos, arenas, localization, source) -> None:
        for attack in attacks.values():
            if attack.owner_id != "common" and attack.owner_id not in fighters:
                raise MissingContentReferenceError(f"{source}: attack '{attack.id}' references unknown owner '{attack.owner_id}'")
            for target in attack.cancel_on_hit + attack.cancel_on_block:
                if target not in attacks:
                    raise MissingContentReferenceError(f"{source}: attack '{attack.id}' references unknown cancel attack '{target}'")
            if not localization.has(attack.display_name_key):
                raise MissingContentReferenceError(f"{source}: attack '{attack.id}' references unknown localization key '{attack.display_name_key}'")
        sequences: set[tuple[str, tuple[str, ...], int]] = set()
        for combo in combos.values():
            if combo.owner_id != "common" and combo.owner_id not in fighters:
                raise MissingContentReferenceError(f"{source}: combo '{combo.id}' references unknown owner '{combo.owner_id}'")
            attack = attacks.get(combo.resulting_attack_id)
            if attack is None:
                raise MissingContentReferenceError(f"{source}: combo '{combo.id}' references unknown result '{combo.resulting_attack_id}'")
            if attack.owner_id not in {"common", combo.owner_id} and combo.owner_id != "common":
                raise MissingContentReferenceError(f"{source}: combo '{combo.id}' cannot use attack owned by '{attack.owner_id}'")
            signature = (combo.owner_id, combo.inputs, combo.priority)
            if signature in sequences:
                raise ContentValidationError(f"{source}: conflicting combo input sequence for '{combo.owner_id}'")
            sequences.add(signature)
            if not localization.has(combo.display_name_key):
                raise MissingContentReferenceError(f"{source}: combo '{combo.id}' has unknown localization key")
        for fighter in fighters.values():
            for attack_id in fighter.attack_ids + fighter.special_ids + (fighter.super_attack_id,):
                if attack_id not in attacks:
                    raise MissingContentReferenceError(f"{source}: fighter '{fighter.id}' references unknown attack '{attack_id}'")
            for combo_id in fighter.combo_ids:
                if combo_id not in combos:
                    raise MissingContentReferenceError(f"{source}: fighter '{fighter.id}' references unknown combo '{combo_id}'")
        for arena in arenas.values():
            if not localization.has(arena.name_key) or not localization.has(arena.description_key):
                raise MissingContentReferenceError(f"{source}: arena '{arena.id}' references unknown localization key")

    def get_fighter(self, fighter_id: str) -> FighterDefinition:
        return self._get("fighter", fighter_id, self.fighters, "fighters.json")
    def get_attack(self, attack_id: str) -> AttackDefinition:
        return self._get("attack", attack_id, self.attacks, "attacks.json")
    def get_combo(self, combo_id: str) -> ComboDefinition:
        return self._get("combo", combo_id, self.combos, "combos.json")
    def get_arena(self, arena_id: str) -> ArenaDefinition:
        return self._get("arena", arena_id, self.arenas, "arenas.json")
    def has_fighter(self, fighter_id: str) -> bool:
        return fighter_id in self.fighters
    def has_arena(self, arena_id: str) -> bool:
        return arena_id in self.arenas
    def _get(self, kind: str, content_id: str, mapping: dict, filename: str):
        try:
            return mapping[content_id]
        except KeyError as exc:
            suggestions = difflib.get_close_matches(content_id, mapping, n=3)
            suffix = f"; closest: {', '.join(suggestions)}" if suggestions else ""
            raise MissingContentReferenceError(f"Unknown {kind} id '{content_id}' in {self.data_dir / filename}{suffix}") from exc


def _require_string(row, field, source, *, allow_empty=False):
    value = row.get(field)
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        raise ContentValidationError(f"{source}: field '{field}' must be a {'string' if allow_empty else 'non-empty string'}")
    return value
def _valid_id(value, source):
    if not ID_PATTERN.fullmatch(value): raise ContentValidationError(f"{source}: invalid content id '{value}'")
def _number(row, field, source, *, integer=False):
    value = row.get(field)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or (integer and not isinstance(value, int)): raise ContentValidationError(f"{source}: field '{field}' must be numeric")
    return value
def _strings(row, field, source):
    value = row.get(field)
    if not isinstance(value, list) or any(not isinstance(item, str) for item in value): raise ContentValidationError(f"{source}: field '{field}' must be a string list")
    return tuple(value)
def _dict(row, field, source):
    value = row.get(field)
    if not isinstance(value, dict): raise ContentValidationError(f"{source}: field '{field}' must be an object")
    return dict(value)
def _boolean(row, field, source):
    value = row.get(field)
    if not isinstance(value, bool): raise ContentValidationError(f"{source}: field '{field}' must be boolean")
    return value
def _palette(value, source, content_id):
    if not isinstance(value, list) or len(value) != 3 or any(not isinstance(c, list) or len(c) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in c) for c in value): raise ContentValidationError(f"{source}: '{content_id}' palette must contain three RGB colors")
    return tuple(tuple(c) for c in value)

def _frame_mapping(value,source,content_id,total,field):
    if not isinstance(value,dict):raise ContentValidationError(f"{source}: attack '{content_id}' {field} must be an object")
    result=[]
    for key,rows in value.items():
        try:frame=int(key)
        except (TypeError,ValueError):raise ContentValidationError(f"{source}: attack '{content_id}' has invalid frame '{key}'")
        if not 0<=frame<total or not isinstance(rows,list) or any(not isinstance(x,dict) for x in rows):raise ContentValidationError(f"{source}: invalid {field} frame {frame} in '{content_id}'")
        result.append((frame,tuple(dict(x) for x in rows)))
    return tuple(sorted(result))

def _frame_list(value,source,content_id,total,field):
    if not isinstance(value,list) or any(not isinstance(x,int) or not 0<=x<total for x in value):raise ContentValidationError(f"{source}: invalid {field} in '{content_id}'")
    return tuple(value)

def _projectile(value,source,content_id,total):
    if value is None:return None
    if not isinstance(value,dict):raise ContentValidationError(f"{source}: projectile_definition in '{content_id}' must be an object or null")
    required={"projectile_id","spawn_frame","offset_x","offset_y","velocity_x","velocity_y","acceleration_x","acceleration_y","lifetime_frames","width","height","damage","chip_damage","hit_level","hit_stun_frames","block_stun_frames","priority","durability","multi_hit","multi_hit_interval_frames","destroy_on_hit","destroy_on_block","destroy_outside_arena","properties"}
    missing=required-value.keys()
    if missing:raise ContentValidationError(f"{source}: projectile in '{content_id}' missing {sorted(missing)}")
    if not 0<=value["spawn_frame"]<total or value["lifetime_frames"]<=0 or value["width"]<=0 or value["height"]<=0 or value["durability"]<=0 or value["priority"]<0 or value["damage"]<0 or not 0<=value["chip_damage"]<=value["damage"]:raise ContentValidationError(f"{source}: invalid projectile values in '{content_id}'")
    if value["hit_level"] not in HIT_LEVELS or not isinstance(value["properties"],list) or set(value["properties"])-PROJECTILE_PROPERTIES:raise ContentValidationError(f"{source}: invalid projectile level/properties in '{content_id}'")
    if value["multi_hit"] and value["multi_hit_interval_frames"]<=0:raise ContentValidationError(f"{source}: invalid projectile multi-hit interval in '{content_id}'")
    return dict(value)


_DEFAULT_REGISTRY: ContentRegistry | None = None
def get_default_registry() -> ContentRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = ContentRegistry()
        _DEFAULT_REGISTRY.load_all()
    return _DEFAULT_REGISTRY
