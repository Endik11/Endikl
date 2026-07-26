from __future__ import annotations
import argparse,json,shutil
from pathlib import Path
FIELDS=("startup_frames","active_frames","recovery_frames","hit_stun_frames","block_stun_frames")
def convert(value,active=False):return max(1 if active else 0,round(value*60/100))
def migrate(path:Path,dry_run=False):
    data=json.loads(path.read_text(encoding="utf-8"))
    if data.get("data_version",1)>=2:
        changed=False
        for attack in data["attacks"]:
            if not attack.get("hitboxes_by_frame"):
                x,y,width,height=attack["hitbox"]
                attack["hitboxes_by_frame"]={str(frame):[{"x":x,"y":y,"width":width,"height":height,"hit_id":"main","priority":1}] for frame in range(attack["startup_frames"],attack["startup_frames"]+attack["active_frames"])}
                changed=True
        if changed and not dry_run:path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        return changed
    for attack in data["attacks"]:
        before=sum(attack[x] for x in ("startup_frames","active_frames","recovery_frames"))/100
        for field in FIELDS:attack[field]=convert(attack[field],field=="active_frames")
        attack.setdefault("cancel_start_frame",attack["startup_frames"]);attack.setdefault("cancel_end_frame",attack["startup_frames"]+attack["active_frames"]-1);attack.setdefault("hit_stop_frames",3);attack.setdefault("block_stop_frames",2);attack.setdefault("movement",{"x_per_frame":0,"y_per_frame":0});attack.setdefault("hitboxes_by_frame",{});attack.setdefault("hurtbox_overrides_by_frame",{});attack.setdefault("invulnerability_frames",[]);attack.setdefault("armor_frames",[]);attack.setdefault("projectile_definition",None);attack.setdefault("multi_hit_interval_frames",1)
        after=sum(attack[x] for x in ("startup_frames","active_frames","recovery_frames"))/60
        if abs(before-after)>.02:raise ValueError(f"duration drift too large for {attack['id']}")
        print(f"{attack['id']}: {before:.3f}s -> {after:.3f}s")
    data["data_version"]=2;data["simulation_fps"]=60
    if not dry_run:
        backup=path.with_suffix(path.suffix+".100fps.bak")
        if not backup.exists():shutil.copy2(path,backup)
        path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return True
def main():
    p=argparse.ArgumentParser();p.add_argument("path",nargs="?",default="data/attacks.json");p.add_argument("--dry-run",action="store_true");a=p.parse_args();print("migrated" if migrate(Path(a.path),a.dry_run) else "already migrated")
if __name__=="__main__":main()
