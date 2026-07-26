# Architecture — Stage 2

## Before the refactor

`main.py` created `GameEngine`, while `game/engine.py` owned the window, input,
audio, state strings, menus, match lifecycle, combat update and rendering. A
single `if/elif` dispatcher selected behavior from string values. `game/menu.py`
contained almost every non-combat screen plus common UI and arena data. Screen
transitions mutated engine state directly, so Character Select could create a
match before Arena Select and Arena Select could create it a second time.

## After the refactor

`main.py` remains the stable entry point and only creates and runs
`GameEngine`. The engine is the composition root and temporary owner of legacy
combat. It polls input, asks the active screen to update/draw, applies one
deferred transition, and presents the virtual frame.

- `game/enums.py` defines typed game, mode, round, fighter, attack and hit
  states. Conversion helpers accept known legacy strings and reject unknown
  values.
- `game/state_manager.py` owns screen registration, active state, deferred
  changes, lifecycle calls and back history. It contains no menu or combat
  rules.
- `game/screens/base_screen.py` defines the lifecycle contract without importing
  `GameEngine`.
- `game/screen_context.py` is the narrow dependency bundle provided to screens.
  It exposes managers, session, input view, exit callback and the temporary
  match runtime protocol—not the engine.
- `game/session.py` holds typed, serializable selections and transient match
  data. It never stores surfaces, channels, managers or screens.
- `game/display_manager.py` owns the 1280×720 virtual surface, physical window,
  proportional presentation, letterbox viewport, resizing and coordinate
  conversion.
- `game/audio_manager.py` is the safe audio facade. `ToneBank` remains its
  procedural fallback and audio failures are degraded to one-time warnings.
- `game/input_manager.py` owns input snapshots. `InputRouter` remains an alias.
- `game/match_runtime.py` defines the narrow match protocol.
  `CallbackMatchRuntime` is the explicit Stage 2 adapter to combat code still in
  `GameEngine`.
- `game/arena_catalog.py` owns arena definitions; `game/screens/ui_helpers.py`
  owns shared non-screen drawing and menu helpers.
- `game/screens/*_screen.py` contains one screen responsibility per module.
  Fight, Pause and Result delegate only through `MatchRuntime`.
- `game/menu.py` is now a compatibility re-export module.

## Dependency direction

```text
main.py
  -> GameEngine (composition root)
      -> StateManager -> BaseScreen implementations
      -> ScreenContext -> manager/protocol interfaces
      -> DisplayManager / AudioManager / InputManager
      -> CallbackMatchRuntime -> legacy combat methods

screens -> ScreenContext + enums + session/domain data
screens -X-> GameEngine
StateManager -X-> concrete screen behavior
GameSession -X-> pygame and service objects
```

Transitions are requested during event/update handling and applied by the
engine after update. `exit()` runs on the old screen, history is updated, the
new state becomes active, and `enter(payload)` runs on the new screen. Recursive
or unregistered transitions fail explicitly.

## Match selection flow

```text
MAIN_MENU
  -> CHARACTER_SELECT (mode stored in GameSession)
  -> ARENA_SELECT (both fighter keys stored; no match exists yet)
  -> FIGHT (arena stored; MatchRuntime.start_match called exactly once)
  -> PAUSE -> FIGHT
  -> RESULT -> FIGHT (next ladder opponent) or MAIN_MENU
```

Local versus requires independent confirmation from player one and player two.
Only Arena Select is authorized to call `start_match`, and its `_starting` guard
prevents duplicate creation.

## Letterbox calculation

For physical size `(W, H)`, the display manager uses
`scale = min(W / 1280, H / 720)`. The viewport is the centered rounded size
`(1280 * scale, 720 * scale)`. Presentation clears the physical window to black
and draws only inside that viewport. Mouse conversion first subtracts the
viewport offset; coordinates in a black bar return `None`.

## Compatibility retained

- Public launch remains `python main.py`.
- `game.menu` re-exports `MenuScreen`, all migrated screen classes, arenas and
  shared UI helpers used by existing imports and tests.
- `MenuScreen` aliases `MainMenuScreen`.
- `InputRouter` aliases `InputManager`.
- `ToneBank` remains available in `game.audio_manager` and backs
  `AudioManager`.
- Migrated screen `update` and `draw` methods still accept their legacy call
  shapes when instantiated without a `ScreenContext`.
- Legacy string parsing is centralized in strict conversion helpers.

## Deliberately remaining after Stage 2

Combat update/rendering and `MatchContext` remain in `GameEngine` behind
`CallbackMatchRuntime`; extracting the combat domain would change a larger risk
surface and belongs to a later stage. Several menu labels and all procedural
visuals remain as they were. Stage 2 does not introduce JSON fighters,
projectiles, throws, balance changes or new graphics.

## Data-driven content

Primary content lives in UTF-8 files under `data/`: fighters, attacks, combos,
arenas and Russian localization are separate documents. `data/defaults.json`
records stable defaults and the 100-Hz content timing scale. The files in
`data/schemas/` document the external format; runtime validation deliberately
uses the small built-in validator rather than adding `jsonschema`.

