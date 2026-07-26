from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIAction:
    name: str
    buttons: tuple[str, ...] = ()
    duration: int = 1
