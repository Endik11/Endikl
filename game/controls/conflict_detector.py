from dataclasses import dataclass
from .control_action import ControlAction
DEBUG_KEYS=frozenset({282,283,284,285,286,287,288,289})
UI=set(list(ControlAction)[:7])
@dataclass(frozen=True,slots=True)
class BindingConflict:kind:str;action:ControlAction;other_action:ControlAction|None;other_player:str=""
class ConflictDetector:
    @staticmethod
    def find(profile,action,binding,others=()):
        found=[]
        if binding.device=="keyboard" and binding.code in DEBUG_KEYS:found.append(BindingConflict("debug",action,None))
        for other_action,other in profile.bindings.items():
            if other_action!=action and other.identity==binding.identity:
                kind="ui_combat" if (action in UI)!=(other_action in UI) else "same_context";found.append(BindingConflict(kind,action,other_action,profile.player))
        for other_profile in others:
            for other_action,other in other_profile.bindings.items():
                if other.identity==binding.identity:found.append(BindingConflict("cross_player",action,other_action,other_profile.player))
        return found
