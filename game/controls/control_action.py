from enum import Enum
class ControlAction(str,Enum):
    NAVIGATE_UP="navigate_up";NAVIGATE_DOWN="navigate_down";NAVIGATE_LEFT="navigate_left";NAVIGATE_RIGHT="navigate_right";CONFIRM="confirm";CANCEL="cancel";PAUSE="pause";MOVE_LEFT="move_left";MOVE_RIGHT="move_right";JUMP="jump";CROUCH="crouch";LIGHT_PUNCH="light_punch";HEAVY_PUNCH="heavy_punch";LIGHT_KICK="light_kick";HEAVY_KICK="heavy_kick";BLOCK="block";THROW="throw";SPECIAL="special";TRAINING_RESET="training_reset";TRAINING_RECORD="training_record";TRAINING_PLAYBACK="training_playback"

REQUIRED_ACTIONS=frozenset({ControlAction.CONFIRM,ControlAction.CANCEL,ControlAction.PAUSE,ControlAction.MOVE_LEFT,ControlAction.MOVE_RIGHT,ControlAction.JUMP,ControlAction.CROUCH,ControlAction.LIGHT_PUNCH,ControlAction.HEAVY_PUNCH,ControlAction.LIGHT_KICK,ControlAction.HEAVY_KICK})
