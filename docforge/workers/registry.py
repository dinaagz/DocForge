"""Worker registry — every agent name resolves to a Python callable."""
from __future__ import annotations

from typing import Any, Callable, Dict, List

from ..providers.base import ProviderResult

WorkerFn = Callable[[Dict[str, Any]], Dict[str, Any]]

_WORKERS: Dict[str, WorkerFn] = {}


def register(name: str, fn: WorkerFn) -> None:
    _WORKERS[name] = fn


def list_workers() -> List[str]:
    return sorted(_WORKERS)


def run_worker(name: str, context: Dict[str, Any]) -> ProviderResult:
    fn = _WORKERS.get(name)
    if not fn:
        return ProviderResult(ok=False, error=f"unknown worker: {name}")
    try:
        out = fn(context) or {}
        return ProviderResult(ok=True, output=out)
    except Exception as e:  # noqa: BLE001
        return ProviderResult(ok=False, error=str(e))
