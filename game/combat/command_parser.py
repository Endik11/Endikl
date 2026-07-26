class CommandParser:
    DIRECTIONS={"down":2,"down_back":1,"down_forward":3,"forward":6,"back":4,"up":8,"neutral":5}

    def match(self,buffer,command,facing=1):
        frames=buffer.recent(command.get("window",buffer.capacity));tokens=command["inputs"]
        cursor=len(frames)-1;matched=[];tolerance=int(command.get("tolerance",999))
        previous_index=len(frames)
        for token in reversed(tokens):
            found=None
            while cursor>=0 and previous_index-cursor-1<=tolerance:
                if frames[cursor].frame_number not in buffer.consumed_frames and self._matches(frames,cursor,token,facing):found=cursor;break
                cursor-=1
            if found is None:return False
            matched.append(frames[found].frame_number);previous_index=found;cursor=found if (token.get("button") or token.get("buttons")) and token.get("direction") is None else found-1
        key=(command.get("id",str(tokens)),tuple(reversed(matched)))
        return buffer.consume(key,matched)

    def _matches(self,frames,index,token,facing):
        frame=frames[index];direction=token.get("direction");button=token.get("button");buttons=token.get("buttons",())
        if direction is not None and frame.direction(facing)!=self.DIRECTIONS[direction]:return False
        if button is not None and not self._button_event(frame,button,token):return False
        if button is not None and token.get("release") and (index==0 or button not in frames[index-1].held and not getattr(frames[index-1],button,False)):return False
        if buttons and not all(self._button_event(frame,b,token) for b in buttons):return False
        hold=int(token.get("hold_frames",0))
        if hold:
            if index-hold+1<0:return False
            for prior in frames[index-hold+1:index+1]:
                if direction is not None and prior.direction(facing)!=self.DIRECTIONS[direction]:return False
                if button is not None and button not in prior.held and not getattr(prior,button,False):return False
        return True

    @staticmethod
    def _button_event(frame,button,token):
        if token.get("release"):return button in frame.released
        if token.get("held"):return button in frame.held or getattr(frame,button,False)
        return button in frame.pressed
