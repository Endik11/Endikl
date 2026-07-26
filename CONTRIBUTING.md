# Contributing

Install both requirements files, branch from the current integration branch, keep changes focused and use descriptive imperative commits. Run compileall, normal tests, relevant slow tests, localization and content validation before a pull request.

Follow existing typed data/runtime boundaries: combat changes belong under `game/combat`, visual code must not mutate the simulation, and AI must produce `InputFrame`. Add tests proportional to behavioral risk. JSON changes must pass schemas and runtime validators.

Do not add copied sprites, music, fonts, logos or reference images without recorded author, source and redistribution license in `ASSET_AUDIT.md`. Do not commit saves, logs, crash reports, credentials or generated release directories.
