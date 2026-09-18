"""Claude Code adapter — delegates to the generic runtime when the CLI
is not present, so DocForge always works.
"""
from __future__ import annotations

import shutil
from typing import Any, Dict, Optional

from .base import ProviderAdapter, ProviderResult
from .registry import register


class ClaudeCodeAdapter(ProviderAdapter):
    name = "claude-code"
    capabilities = ["filesystem", "shell", "python", "agents", "parallel_agents", "background"]

    def available(self) -> bool:
        return shutil.which("claude") is not None

    def run_agent(self, agent: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ProviderResult:
        # Deterministic worker impl is always the ground truth; the Claude CLI
        # can be attached by adapters/claude-code/ for interactive sessions.
        from ..workers.registry import run_worker
        return run_worker(agent, context or {"prompt": prompt})


register(ClaudeCodeAdapter())
