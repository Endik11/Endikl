from pathlib import Path

from game.version import VERSION

root = Path(SPECPATH)
name = f"ShadowRealmArena-{VERSION}-windows-x64"
data_files = [(str(path), "data") for path in (root / "data").glob("*.json") if not path.name.endswith(".bak")]
docs = ["CREDITS.md", "THIRD_PARTY_LICENSES.md", "ASSET_AUDIT.md", "release_manifest.json"]
datas = data_files + [(str(root / item), ".") for item in docs]
key_art = root / "assets" / "ui" / "shadow_realm_keyart.png"
if key_art.exists():
    datas.append((str(key_art), "assets/ui"))
for fighter_render in (root / "assets" / "fighters").glob("*_render.png"):
    datas.append((str(fighter_render), "assets/fighters"))

a = Analysis([str(root / "main.py")], pathex=[str(root)], binaries=[], datas=datas, hiddenimports=[], hookspath=[], hooksconfig={}, runtime_hooks=[], excludes=["pytest"], noarchive=False)
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=name, debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=True, contents_directory=".", version=str(root / "build_version_info.txt"))
coll = COLLECT(exe, a.binaries, a.datas, strip=False, upx=True, upx_exclude=[], name=name)
