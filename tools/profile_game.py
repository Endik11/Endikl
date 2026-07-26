from __future__ import annotations
import sys,time,json,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from game.content_registry import ContentRegistry
from game.localization import LocalizationManager
from game.achievements import AchievementRegistry,AchievementManager
from game.economy import Catalog
from game.save import SaveManager
ROOT=Path(__file__).resolve().parents[1]
def timed(label,fn,count):
    start=time.perf_counter()
    for _ in range(count):fn()
    elapsed=time.perf_counter()-start;print(f"{label} count={count} elapsed_ms={elapsed*1000:.3f} avg_ms={elapsed*1000/count:.5f}")
def main():
    timed("content_registry",lambda:ContentRegistry(ROOT/"data").load_all(),10)
    ru=json.loads((ROOT/"data/localization_ru.json").read_text(encoding="utf-8"))["strings"];loc=LocalizationManager(ru);timed("localization",lambda:loc.get("shop.balance",amount=100),10000)
    catalog=Catalog.load(ROOT/"data/shop_catalog.json");timed("shop",lambda:catalog.items.get("ember_palette"),10000)
    registry=AchievementRegistry.load(ROOT/"data/achievements.json");manager=AchievementManager(registry);timed("achievements",lambda:manager.evaluate("same",{"matches_played":1}),10000)
    with tempfile.TemporaryDirectory() as directory:
        saves=SaveManager(Path(directory)/"profile.json");saves.load();timed("saves",saves.save,100)
    print("bounded_histories=ai:48,toasts:32,transactions:set,results:set");return 0
if __name__=="__main__":raise SystemExit(main())
