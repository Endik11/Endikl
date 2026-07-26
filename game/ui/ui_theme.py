from dataclasses import dataclass

@dataclass(frozen=True,slots=True)
class UITheme:
    background:tuple[int,int,int]=(8,10,14);panel:tuple[int,int,int]=(27,31,38);text:tuple[int,int,int]=(239,242,245);muted:tuple[int,int,int]=(145,154,164);accent:tuple[int,int,int]=(232,181,82);focus:tuple[int,int,int]=(63,201,197);danger:tuple[int,int,int]=(207,53,63);spacing:int=16;radius:int=6;text_scale:float=1.0;transition_seconds:float=.18
    @classmethod
    def accessible(cls,settings):
        high=getattr(settings,"high_contrast",False);large=getattr(settings,"large_text",False);reduced=getattr(settings,"reduced_motion",False)
        return cls(background=(0,0,0) if high else (8,10,14),text=(255,255,255) if high else (239,242,245),focus=(255,220,0) if high else (63,201,197),text_scale=1.25 if large else 1.0,transition_seconds=0 if reduced else .18)
