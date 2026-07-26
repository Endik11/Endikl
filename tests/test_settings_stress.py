import json
from game.settings import SettingsManager
def test_hundred_corrupt_and_valid_settings_reloads(tmp_path):
    path=tmp_path/"settings.json";manager=SettingsManager(path)
    for i in range(100):path.write_text("bad" if i%2 else json.dumps({"video":{"width":1280+i}}),encoding="utf-8");settings=manager.load();assert 640<=settings.video.width<=7680
import pytest

pytestmark = pytest.mark.slow
