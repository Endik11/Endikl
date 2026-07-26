from collections import Counter, deque
from dataclasses import dataclass, field


@dataclass(slots=True)
class AIMemory:
    limit: int = 48
    opponent_actions: deque[str] = field(default_factory=lambda: deque(maxlen=48))
    successful_punishes: deque[str] = field(default_factory=lambda: deque(maxlen=12))
    errors: deque[str] = field(default_factory=lambda: deque(maxlen=12))

    def remember(self, action: str) -> None:
        if action:
            self.opponent_actions.append(action)

    def frequency(self, action: str) -> float:
        if not self.opponent_actions:
            return 0.0
        return Counter(self.opponent_actions)[action] / len(self.opponent_actions)

    def clear(self) -> None:
        self.opponent_actions.clear(); self.successful_punishes.clear(); self.errors.clear()
