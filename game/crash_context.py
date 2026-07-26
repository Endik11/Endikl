from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass
class CrashContext:
    game_state: str = "unknown"
    mode: str = "unknown"
    fighters: list[str] = field(default_factory=list)
    arena: str = "unknown"
    fallback_content: bool = False
    accessibility: dict[str, object] = field(default_factory=dict)
    recent_log: list[str] = field(default_factory=list)

    def safe_dict(self) -> dict[str, object]:
        return asdict(self)
