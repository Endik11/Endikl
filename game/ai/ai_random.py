from __future__ import annotations

import random


class AIRandom:
    def __init__(self, seed: int = 1) -> None:
        self._random = random.Random(seed)

    def reset(self, seed: int) -> None:
        self._random.seed(seed)

    def chance(self, probability: float) -> bool:
        return self._random.random() < max(0.0, min(1.0, probability))

    def choose(self, values):
        return values[self._random.randrange(len(values))]
