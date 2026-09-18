"""Generic provider — pure Python, no external agent runtime.

Executes local scripts. Always available. This is what makes DocForge
run in ANY environment even when no LLM CLI is installed.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from .base import ProviderAdapter, ProviderResult
from .registry import register


class GenericAdapter(ProviderAdapter):
    name = "generic"
    capabilities = ["filesystem", "shell", "python", "parallel"]

    def run_agent(self, agent: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ProviderResult:
        # Generic mode has no LLM: it runs deterministic worker impls by name.
        from ..workers.registry import run_worker
        return run_worker(agent, context or {"prompt": prompt})


register(GenericAdapter())
