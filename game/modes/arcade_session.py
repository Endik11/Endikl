from __future__ import annotations

from dataclasses import asdict, dataclass, field

from .arcade_ladder import build_arcade_ladder, validate_ladder
from .arcade_rules import ArcadeRules


@dataclass(slots=True)
class ArcadeSession:
    fighter_id: str
    opponents: tuple[str, ...]
    seed: int
    difficulty: str = "medium"
    position: int = 0
    continues: int = 2
    wins: int = 0
    losses: int = 0
    match_results: list[dict] = field(default_factory=list)
    completed: bool = False
    rewards: list[str] = field(default_factory=list)
    processed_result_ids: set[str] = field(default_factory=set)

    @classmethod
    def create(cls, fighter_id: str, available: list[str], seed: int, difficulty: str = "medium") -> "ArcadeSession":
        return cls(fighter_id, build_arcade_ladder(fighter_id, available, seed), seed, difficulty)

    @property
    def current_opponent(self) -> str | None:
        return None if self.completed or self.position >= len(self.opponents) else self.opponents[self.position]

    @property
    def current_difficulty(self) -> str:
        order = ArcadeRules().difficulty_order; base = order.index(self.difficulty)
        return order[min(len(order)-1, base + self.position * 2 // max(1, len(self.opponents)))]

    @property
    def is_final(self) -> bool:
        return self.position == len(self.opponents) - 1

    def record_result(self, result_id: str, won: bool) -> bool:
        if result_id in self.processed_result_ids or self.completed: return False
        self.processed_result_ids.add(result_id); self.match_results.append({"result_id": result_id, "won": won, "opponent": self.current_opponent})
        if won:
            self.wins += 1; self.position += 1; self.completed = self.position >= len(self.opponents)
            if self.completed and "arcade_complete" not in self.rewards: self.rewards.append("arcade_complete")
        else: self.losses += 1
        return True

    def use_continue(self) -> bool:
        if self.continues <= 0 or self.completed: return False
        self.continues -= 1; return True

    def to_dict(self) -> dict:
        data=asdict(self);data["opponents"]=list(self.opponents);data["processed_result_ids"]=sorted(self.processed_result_ids);return data

    @classmethod
    def from_dict(cls, data: dict, available: set[str]) -> "ArcadeSession":
        fighter=str(data.get("fighter_id",""));ladder=data.get("opponents",[]);seed=int(data.get("seed",1))
        if fighter not in available or not validate_ladder(ladder,fighter,available): return cls.create(next(iter(sorted(available))),sorted(available),seed)
        session=cls(fighter,tuple(ladder),seed,str(data.get("difficulty","medium")),max(0,int(data.get("position",0))),max(0,int(data.get("continues",0))),max(0,int(data.get("wins",0))),max(0,int(data.get("losses",0))),list(data.get("match_results",[])),bool(data.get("completed",False)),list(data.get("rewards",[])),set(data.get("processed_result_ids",[])))
        if session.position > len(session.opponents): session.position=0;session.completed=False
        return session
