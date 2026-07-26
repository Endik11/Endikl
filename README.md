# Shadow Realm: Arena

An original data-driven 2D fighting game built with Python and Pygame. Current application version: **0.8.0 development**.

## Features

- Deterministic combat through `CombatWorld` and `CombatResolver`
- Local versus, Arcade, Story, Tournament and Training modes
- Difficulty profiles, keyboard/gamepad rebinding and disconnect pause
- RU/EN localization, accessibility settings, achievements and cosmetic shop
- Versioned atomic saves, recovery backups and user-data migration
- Original procedural fighters, arenas and effects

## Install and run

Python 3.11+ is supported. Install `pygame>=2.6`:

```powershell
python -m pip install -r requirements.txt
python main.py
```

Default Player 1 controls use WASD plus T/U/G/J; Player 2 uses arrows and keypad attacks. Block, throw, stance, energy and pause bindings are shown and editable in Controls. Compatible gamepads are detected through Pygame.

## Development

```powershell
python -m pip install -r requirements-dev.txt
python -m compileall -q .
python -m pytest -q
python -m pytest -q -m slow
python tools/check_localization.py
python tools/validate_content.py
python tools/benchmark_combat.py
python tools/benchmark_renderer.py
python tools/benchmark_ai.py
```

Game definitions live in `data/*.json` and are validated by the same registries used at runtime. See `CONTENT_GUIDE.md` for fighters and arenas and `ANIMATION_GUIDE.md` for visual-only animation data.

## Project structure

- `game/combat/`: authoritative simulation and damage resolution
- `game/ai/`: perception and decisions producing `InputFrame`
- `game/modes/`, `game/screens/`, `game/ui/`: modes and presentation
- `game/platform_paths.py`: bundled versus writable paths
- `data/`: versioned definitions and localization
- `tools/`: validation, profiling and release scripts
- `tests/`: unit, integration, stress, headless and release checks

## User data

Writable data never belongs in the bundle: Windows `%LOCALAPPDATA%/ShadowRealmArena`, Linux `$XDG_DATA_HOME/ShadowRealmArena` (normally `~/.local/share`), macOS `~/Library/Application Support/ShadowRealmArena`. Set `SHADOW_REALM_USER_DATA` for isolated testing. Existing source-tree `saves/*.json` are validated, backed up and copied once; originals are retained.

## Build

Run `python tools/build_release.py`, then `python tools/verify_release.py`. The supported release format is a Windows x64 one-folder build. Details are in `BUILDING.md`.

## Troubleshooting and limitations

See `TROUBLESHOOTING.md`. Physical fullscreen, multi-monitor, audio-device and controller compatibility require the checks in `MANUAL_TEST_CHECKLIST.md`. UNKNOWN development assets are blocked and excluded; release visuals are procedural. The project license has not been selected; see `LICENSE_OPTIONS.md` and `THIRD_PARTY_LICENSES.md`.

Roadmap after this release-readiness stage: owner license selection, original icon, hardware QA, localization polish and signed public release preparation.