`DataLoader` reads JSON and rejects structural errors and duplicate IDs.
`ContentRegistry` constructs immutable definitions, validates ranges and all
cross-file references, then atomically publishes complete dictionaries. Runtime
objects are created by `definition_adapters.py`: content frames are divided by
100 to preserve the exact pre-refactor second values, while hitboxes and combat
rules remain unchanged. `arena_catalog.py`, `fighter.py`, and `combos.py` expose
compatibility views backed by the registry; they no longer contain independent
content definitions.

On initial load failure, the error is logged at critical level and a separately
defined emergency set of two original procedural fighters, two attacks and one
arena permits menu and local-fight startup. A debug Ctrl+F5 reload is
transactional: invalid replacement data leaves the previous registry intact,
and reload is disabled during Fight, Pause and Result. Missing optional artwork
continues through procedural rendering rather than blocking content loading.

`ScreenContext` exposes the registry and localization manager. Selection screens
derive their ID lists from that registry, while `GameSession` stores IDs only.
The match adapter resolves those IDs immediately before constructing runtime
fighters; an unknown ID is logged and returns to the main menu without creating
a partial match.

Save format 2 performs an idempotent retired-ID migration before validation. A
`.v1.bak` copy is created before the first migrated write, nested references are
updated, and colliding statistics are merged without dropping additive counters.

## Deterministic combat core

The active fight runtime is `CombatMatchRuntime`; `CallbackMatchRuntime` is no
longer constructed by the game. Render delta is accumulated by
`SimulationClock`, capped at five catch-up frames, and consumed as exact 1/60 s
simulation steps. Hit stop freezes physics, attacks and the round timer while
still accepting immutable `InputFrame` records. Rendering reads immutable
`CombatSnapshot` values and never mutates `CombatWorld`.

One simulation frame follows this order: capture buffered inputs; honor hit
stop; update fighter controllers and attack phases; resolve throws; update
facing and fixed-step physics; separate pushboxes; resolve strike hitboxes
against hurtboxes through `CombatResolver`; update and clash projectiles; tick
the round controller; publish combat events; increment the deterministic frame.
All simulation randomness belongs to `random.Random(match_seed)`, and snapshots
provide a stable digest for replay tests.

`CombatFighter` stores enum state, frame counters, health, meter, position,
velocity, stun, active `AttackInstance`, input history, pushbox, hurtboxes and
combo tracking without pygame, audio or opponent mutation. `FrameData` and
`AttackInstance` define startup, active, recovery, cancel, hit-stop and repeat-hit
rules in simulation frames. `BlockSystem` handles level, stance, side-relative
back input and non-lethal chip. `CombatResolver` is the strike damage authority,
applying defense and table-driven combo scaling and emitting immutable events.
`ThrowSystem`, `ProjectileSystem`, `MeterSystem`, `HitStopController`,
`FighterPhysics`, and `RoundController` are independent headless subsystems.

Content version 2 stores true 60-FPS timings. The migration tool converts each
100-Hz value with `round(old * 60 / 100)`, keeps active frames at least one,
creates a `.100fps.bak`, populates per-active-frame hitboxes, supports dry-run,
and exits idempotently for already migrated data. Legacy adapters now divide by
60 only for compatibility callers; the active combat core consumes frames
directly.

Legacy `game/fighter.py`, `AttackData`, old collision helpers and `ComboSystem`
remain import-compatible but are not instantiated or advanced by the active
match runtime. Their planned removal follows downstream tool migration; they
must never run alongside `CombatWorld` in one match.

### Unified damage and extended frame data

Every strike, projectile and throw creates an immutable `DamageRequest` and is
resolved into an immutable `CombatResolution`. Only `CombatResolver` subtracts
combat health; round initialization and reset are the explicit exceptions.
Blocking, chip-kill policy, defense scaling, armor, invulnerability, stun,
knockback, meter and combat events therefore share one deterministic path.

`ThrowSystem` validates range, airborne and throw-invulnerable states and tech,
then returns exactly one request without changing health. `ProjectileSystem`
performs movement, deterministic clashes, hurtbox collision and block checks
before sending its request to the resolver. Equal projectile durability and
priority destroy both. Unequal durability subtracts the weaker value; at equal
durability, higher priority survives with one point. `pierce` wins against a
non-piercing projectile. One clash event is emitted per colliding pair.

The content adapter preserves cancel and stop frames, per-frame movement,
turn/single-hit rules, per-frame hitboxes and hurtbox overrides, armor and
invulnerability frames, projectile definitions, multi-hit intervals and attack
properties. A projectile is spawned once when its declared `spawn_frame` is
reached. Missing per-frame hitboxes alone use the documented legacy-box
fallback.

Command recognition supports holds, releases, charge sequences, simultaneous
buttons and direction-plus-button tokens. Conflicts use explicit priority,
affordable meter cost, specificity and finally stable content id order. F1–F8
are read-only views for timing, hitboxes, hurtboxes, pushboxes, frame/state
data, input history, damage state and deterministic match state respectively.

Legacy `game/fighter.py` and `game/combos.py` remain for compatibility tools,
but production constructs only `CombatFighter` and registry-backed commands.
The obsolete `CallbackMatchRuntime` class has been removed.
