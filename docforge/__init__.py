"""DocForge — Autonomous multi-agent document reconstruction engine.

The core is provider-agnostic. Adapters (Claude Code, Codex, Gemini,
Cursor, Qwen, OpenCode, …) plug into the same core.
"""
from __future__ import annotations

from ._version import VERSION as __version__

__all__ = ["__version__"]
