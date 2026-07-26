from dataclasses import replace
from ..combat.input_buffer import InputFrame


class DummyRecorder:
    def __init__(self,max_frames=600):self.max_frames=max_frames;self.frames=[];self.recording=False;self.playing=False;self.loop=False;self.delay=0;self.index=0;self.started_at=0
    def start(self):self.frames=[];self.recording=True;self.playing=False
    def stop(self):self.recording=False
    def record(self,frame,facing):
        if not self.recording or len(self.frames)>=self.max_frames:return
        relative=replace(frame,left=frame.right if facing<0 else frame.left,right=frame.left if facing<0 else frame.right,frame_number=len(self.frames));self.frames.append(relative)
    def play(self,frame_number,loop=False,delay=0):self.playing=True;self.loop=loop;self.delay=max(0,delay);self.index=0;self.started_at=frame_number
    def build_input(self,frame_number,facing):
        if not self.playing or frame_number-self.started_at<self.delay or not self.frames:return InputFrame(frame_number=frame_number)
        if self.index>=len(self.frames):
            if not self.loop:self.playing=False;return InputFrame(frame_number=frame_number)
            self.index=0
        source=self.frames[self.index];self.index+=1
        return replace(source,left=source.right if facing<0 else source.left,right=source.left if facing<0 else source.right,frame_number=frame_number)
