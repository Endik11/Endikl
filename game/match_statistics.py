from dataclasses import asdict,dataclass,field
from .combat.enums import CombatEventType


@dataclass(slots=True)
class MatchStatistics:
    result_id:str;fighter_id:str;opponent_id:str;arena_id:str;outcome:str;damage_dealt:int=0;damage_received:int=0;longest_combo:int=0;highest_combo_damage:int=0;total_combo_hits:int=0;successful_blocks:int=0;chip_damage_dealt:int=0;throws:int=0;throw_techs:int=0;projectiles_created:int=0;projectiles_hit:int=0;projectiles_blocked:int=0;projectile_clashes:int=0;knockouts:int=0;double_knockouts:int=0;rounds_won:int=0;rounds_lost:int=0
    @classmethod
    def from_events(cls,result_id,fighter_id,opponent_id,arena_id,outcome,events):
        stats=cls(result_id,fighter_id,opponent_id,arena_id,outcome);combo_hits=combo_damage=0
        for event in events:
            source=event.source_id in {fighter_id,"p1"};target=event.target_id in {fighter_id,"p1"}
            if event.type in {CombatEventType.ATTACK_HIT,CombatEventType.PROJECTILE_HIT,CombatEventType.THROW_DAMAGE_APPLIED}:
                if source:stats.damage_dealt+=int(event.value);combo_hits+=1;combo_damage+=int(event.value)
                if target:stats.damage_received+=int(event.value)
            if event.type in {CombatEventType.ATTACK_BLOCKED,CombatEventType.PROJECTILE_BLOCKED}:
                if target:stats.successful_blocks+=1
                if source:stats.chip_damage_dealt+=int(event.value)
            if event.type is CombatEventType.THROW_CONNECTED and source:stats.throws+=1
            if event.type is CombatEventType.THROW_TECHED and target:stats.throw_techs+=1
            if event.type is CombatEventType.PROJECTILE_CREATED and source:stats.projectiles_created+=1
            if event.type is CombatEventType.PROJECTILE_HIT and source:stats.projectiles_hit+=1
            if event.type is CombatEventType.PROJECTILE_BLOCKED and source:stats.projectiles_blocked+=1
            if event.type is CombatEventType.PROJECTILE_CLASH:stats.projectile_clashes+=1
            if event.type is CombatEventType.COMBO_ENDED:
                stats.longest_combo=max(stats.longest_combo,combo_hits);stats.highest_combo_damage=max(stats.highest_combo_damage,combo_damage);stats.total_combo_hits+=combo_hits;combo_hits=combo_damage=0
            if event.type is CombatEventType.ROUND_DOUBLE_KO:stats.double_knockouts+=1
            if event.type is CombatEventType.ROUND_ENDED:
                if source:stats.rounds_won+=1
                elif target:stats.rounds_lost+=1
        stats.longest_combo=max(stats.longest_combo,combo_hits);stats.highest_combo_damage=max(stats.highest_combo_damage,combo_damage);stats.total_combo_hits+=combo_hits
        if outcome=="win":stats.knockouts=1
        return stats
    def to_dict(self):return asdict(self)
