from collections import deque
class ToastManager:
    def __init__(self,limit=32):self.queue=deque(maxlen=limit);self.active=None;self.remaining=0
    def push(self,notification):self.queue.append(notification)
    def update(self,dt):
        if self.active:self.remaining-=dt
        if self.active and self.remaining<=0:self.active=None
        if self.active is None and self.queue:self.active=self.queue.popleft();self.remaining=self.active.duration
        return self.active
