"""Provider adapter registry.

The core never says `if claude:`. It calls ProviderAdapter methods.
Adapters translate DocForge intents to the provider's runtime.
"""
from __future__ import annotations

from .base import ProviderAdapter, ProviderResult
from .registry import get, register, available, select

__all__ = ["ProviderAdapter", "ProviderResult", "get", "register", "available", "select"]

# Register built-in adapters
from . import generic  # noqa: F401,E402
from . import claude_code  # noqa: F401,E402
from . import codex  # noqa: F401,E402
from . import gemini  # noqa: F401,E402
from . import cursor  # noqa: F401,E402
from . import qwen  # noqa: F401,E402
from . import opencode  # noqa: F401,E402
