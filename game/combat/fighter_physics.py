from .constants import FIXED_DT,GRAVITY,TERMINAL_VELOCITY
from .hitbox import intersects
class FighterPhysics:
    @staticmethod
    def update(f,left,right,ground):
        if not f.grounded:f.velocity_y=min(TERMINAL_VELOCITY,f.velocity_y+GRAVITY*FIXED_DT)
        f.x=max(left,min(right,f.x+f.velocity_x*FIXED_DT));f.y+=f.velocity_y*FIXED_DT
        if f.y>=ground:f.y=ground;f.velocity_y=0;f.grounded=True
    @staticmethod
    def separate(a,b,left,right):
        ra=a.pushbox.rect(a.x,a.y);rb=b.pushbox.rect(b.x,b.y)
        if not intersects(ra,rb):return 0
        overlap=min(ra[0]+ra[2]-rb[0],rb[0]+rb[2]-ra[0]);push=max(0,overlap/2)
        if a.x<=b.x:a.x=max(left,a.x-push);b.x=min(right,b.x+push)
        else:a.x=min(right,a.x+push);b.x=max(left,b.x-push)
        return push*2
