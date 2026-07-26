# Asset audit

No source or license metadata accompanied the files below. Consequently every
file is marked **UNKNOWN** and must not be represented as freely redistributable.
The game does not require any of them: `ResourceReport`, procedural fighter
rendering, procedural arenas, `missing_artwork_policy: procedural_fallback`,
and `allow_unverified_assets: false` in `data/defaults.json` keep startup and
play functional when they are absent. Unverified image files are blocked by
default and only loaded when the user explicitly enables `allow_unverified_assets`.
That opt-in path logs a warning and does not make any redistribution claim.

| Path | Type | Current use | Source | License | Safe to distribute | Temporary | Fallback |
|---|---|---|---|---|---|---|---|
| `assets/arenas/li_river_guilin.jpg` | JPEG arena reference | Optional preview metadata for `great_wall`; runtime arena remains procedural | UNKNOWN | UNKNOWN | No determination possible; replace before distribution | Yes | Procedural wall arena |
| `assets/arenas/zhangjiajie_forest.jpg` | JPEG arena reference | Optional preview metadata for `dragon_mountains`; runtime arena remains procedural | UNKNOWN | UNKNOWN | No determination possible; replace before distribution | Yes | Procedural mountain arena |
| `assets/fighters/kael_sheet.png` | PNG sprite-sheet export | Optional resource audit/export; current fighter renderer is procedural | UNKNOWN | UNKNOWN | No determination possible; replace or document provenance | Yes | Procedural fighter model |
| `assets/fighters/mira_sheet.png` | PNG sprite-sheet export | Optional resource audit/export; current fighter renderer is procedural | UNKNOWN | UNKNOWN | No determination possible; replace or document provenance | Yes | Procedural fighter model |
| `assets/fighters/orrin_sheet.png` | PNG sprite-sheet export | Optional resource audit/export; current fighter renderer is procedural | UNKNOWN | UNKNOWN | No determination possible; replace or document provenance | Yes | Procedural fighter model |
| `assets/fighters/sable_sheet.png` | PNG sprite-sheet export | Optional resource audit/export; current fighter renderer is procedural | UNKNOWN | UNKNOWN | No determination possible; replace or document provenance | Yes | Procedural fighter model |

The two JPEG files require particular attention: their filenames describe real
locations, but no author, download origin, release, or license can be verified
from repository contents. They should be replaced with original commissioned or
procedurally generated art before a public release.
