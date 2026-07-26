from .enums import FighterState
class FighterStateMachine:
    @staticmethod
    def change(fighter,state): fighter.state=state;fighter.state_frame=0;fighter.current_animation=state.name.lower()
    @staticmethod
    def tick(fighter):fighter.state_frame+=1
