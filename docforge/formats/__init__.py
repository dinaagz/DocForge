"""Universal Document Kernel — format-agnostic core.

Every supported document format registers a `UniversalDocumentAdapter`
here. The rest of DocForge never touches format-specific code: it asks
the registry for an adapter and calls its abstract methods.

Rule: any adapter that is not fully implemented MUST declare
`implemented = False` and `capabilities = []`. Its operational methods
raise `NotImplementedError` with a clear message. No fake capability.
"""
from __future__ import annotations

from typing import Dict, List

from .base import UniversalDocumentAdapter, NotAvailable  # noqa: F401

registry: Dict[str, UniversalDocumentAdapter] = {}


def register(adapter: UniversalDocumentAdapter) -> None:
    registry[adapter.format_name] = adapter


def get(name: str) -> UniversalDocumentAdapter:
    a = registry.get(name.lower())
    if a is None:
        raise NotAvailable(f"unknown format: {name}")
    return a


def available() -> List[str]:
    """Formats with a functional adapter (implemented=True)."""
    return sorted(n for n, a in registry.items() if a.implemented)


def declared() -> List[str]:
    """All registered formats, including declarative stubs."""
    return sorted(registry.keys())


# ── Built-in adapters ──────────────────────────────────────────
from . import docx as _docx  # noqa: F401,E402
from . import txt as _txt  # noqa: F401,E402
from . import markdown as _md  # noqa: F401,E402
from . import stubs as _stubs  # noqa: F401,E402
