"""Provider adapter registry."""
from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from .base import ProviderAdapter

_registry: Dict[str, ProviderAdapter] = {}


def register(adapter: ProviderAdapter) -> None:
    _registry[adapter.name] = adapter


def get(name: str) -> Optional[ProviderAdapter]:
    return _registry.get(name)


def available() -> List[str]:
    return [n for n, a in _registry.items() if a.available()]


def select(preferred: Iterable[str]) -> ProviderAdapter:
    for name in preferred:
        a = _registry.get(name)
        if a and a.available():
            return a
    # Fall back to generic (always available)
    return _registry["generic"]
