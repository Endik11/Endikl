class ProgressManager:
    def __init__(self,profile):self.profile=profile
    def store_arcade(self,session):self.profile.arcade_progress=session.to_dict()
    def store_story(self,session):self.profile.story_progress=session.to_dict()
    def store_tournament(self,session):self.profile.tournament_progress=session.to_dict()
    def store_training(self,session):self.profile.training_preferences=session.to_dict()
