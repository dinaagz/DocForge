"""Abstract provider adapter interface."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ProviderResult:
    ok: bool
    output: Dict[str, Any] = field(default_factory=dict)
    error: str = ""


class ProviderAdapter:
    """All providers implement this shape. Absent capability → NotImplemented."""

    name: str = "abstract"
    capabilities: List[str] = []

    def available(self) -> bool:
        return True

    def run_agent(self, agent: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ProviderResult:
        raise NotImplementedError

    def spawn_agent(self, agent: str, prompt: str, context: Optional[Dict[str, Any]] = None) -> ProviderResult:
        return self.run_agent(agent, prompt, context)

    def read_file(self, path: str) -> ProviderResult:
        try:
            with open(path, "r", encoding="utf-8") as fh:
                return ProviderResult(ok=True, output={"content": fh.read()})
        except Exception as e:  # noqa: BLE001
            return ProviderResult(ok=False, error=str(e))

    def write_file(self, path: str, content: str) -> ProviderResult:
        try:
            with open(path, "w", encoding="utf-8") as fh:
                fh.write(content)
            return ProviderResult(ok=True)
        except Exception as e:  # noqa: BLE001
            return ProviderResult(ok=False, error=str(e))

    def run_command(self, argv: List[str], **kwargs: Any) -> ProviderResult:
        import subprocess
        try:
            r = subprocess.run(argv, capture_output=True, text=True, **kwargs)
            return ProviderResult(ok=(r.returncode == 0),
                                  output={"stdout": r.stdout, "stderr": r.stderr, "rc": r.returncode})
        except Exception as e:  # noqa: BLE001
            return ProviderResult(ok=False, error=str(e))

    def parallel(self) -> bool:
        return True

    def background(self) -> bool:
        return False
