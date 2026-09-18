"""OpenCode adapter."""
from __future__ import annotations

import shutil
from typing import Any, Dict, Optional

from .base import ProviderAdapter, ProviderResult
from .registry import register


class OpenCodeAdapter(ProviderAdapter):
    name = "opencode"
    capabilities = ["filesystem", "shell", "agents"]

    def available(self) -> bool:
        return shutil.which("opencode") is not None

    def run_agent(self, agent: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ProviderResult:
        from ..workers.registry import run_worker
        return run_worker(agent, context or {"prompt": prompt})


register(OpenCodeAdapter())
