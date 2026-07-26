# Legacy audit

| Path / symbol | Purpose | Production usage | Why retained | Removal plan |
|---|---|---|---|---|
| `game/fighter.py` | Stage 1 fighter facade | No; `CombatWorld` is authoritative | `tools/export_fighter_sheets.py` still imports definitions | Move exporter to `ContentRegistry`, then delete with its tests |
| `game/combos.py` | Old combo/input facade | Only lazy `definition_adapters` compatibility | Supports the retained fighter export facade | Remove together with `game/fighter.py` after exporter migration |
| `game/ai.py` | Pre-package AI implementation | No; Python resolves `game/ai/` package used by runtime | Historical source reference; filename collision makes direct imports ambiguous | Delete after owner confirms no external tools load it by file path |
| `BASE_ATTACKS`, `DEFAULT_COMBOS`, `ComboSystem` | Compatibility views | Not imported by engine or `CombatMatchRuntime` | Tool compatibility only | Same removal as fighter/combos facades |
| `game/match_runtime.py` | Runtime protocol/adapter boundary | Yes | Preserves screen and test contracts around the authoritative runtime | Keep until public API versioning permits a breaking change |
| save migrations in `game/save.py` | Old profile conversion | Yes, during load only | Required for existing user data | Retain while those save versions remain supported |

Production damage remains in `CombatResolver`. Render, UI, AI, throw and projectile systems do not directly mutate health; reset and sudden-death setup are explicit lifecycle exceptions.
