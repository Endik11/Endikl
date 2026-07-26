from __future__ import annotations

from .content_registry import get_default_registry
from .definitions import ArenaDefinition


# Compatibility view backed by the registry; no arena data is duplicated here.
ARENAS = get_default_registry().arenas
