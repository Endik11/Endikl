from dataclasses import asdict, dataclass


@dataclass(slots=True)
class BracketMatch:
    id:str;round_index:int;slot_index:int;fighter_one:str="";fighter_two:str="";winner:str="";loser:str="";result_id:str=""


def build_bracket(participants:list[str],third_place=False):
    if len(participants) not in (4,8) or len(set(participants))!=len(participants):raise ValueError("Tournament needs 4 or 8 unique participants")
    matches=[];size=len(participants);round_count=2 if size==4 else 3
    for slot in range(size//2):matches.append(BracketMatch(f"r0-m{slot}",0,slot,participants[slot*2],participants[slot*2+1]))
    for round_index in range(1,round_count):
        for slot in range(size//(2**(round_index+1))):matches.append(BracketMatch(f"r{round_index}-m{slot}",round_index,slot))
    if third_place:matches.append(BracketMatch("third-place",round_count,0))
    return matches


def next_match(matches):return next((match for match in matches if match.fighter_one and match.fighter_two and not match.winner),None)
