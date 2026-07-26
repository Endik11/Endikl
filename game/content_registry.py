from __future__ import annotations

import difflib
import re
from pathlib import Path

from .content_errors import ContentError, ContentValidationError, MissingContentReferenceError
from .data_loader import DataLoader
from .debug import log_critical, log_error, log_event, log_warning
from .definitions import (
    AnimationDefinition,
    AnimationKeyframeDefinition,
    ArenaDefinition,
    ArenaVisualDefinition,
    AttackDefinition,
    BoneDefinition,
    ComboDefinition,
    EffectDefinition,
    FighterDefinition,
    FighterVisualDefinition,
    HudDefinition,
    RigDefinition,
)
from .fallback_content import (
    FALLBACK_ARENAS,
    FALLBACK_ATTACKS,
    FALLBACK_COMBOS,
    FALLBACK_FIGHTERS,
    FALLBACK_LOCALIZATION,
)
from .localization import LocalizationManager
from .settings import MAX_ENERGY, ROOT_DIR
from .platform_paths import data_path


ID_PATTERN = re.compile(r"^[a-z0-9_]+$")
HIT_LEVELS = {"high", "mid", "low", "overhead", "throw", "unblockable"}
ATTACK_PROPERTIES = {"launcher", "knockdown", "projectile", "armor", "invulnerable", "multi_hit", "air_only", "crouch_only", "special", "enhanced", "super"}
PROJECTILE_PROPERTIES = {"pierce","multi_hit","unblockable","armor_break","chip_kill"}
PROCEDURAL_STYLES = {"foundry", "pier", "court", "wall", "mountains", "pagoda"}


