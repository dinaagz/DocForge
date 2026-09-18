"""Codex CLI adapter (best-effort presence probe)."""
from __future__ import annotations

import shutil
from typing import Any, Dict, Optional

from .base import ProviderAdapter, ProviderResult
from .registry import register


class CodexAdapter(ProviderAdapter):
    name = "codex"
    capabilities = ["filesystem", "shell", "agents", "parallel_agents"]

    def available(self) -> bool:
        return shutil.which("codex") is not None

    def run_agent(self, agent: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ProviderResult:
        from ..workers.registry import run_worker
        return run_worker(agent, context or {"prompt": prompt})


register(CodexAdapter())
