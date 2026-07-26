# Animation guide

Procedural rigs define named bones; clips contain ordered keyframes and visual events. Bone and clip IDs must match `visuals.json`/`animations.json`. Interpolate render poses without changing fighter physics, hitboxes, health, energy or combat timing.

Visual events may request particles, trails, flashes or camera feedback. Accessibility settings must be able to reduce motion and flashes. Gameplay events originate in the simulation; animation can represent them but cannot create hits or damage.
