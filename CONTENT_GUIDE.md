# Content guide

Content is loaded from `data/` by `ContentRegistry`; use existing entries and schemas as templates and run `python tools/validate_content.py`.

- Fighters reference attacks, visual definitions and default unlock state with unique stable IDs.
- Attacks own timing and combat values; combos reference valid attacks and input tokens.
- Arenas define combat bounds and procedural visual themes, never damage logic.
- AI profiles tune deterministic decision behavior without direct world mutation.
- Stories/dialogues use valid fighter and node references with reachable transitions.
- Achievements use stable event IDs and idempotent rewards.
- Shop entries are cosmetic categories only, with nonnegative integer prices and localization keys.

To add a fighter or arena, add its JSON definition, every referenced localization/visual entry and focused registry tests. Do not put unlicensed media in `assets/`.
