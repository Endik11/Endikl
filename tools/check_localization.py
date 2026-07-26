from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(path):
    data=json.loads(path.read_text(encoding="utf-8"));strings=data.get("strings")
    if not isinstance(strings,dict):raise ValueError(f"{path.name}: strings must be object")
    return strings
def placeholders(value):return set(re.findall(r"\{([A-Za-z_][A-Za-z0-9_]*)\}",value))
def main():
    try:ru=load(ROOT/"data/localization_ru.json");en=load(ROOT/"data/localization_en.json")
    except (OSError,ValueError,json.JSONDecodeError) as exc:print(exc);return 1
    errors=[]
    if set(ru)!=set(en):errors.append(f"key mismatch missing_en={sorted(set(ru)-set(en))} missing_ru={sorted(set(en)-set(ru))}")
    for key in set(ru)&set(en):
        if not str(ru[key]).strip() or not str(en[key]).strip():errors.append(f"empty: {key}")
        if placeholders(ru[key])!=placeholders(en[key]):errors.append(f"placeholder mismatch: {key}")
    for error in errors:print(error)
    print(f"localization_keys={len(ru)} errors={len(errors)}")
    return 1 if errors else 0
if __name__=="__main__":raise SystemExit(main())
