# Asset audit

Audit date: 2026-07-26. Release policy: only `VERIFIED` resources may be bundled. The default game uses original procedural rendering and `allow_unverified_assets=false`.

| Path | Type | Source / author | License / link | Production | Release | Original | Fallback | Status |
|---|---|---|---|---|---|---|---|---|
| `assets/arenas/li_river_guilin.jpg` | JPEG | Unknown | Unknown | Blocked | No | Unverified | Procedural arena | UNKNOWN / EXCLUDED |
| `assets/arenas/zhangjiajie_forest.jpg` | JPEG | Unknown | Unknown | Blocked | No | Unverified | Procedural arena | UNKNOWN / EXCLUDED |
| `assets/fighters/kael_sheet.png` | PNG | Unknown | Unknown | Blocked | No | Unverified | Procedural fighter | UNKNOWN / EXCLUDED |
| `assets/fighters/mira_sheet.png` | PNG | Unknown | Unknown | Blocked | No | Unverified | Procedural fighter | UNKNOWN / EXCLUDED |
| `assets/fighters/orrin_sheet.png` | PNG | Unknown | Unknown | Blocked | No | Unverified | Procedural fighter | UNKNOWN / EXCLUDED |
| `assets/fighters/sable_sheet.png` | PNG | Unknown | Unknown | Blocked | No | Unverified | Procedural fighter | UNKNOWN / EXCLUDED |
| `assets/fighters/kael_render.png` | PNG | Project-generated combat render | Project-generated, no third-party media | Yes | Yes | Yes | Procedural fighter | VERIFIED |
| `assets/fighters/sable_render.png` | PNG | Project-generated combat render | Project-generated, no third-party media | Yes | Yes | Yes | Procedural fighter | VERIFIED |
| `assets/ui/shadow_realm_keyart.png` | PNG | Project-generated concept art | Project-generated, no third-party media | Yes | Yes | Yes | Procedural menu fallback | VERIFIED |

The six files marked UNKNOWN remain development-only and are enumerated in `release_excludes.json`. The verified Kael and Sable combat renders are used by the Pygame fighter renderer and bundled release. The key art is a project-generated visual asset used by the Pygame menu and bundled release.
