from __future__ import annotations

from .hit_effects import EVENT_EFFECTS
from .particle_system import ParticleSystem


class EffectsManager:
    def __init__(self, registry) -> None:
        self.registry = registry
        self.particles = ParticleSystem()
        self.last_events: list[str] = []

    def handle_events(self, events) -> None:
        for event in events:
            name = getattr(event.type, "name", str(event.type))
            effect_id = EVENT_EFFECTS.get(name)
            definition = self.registry.effects.get(effect_id or "")
            if not definition:
                continue
            x, y = event.position if event.position else (640, 360)
            self.particles.emit(float(x), float(y), definition)
            self.last_events.append(name)

    def update(self, settings=None) -> None:
        reduced = getattr(getattr(settings, "video", settings), "reduced_motion", False)
        particles_enabled = getattr(getattr(settings, "video", settings), "particles", True)
        if particles_enabled:
            self.particles.update(reduced_motion=reduced)

    def draw(self, surface, camera, settings=None) -> None:
        if getattr(getattr(settings, "video", settings), "particles", True):
            self.particles.draw(surface, camera)
