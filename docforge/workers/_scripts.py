"""Bridge to existing deterministic Python scripts under scripts/."""
from __future__ import annotations

import subprocess
import sys
from typing import List, Tuple

from ..paths import SCRIPTS_DIR


def run_script(name: str, *args: str, timeout: int = 600) -> Tuple[int, str, str]:
    script = SCRIPTS_DIR / name
    cmd: List[str] = [sys.executable, str(script), *args]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                           cwd=str(SCRIPTS_DIR))
        return r.returncode, r.stdout, r.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"timeout after {timeout}s"
    except Exception as e:  # noqa: BLE001
        return -1, "", str(e)
