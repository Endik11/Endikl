from dataclasses import dataclass
import json
from pathlib import Path
@dataclass(frozen=True,slots=True)
class CatalogItem:
    id:str;name_key:str;description_key:str;category:str;price:int;preview:dict;requirements:tuple[str,...]=();default_available:bool=True;hidden:bool=False;tags:tuple[str,...]=()
class Catalog:
    ALLOWED={"palettes","emblems","trails","profile_frames","arena_variants","gallery_entries"}
    def __init__(self,items):self.items={item.id:item for item in items}
    @classmethod
    def load(cls,path:Path):
        rows=json.loads(path.read_text(encoding="utf-8"))["items"];items=[]
        for row in rows:
            if row["category"] not in cls.ALLOWED or int(row["price"])<0:raise ValueError("Invalid cosmetic catalog item")
            items.append(CatalogItem(row["id"],row["name_key"],row["description_key"],row["category"],int(row["price"]),dict(row.get("preview",{})),tuple(row.get("unlock_requirements",[])),bool(row.get("default_availability",True)),bool(row.get("hidden",False)),tuple(row.get("tags",[]))))
        if len({x.id for x in items})!=len(items):raise ValueError("Duplicate catalog id")
        return cls(items)
