import json
from pathlib import Path
from ..json_io import read_json_object,write_json_atomic
from .control_action import ControlAction
from .control_binding import ControlBinding
from .control_profile import ControlProfile
def default_profile(player="p1"):
    codes=[273,274,276,275,13,27,27,97,100,119,115,116,117,103,106,32,306,113,114,101,112]
    return ControlProfile(player,{action:ControlBinding("keyboard",code) for action,code in zip(ControlAction,codes)})
class ControlsManager:
    VERSION=1
    def __init__(self,path:Path):self.path=path;self.profiles={p:default_profile(p) for p in ("p1","p2")}
    def load(self):
        data=read_json_object(self.path,"controls")
        if not data:return self.profiles
        try:
            loaded={p:ControlProfile.from_dict(row) for p,row in data["profiles"].items()}
            for profile in loaded.values():profile.validate()
            self.profiles=loaded
        except (KeyError,TypeError,ValueError):pass
        return self.profiles
    def save(self):return write_json_atomic(self.path,{"version":self.VERSION,"profiles":{p:v.to_dict() for p,v in self.profiles.items()}},"controls")
    def restore_defaults(self,player):self.profiles[player]=default_profile(player)
