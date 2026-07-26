import json
from game.save import SaveManager,SAVE_VERSION
def test_format_four_fields_roundtrip_and_backup(tmp_path):
    path=tmp_path/"profile.json";manager=SaveManager(path);profile=manager.load();profile.economy_transactions=["tx"];profile.unlocked_achievements=["first_match"];profile.display_name="A";assert manager.save();loaded=SaveManager(path).load();assert loaded.economy_transactions==["tx"] and loaded.unlocked_achievements==["first_match"] and loaded.display_name=="A" and path.with_suffix(".json.bak").exists()
def test_corrupt_recovery_preserves_file(tmp_path):
    path=tmp_path/"profile.json";path.write_text("broken",encoding="utf-8");manager=SaveManager(path);manager.load();assert path.with_suffix(".json.corrupt.bak").read_text(encoding="utf-8")=="broken"
def test_newer_version_is_not_overwritten(tmp_path):
    path=tmp_path/"profile.json";original={"version":SAVE_VERSION+9,"unknown":{"future":True},"currency":10};path.write_text(json.dumps(original),encoding="utf-8");manager=SaveManager(path);manager.load();assert manager.read_only_newer and not manager.save();assert json.loads(path.read_text(encoding="utf-8"))==original
