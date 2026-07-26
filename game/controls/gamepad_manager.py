class GamepadManager:
    def __init__(self,deadzone=.35):self.deadzone=max(.05,min(.95,deadzone))
    def axis(self,value):return 0 if abs(value)<self.deadzone else (1 if value>0 else -1)
    def rumble(self,joystick,low=.3,high=.5,duration_ms=80):
        try:return bool(joystick.rumble(low,high,duration_ms))
        except (AttributeError,RuntimeError):return False
