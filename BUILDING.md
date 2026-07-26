# Building

Install Python 3.11 x64 and `requirements-dev.txt`. Validate first:

```powershell
python -m pytest -q
python tools/check_localization.py
python tools/validate_content.py
python tools/build_release.py
python tools/verify_release.py
```

`Endikl.spec` creates `dist/ShadowRealmArena-0.8.0-windows-x64/` plus a zip. It includes code, JSON content, manifest and notices. It excludes user data, tests, caches, backups and every UNKNOWN asset. The executable resolves bundled files through the single helper in `game/platform_paths.py` and writes profiles outside the bundle.

GitHub's manual Windows build workflow performs the same checks and uploads a CI artifact. It does not tag, sign, publish or create a GitHub Release.