class ContentRegistry:
    def __init__(self, data_dir: Path | None = None, *, allow_fallback: bool = True) -> None:
        self.data_dir = Path(data_dir or data_path())
        self.allow_fallback = allow_fallback
        self.fighters: dict[str, FighterDefinition] = {}
        self.attacks: dict[str, AttackDefinition] = {}
        self.combos: dict[str, ComboDefinition] = {}
        self.arenas: dict[str, ArenaDefinition] = {}
        self.rigs: dict[str, RigDefinition] = {}
        self.fighter_visuals: dict[str, FighterVisualDefinition] = {}
        self.arena_visuals: dict[str, ArenaVisualDefinition] = {}
        self.animations: dict[str, AnimationDefinition] = {}
        self.effects: dict[str, EffectDefinition] = {}
        self.hud: HudDefinition | None = None
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
                None,
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
            self._load_visual_rows(loader),
            source=str(self.data_dir),
        )

    def _load_visual_rows(self, loader: DataLoader):
        filenames = ("visuals.json", "animations.json", "effects.json", "hud.json")
        if any(not (loader.data_dir / filename).is_file() for filename in filenames):
            log_warning("Visual data files are incomplete; using procedural visual fallback from content ids")
            return None
        return {
            "rigs": loader.load_records("visuals.json", "rigs"),
            "fighters": loader.load_records("visuals.json", "fighters"),
            "arenas": loader.load_records("visuals.json", "arenas"),
            "animations": loader.load_records("animations.json", "animations"),
            "effects": loader.load_records("effects.json", "effects"),
            "hud": loader.load_records("hud.json", "hud"),
        }

    def _build_content(self, fighter_rows, attack_rows, combo_rows, arena_rows, strings, visual_rows, *, source: str):
        fighter_values = [self._fighter(row, source) for row in fighter_rows]
        attack_values = [self._attack(row, source) for row in attack_rows]
        combo_values = [self._combo(row, source) for row in combo_rows]
        fighters = {item.id: item for item in fighter_values}
        attacks = {item.id: item for item in attack_values}
        combos = {item.id: item for item in combo_values}
        localization = LocalizationManager(strings)
        arena_values = [self._arena(row, localization, source) for row in arena_rows]
        arenas = {item.id: item for item in arena_values}
        visual_rows = visual_rows or _generated_visual_rows(tuple(fighters), tuple(arenas))
        rigs, fighter_visuals, arena_visuals, animations, effects, hud = self._visuals(visual_rows, source)
        self._validate_references(fighters, attacks, combos, arenas, localization, rigs, fighter_visuals, arena_visuals, animations, source)
        return fighters, attacks, combos, arenas, strings, rigs, fighter_visuals, arena_visuals, animations, effects, hud

    def _apply(self, content) -> None:
        fighters, attacks, combos, arenas, strings, rigs, fighter_visuals, arena_visuals, animations, effects, hud = content
        self.fighters.clear(); self.fighters.update(fighters)
        self.attacks.clear(); self.attacks.update(attacks)
        self.combos.clear(); self.combos.update(combos)
        self.arenas.clear(); self.arenas.update(arenas)
        self.rigs.clear(); self.rigs.update(rigs)
        self.fighter_visuals.clear(); self.fighter_visuals.update(fighter_visuals)
        self.arena_visuals.clear(); self.arena_visuals.update(arena_visuals)
        self.animations.clear(); self.animations.update(animations)
        self.effects.clear(); self.effects.update(effects)
        self.hud = hud
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

    def _visuals(self, rows, source: str):
        rigs = {item.id: item for item in (self._rig(row, source) for row in rows["rigs"])}
        fighter_visuals = {item.fighter_id: item for item in (self._fighter_visual(row, source) for row in rows["fighters"])}
        arena_visuals = {item.arena_id: item for item in (self._arena_visual(row, source) for row in rows["arenas"])}
        animations = {item.id: item for item in (self._animation(row, source) for row in rows["animations"])}
        effects = {item.id: item for item in (self._effect(row, source) for row in rows["effects"])}
        hud_values = [self._hud(row, source) for row in rows["hud"]]
        if len(hud_values) != 1:
            raise ContentValidationError(f"{source}: hud.json must define exactly one hud")
        return rigs, fighter_visuals, arena_visuals, animations, effects, hud_values[0]

    def _rig(self, row, source: str) -> RigDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        bones = row.get("bones")
        if not isinstance(bones, list) or not bones:
            raise ContentValidationError(f"{source}: rig '{content_id}' bones must be a non-empty list")
        parsed = tuple(self._bone(dict(item), source, content_id) for item in bones if isinstance(item, dict))
        if len(parsed) != len(bones):
            raise ContentValidationError(f"{source}: rig '{content_id}' has invalid bone rows")
        ids = {bone.id for bone in parsed}
        if len(ids) != len(parsed) or "root" not in ids:
            raise ContentValidationError(f"{source}: rig '{content_id}' must contain unique bones and root")
        for bone in parsed:
            if bone.parent and bone.parent not in ids:
                raise MissingContentReferenceError(f"{source}: rig '{content_id}' bone '{bone.id}' references unknown parent '{bone.parent}'")
        return RigDefinition(content_id, tuple(sorted(parsed, key=lambda bone: bone.draw_order)))

    def _bone(self, row, source: str, rig_id: str) -> BoneDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        parent = _require_string(row, "parent", source, allow_empty=True)
        return BoneDefinition(
            content_id,
            parent,
            _point(row.get("local_position"), source, f"{rig_id}.{content_id}.local_position"),
            float(_number(row, "rotation", source)),
            _point(row.get("scale"), source, f"{rig_id}.{content_id}.scale", default=(1.0, 1.0)),
            float(_number(row, "length", source)),
            float(_number(row, "thickness", source)),
            _point(row.get("pivot"), source, f"{rig_id}.{content_id}.pivot", default=(0.0, 0.0)),
            _require_string(row, "shape", source),
            int(_number(row, "draw_order", source, integer=True)),
            _require_string(row, "palette_role", source),
            _require_string(row, "attachment", source, allow_empty=True),
        )

    def _fighter_visual(self, row, source: str) -> FighterVisualDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        return FighterVisualDefinition(
            content_id,
            _require_string(row, "fighter_id", source),
            _require_string(row, "rig_id", source),
            _require_string(row, "silhouette", source),
            _require_string(row, "stance", source),
            float(_number(row, "scale", source)),
            _require_string(row, "idle_clip", source),
            _require_string(row, "walk_clip", source),
            _require_string(row, "attack_clip", source),
            _require_string(row, "victory_clip", source),
            _require_string(row, "defeat_clip", source),
            _palette_dict(row.get("palette_roles"), source, content_id),
            tuple(_strings(row, "attachments", source)),
            _require_string(row, "effect_style", source),
        )

    def _arena_visual(self, row, source: str) -> ArenaVisualDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        layers = row.get("layers")
        if not isinstance(layers, list) or any(not isinstance(layer, dict) for layer in layers):
            raise ContentValidationError(f"{source}: arena visual '{content_id}' layers must be objects")
        return ArenaVisualDefinition(
            content_id,
            _require_string(row, "arena_id", source),
            _require_string(row, "style", source),
            _palette(row.get("palette"), source, content_id),
            tuple(dict(layer) for layer in layers),
            _require_string(row, "particle_style", source),
            _color(row.get("light_color"), source, f"{content_id}.light_color"),
            _color(row.get("shadow_color"), source, f"{content_id}.shadow_color"),
        )

    def _animation(self, row, source: str) -> AnimationDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        keyframes = row.get("keyframes")
        if not isinstance(keyframes, list):
            raise ContentValidationError(f"{source}: animation '{content_id}' keyframes must be a list")
        parsed = tuple(self._keyframe(dict(item), source, content_id) for item in keyframes if isinstance(item, dict))
        if len(parsed) != len(keyframes):
            raise ContentValidationError(f"{source}: animation '{content_id}' has invalid keyframes")
        duration = int(_number(row, "duration_frames", source, integer=True))
        if duration <= 0:
            raise ContentValidationError(f"{source}: animation '{content_id}' duration must be positive")
        events = row.get("events", [])
        if not isinstance(events, list) or any(not isinstance(event, dict) for event in events):
            raise ContentValidationError(f"{source}: animation '{content_id}' events must be objects")
        return AnimationDefinition(
            content_id,
            _require_string(row, "state", source),
            duration,
            _boolean(row, "loop", source),
            float(_number(row, "playback_speed", source)),
            int(_number(row, "priority", source, integer=True)),
            int(_number(row, "blend_frames", source, integer=True)),
            _boolean(row, "restart", source),
            _boolean(row, "freeze_on_hit_stop", source),
            tuple(sorted(parsed, key=lambda item: (item.bone_id, item.frame))),
            tuple(dict(event) for event in events),
        )

    def _keyframe(self, row, source: str, animation_id: str) -> AnimationKeyframeDefinition:
        frame = int(_number(row, "frame", source, integer=True))
        if frame < 0:
            raise ContentValidationError(f"{source}: animation '{animation_id}' has negative keyframe")
        return AnimationKeyframeDefinition(
            frame,
            _require_string(row, "bone_id", source),
            _point(row.get("translation"), source, f"{animation_id}.translation"),
            float(_number(row, "rotation", source)),
            _point(row.get("scale"), source, f"{animation_id}.scale", default=(1.0, 1.0)),
            float(row.get("alpha", 1.0)),
        )

    def _effect(self, row, source: str) -> EffectDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        return EffectDefinition(
            content_id,
            _require_string(row, "event", source),
            int(_number(row, "particle_count", source, integer=True)),
            int(_number(row, "lifetime_frames", source, integer=True)),
            float(_number(row, "speed", source)),
            _color(row.get("color"), source, f"{content_id}.color"),
            _color(row.get("secondary_color"), source, f"{content_id}.secondary_color"),
            float(_number(row, "radius", source)),
            bool(row.get("pooled", True)),
        )

    def _hud(self, row, source: str) -> HudDefinition:
        content_id = _require_string(row, "id", source); _valid_id(content_id, source)
        keys = row.get("announcer_keys")
        if not isinstance(keys, dict) or any(not isinstance(k, str) or not isinstance(v, str) for k, v in keys.items()):
            raise ContentValidationError(f"{source}: hud '{content_id}' announcer_keys must map strings")
        return HudDefinition(
            content_id,
            int(_number(row, "health_width", source, integer=True)),
            int(_number(row, "meter_segments", source, integer=True)),
            int(_number(row, "meter_max", source, integer=True)),
            _require_string(row, "font_family", source),
            _palette_dict(row.get("palette"), source, content_id),
            dict(keys),
        )

    def _validate_references(self, fighters, attacks, combos, arenas, localization, rigs, fighter_visuals, arena_visuals, animations, source) -> None:
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
        for fighter_id in fighters:
            visual = fighter_visuals.get(fighter_id)
            if visual is None:
                raise MissingContentReferenceError(f"{source}: fighter '{fighter_id}' has no visual definition")
            if visual.rig_id not in rigs:
                raise MissingContentReferenceError(f"{source}: fighter visual '{visual.id}' references unknown rig")
            for clip in (visual.idle_clip, visual.walk_clip, visual.attack_clip, visual.victory_clip, visual.defeat_clip):
                if clip not in animations:
                    raise MissingContentReferenceError(f"{source}: fighter visual '{visual.id}' references unknown animation '{clip}'")
        for arena_id in arenas:
            if arena_id not in arena_visuals:
                raise MissingContentReferenceError(f"{source}: arena '{arena_id}' has no visual definition")

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
def _color(value, source, field):
    if not isinstance(value, list) or len(value) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in value): raise ContentValidationError(f"{source}: '{field}' must be an RGB color")
    return tuple(value)
