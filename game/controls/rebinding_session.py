from copy import deepcopy
from .conflict_detector import ConflictDetector
class RebindingSession:
    def __init__(self,profile,others=()):self.profile=profile;self.others=tuple(others);self.original=deepcopy(profile.bindings);self.waiting_for=None;self.pending=None;self.conflicts=[]
    def begin(self,action):self.waiting_for=action;self.pending=None;self.conflicts=[]
    def capture(self,binding):
        if self.waiting_for is None:return False
        self.pending=binding;self.conflicts=ConflictDetector.find(self.profile,self.waiting_for,binding,self.others);return not self.conflicts
    def apply(self,replace_conflicts=False):
        if self.waiting_for is None or self.pending is None:return False
        if self.conflicts and not replace_conflicts:return False
        previous=self.profile.bindings.get(self.waiting_for)
        if replace_conflicts:
            for conflict in self.conflicts:
                if conflict.other_player==self.profile.player and conflict.other_action:
                    if previous is None:self.profile.bindings.pop(conflict.other_action,None)
                    else:self.profile.bindings[conflict.other_action]=previous
        self.profile.bindings[self.waiting_for]=self.pending
        try:self.profile.validate()
        except ValueError:self.profile.bindings=deepcopy(self.original);return False
        self.waiting_for=self.pending=None;self.conflicts=[];return True
    def cancel(self):self.profile.bindings=deepcopy(self.original);self.waiting_for=self.pending=None;self.conflicts=[]
