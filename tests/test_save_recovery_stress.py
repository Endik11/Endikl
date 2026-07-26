from game.save import SaveManager
def test_repeated_save_load_and_corruption_recovery(tmp_path):
    path=tmp_path/"profile.json";manager=SaveManager(path);manager.load()
    for i in range(100):manager.profile.currency=i;assert manager.save();manager.load()
    path.write_text("bad",encoding="utf-8");SaveManager(path).load();assert path.with_suffix(".json.corrupt.bak").exists()
