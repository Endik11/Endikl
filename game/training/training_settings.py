from dataclasses import dataclass


@dataclass(slots=True)
class TrainingSettings:
    health_mode:str="infinite";meter_mode:str="infinite";meter_value:int=0;dummy_behavior:str="standing";playback_delay:int=0;playback_loop:bool=True;show_input_history:bool=True;show_frame_data:bool=True;show_hitbox:bool=False;show_hurtbox:bool=False;show_pushbox:bool=False;auto_recovery_frames:int=120