def _palette_dict(value, source, content_id):
    if not isinstance(value, dict) or not value:
        raise ContentValidationError(f"{source}: '{content_id}' palette roles must be an object")
    return {str(key): _color(color, source, f"{content_id}.{key}") for key, color in value.items()}
def _point(value, source, field, *, default=None):
    if value is None and default is not None:
        return default
    if not isinstance(value, list) or len(value) != 2 or any(isinstance(v, bool) or not isinstance(v, (int, float)) for v in value):
        raise ContentValidationError(f"{source}: '{field}' must be a two-number point")
    return float(value[0]), float(value[1])

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

def _generated_visual_rows(fighter_ids: tuple[str, ...], arena_ids: tuple[str, ...]):
    bones = [
        ("root", "", [0, 0], 0, 0, 0, "circle", 0, "shadow"),
        ("pelvis", "root", [0, -92], 0, 34, 24, "ellipse", 1, "cloth"),
        ("torso_lower", "pelvis", [0, -28], -4, 42, 26, "capsule", 2, "secondary"),
        ("torso_upper", "torso_lower", [0, -36], 2, 52, 32, "capsule", 3, "primary"),
        ("neck", "torso_upper", [0, -34], 0, 12, 12, "capsule", 4, "secondary"),
        ("head", "neck", [0, -22], 0, 30, 28, "ellipse", 5, "skin"),
        ("left_shoulder", "torso_upper", [-28, -26], -12, 12, 12, "circle", 6, "secondary"),
        ("left_upper_arm", "left_shoulder", [-16, 26], -18, 42, 14, "capsule", 7, "primary"),
        ("left_forearm", "left_upper_arm", [-10, 38], -8, 38, 12, "capsule", 8, "secondary"),
        ("left_hand", "left_forearm", [-4, 34], 0, 12, 12, "circle", 9, "accent"),
        ("right_shoulder", "torso_upper", [28, -26], 12, 12, 12, "circle", 6, "secondary"),
        ("right_upper_arm", "right_shoulder", [16, 26], 18, 42, 14, "capsule", 7, "primary"),
        ("right_forearm", "right_upper_arm", [10, 38], 8, 38, 12, "capsule", 8, "secondary"),
        ("right_hand", "right_forearm", [4, 34], 0, 12, 12, "circle", 9, "accent"),
        ("left_thigh", "pelvis", [-16, 26], -6, 52, 16, "capsule", 10, "primary"),
        ("left_shin", "left_thigh", [-4, 50], 3, 52, 13, "capsule", 11, "secondary"),
        ("left_foot", "left_shin", [-8, 50], -8, 24, 10, "capsule", 12, "accent"),
        ("right_thigh", "pelvis", [16, 26], 6, 52, 16, "capsule", 10, "primary"),
        ("right_shin", "right_thigh", [4, 50], -3, 52, 13, "capsule", 11, "secondary"),
        ("right_foot", "right_shin", [8, 50], 8, 24, 10, "capsule", 12, "accent"),
        ("weapon", "right_hand", [12, -8], 18, 44, 5, "blade", 13, "accent"),
        ("cloth_left", "pelvis", [-24, -6], -18, 42, 7, "ribbon", 14, "cloth"),
        ("cloth_right", "pelvis", [24, -6], 18, 42, 7, "ribbon", 14, "cloth"),
        ("hair", "head", [0, -22], 0, 24, 9, "ribbon", 15, "secondary"),
        ("cape", "torso_upper", [0, -18], 0, 72, 8, "ribbon", 0, "cloth"),
        ("armor", "torso_upper", [24, -18], 12, 30, 12, "plate", 16, "secondary"),
        ("energy_core", "torso_upper", [0, -14], 0, 14, 14, "circle", 17, "accent"),
    ]
    rig = {
        "id": "default_humanoid",
        "bones": [
            {
                "id": bone_id,
                "parent": parent,
                "local_position": position,
                "rotation": rotation,
                "scale": [1, 1],
                "length": length,
                "thickness": thickness,
                "pivot": [0, 0],
                "shape": shape,
                "draw_order": order,
                "palette_role": role,
                "attachment": "",
            }
            for bone_id, parent, position, rotation, length, thickness, shape, order, role in bones
        ],
    }
    palettes = {
        "kael": {"primary": [205, 58, 65], "secondary": [232, 181, 82], "accent": [238, 241, 244], "cloth": [35, 38, 46], "skin": [196, 150, 118], "shadow": [0, 0, 0]},
        "sable": {"primary": [63, 201, 197], "secondary": [142, 104, 207], "accent": [232, 181, 82], "cloth": [24, 28, 36], "skin": [164, 120, 112], "shadow": [0, 0, 0]},
        "orrin": {"primary": [90, 191, 118], "secondary": [176, 186, 192], "accent": [232, 181, 82], "cloth": [28, 33, 30], "skin": [170, 128, 96], "shadow": [0, 0, 0]},
        "mira": {"primary": [79, 150, 214], "secondary": [238, 241, 244], "accent": [63, 201, 197], "cloth": [26, 31, 45], "skin": [198, 136, 120], "shadow": [0, 0, 0]},
        "lin": {"primary": [188, 94, 68], "secondary": [242, 202, 132], "accent": [90, 191, 118], "cloth": [26, 26, 34], "skin": [202, 146, 102], "shadow": [0, 0, 0]},
        "ren_kaido": {"primary": [35, 61, 102], "secondary": [181, 126, 67], "accent": [87, 202, 236], "cloth": [18, 24, 38], "skin": [172, 122, 92], "shadow": [0, 0, 0]},
    }
    silhouettes = {
        "kael": ("ash_guard", 1.0, ["armor", "energy_core"]),
        "sable": ("veil_runner", 0.92, ["cloth_left", "cloth_right", "hair"]),
        "orrin": ("iron_monk", 1.1, ["armor"]),
        "mira": ("storm_dancer", 0.96, ["cloth_left", "hair", "energy_core"]),
        "lin": ("wind_disciple", 0.98, ["cloth_right", "weapon"]),
        "ren_kaido": ("storm_warden", 1.06, ["armor", "cloth_left", "cloth_right", "energy_core"]),
    }
    fighters = []
    for fighter_id in fighter_ids:
        silhouette, scale, attachments = silhouettes.get(fighter_id, ("guardian", 1.0, ["energy_core"]))
        fighters.append({
            "id": f"{fighter_id}_visual",
            "fighter_id": fighter_id,
            "rig_id": "default_humanoid",
            "silhouette": silhouette,
            "stance": "offset_guard",
            "scale": scale,
            "idle_clip": "idle",
            "walk_clip": "walk_forward",
            "attack_clip": "strike_flash",
            "victory_clip": "victory",
            "defeat_clip": "defeat",
            "palette_roles": palettes.get(fighter_id, palettes["kael"]),
            "attachments": attachments,
            "effect_style": "rune_sparks",
        })
    arena_palette = {
        "neon_foundry": [[16, 20, 24], [207, 53, 63], [63, 201, 197]],
        "storm_pier": [[10, 18, 28], [79, 150, 214], [232, 181, 82]],
        "glass_court": [[24, 24, 31], [142, 104, 207], [238, 241, 244]],
        "great_wall": [[18, 24, 34], [164, 112, 62], [232, 181, 82]],
        "dragon_mountains": [[12, 22, 30], [90, 164, 122], [217, 232, 238]],
        "pagoda_ridge": [[12, 16, 24], [163, 86, 164], [242, 202, 132]],
    }
    arenas = [
        {
            "id": f"{arena_id}_visual",
            "arena_id": arena_id,
            "style": arena_id,
            "palette": arena_palette.get(arena_id, arena_palette["neon_foundry"]),
            "layers": [
                {"kind": "sky", "parallax": 0.15, "density": 5},
                {"kind": "mid", "parallax": 0.45, "density": 8},
                {"kind": "front", "parallax": 0.8, "density": 12},
            ],
            "particle_style": "embers",
            "light_color": [242, 202, 132],
            "shadow_color": [0, 0, 0],
        }
        for arena_id in arena_ids
    ]
    animations = [
        _animation_row("idle", "IDLE", 54, True, [("torso_upper", 0, [0, 0], -2), ("torso_upper", 27, [0, -5], 2), ("head", 27, [0, -2], -1)]),
        _animation_row("walk_forward", "WALK_FORWARD", 32, True, [("left_thigh", 0, [-6, 0], -14), ("right_thigh", 0, [6, 0], 14), ("left_thigh", 16, [6, 0], 14), ("right_thigh", 16, [-6, 0], -14)]),
        _animation_row("strike_flash", "ATTACK_ACTIVE", 24, False, [("right_forearm", 0, [0, 0], 10), ("right_forearm", 8, [18, -4], -36), ("right_forearm", 18, [0, 0], 0)]),
        _animation_row("victory", "VICTORY", 80, True, [("right_hand", 0, [0, 0], 0), ("right_hand", 24, [8, -42], -30), ("head", 24, [0, -4], 4)]),
        _animation_row("defeat", "DEFEAT", 60, False, [("torso_upper", 0, [0, 0], 0), ("torso_upper", 40, [0, 42], 84), ("head", 40, [16, 24], 50)]),
        _animation_row("crouch", "CROUCH", 20, True, [("pelvis", 0, [0, 18], 0), ("torso_upper", 0, [0, 10], -8)]),
        _animation_row("airborne", "AIRBORNE", 24, True, [("left_thigh", 0, [0, 0], 24), ("right_thigh", 0, [0, 0], -24)]),
        _animation_row("block_high", "BLOCK", 20, True, [("left_forearm", 0, [14, -12], -60), ("right_forearm", 0, [-14, -12], 60)]),
    ]
    effects = [
        {"id": "light_hit_spark", "event": "ATTACK_HIT", "particle_count": 14, "lifetime_frames": 18, "speed": 5, "color": [242, 202, 132], "secondary_color": [238, 241, 244], "radius": 4, "pooled": True},
        {"id": "block_spark", "event": "ATTACK_BLOCKED", "particle_count": 10, "lifetime_frames": 15, "speed": 4, "color": [79, 150, 214], "secondary_color": [238, 241, 244], "radius": 3, "pooled": True},
        {"id": "projectile_impact", "event": "PROJECTILE_HIT", "particle_count": 18, "lifetime_frames": 20, "speed": 6, "color": [87, 202, 236], "secondary_color": [142, 104, 207], "radius": 5, "pooled": True},
        {"id": "throw_impact", "event": "THROW", "particle_count": 16, "lifetime_frames": 18, "speed": 5, "color": [207, 53, 63], "secondary_color": [232, 181, 82], "radius": 5, "pooled": True},
    ]
    hud = [{
        "id": "default_hud",
        "health_width": 360,
        "meter_segments": 3,
        "meter_max": 3000,
        "font_family": "Segoe UI",
        "palette": {"health": [207, 53, 63], "recoverable": [232, 181, 82], "meter": [63, 201, 197], "panel": [26, 30, 36], "text": [238, 241, 244]},
        "announcer_keys": {"round": "announcer.round", "ready": "announcer.ready", "fight": "announcer.fight", "ko": "announcer.ko", "draw": "announcer.draw", "double_ko": "announcer.double_ko", "sudden_death": "announcer.sudden_death", "victory": "announcer.victory", "shadow_finish": "finish.shadow"},
    }]
    return {"rigs": [rig], "fighters": fighters, "arenas": arenas, "animations": animations, "effects": effects, "hud": hud}

def _animation_row(content_id, state, duration, loop, keys):
    return {
        "id": content_id,
        "state": state,
        "duration_frames": duration,
        "loop": loop,
        "playback_speed": 1.0,
        "priority": 1,
        "blend_frames": 4,
        "restart": False,
        "freeze_on_hit_stop": True,
        "keyframes": [
            {"bone_id": bone, "frame": frame, "translation": translation, "rotation": rotation, "scale": [1, 1], "alpha": 1.0}
            for bone, frame, translation, rotation in keys
        ],
        "events": [],
    }


_DEFAULT_REGISTRY: ContentRegistry | None = None
def get_default_registry() -> ContentRegistry:
    global _DEFAULT_REGISTRY
    if _DEFAULT_REGISTRY is None:
        _DEFAULT_REGISTRY = ContentRegistry()
        _DEFAULT_REGISTRY.load_all()
    return _DEFAULT_REGISTRY
