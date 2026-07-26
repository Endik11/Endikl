import json
from pathlib import Path
from game.localization import LocalizationManager
from tools.check_localization import placeholders
def test_ru_en_have_equal_keys_and_placeholders():
    ru=json.loads(Path("data/localization_ru.json").read_text(encoding="utf-8"))["strings"];en=json.loads(Path("data/localization_en.json").read_text(encoding="utf-8"))["strings"];assert set(ru)==set(en);assert all(placeholders(ru[k])==placeholders(en[k]) for k in ru)
def test_switch_fallback_format_and_unknown_warning():
    manager=LocalizationManager(languages={"ru":{"hello":"Привет {name}","fallback":"Да"},"en":{"hello":"Hello {name}"}},language="en",fallback="ru");assert manager.get("hello",name="A")=="Hello A" and manager.get("fallback")=="Да";assert manager.switch("ru") and not manager.switch("xx");assert manager.get("missing")=="[missing]"
