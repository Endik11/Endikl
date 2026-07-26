# Troubleshooting

- Blank/no-display startup: update graphics drivers and try windowed mode; for CI set SDL video/audio drivers to `dummy`.
- No audio device: the game should continue silently; check OS output selection before relaunching.
- Controller unavailable: reconnect before entering combat, then verify assignment and bindings in Controls.
- Settings or profile reset: inspect the user-data directory for `.bak`, `.corrupt.bak` and crash reports; do not overwrite a newer-version profile.
- Content validation failure: restore valid JSON and run `tools/validate_content.py`; release mode does not accept fallback content.
- Build failure: use Python 3.11 x64, reinstall `requirements-dev.txt`, delete generated `build/` and `dist/`, then rebuild.
