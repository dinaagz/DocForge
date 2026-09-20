"""DocForge installer / updater / uninstaller.

Public entry points:
- `docforge.installer.layout`    : runtime paths per OS.
- `docforge.installer.version`   : semver-like comparison.
- `docforge.installer.integrity` : SHA-256 verification of archives.
- `docforge.installer.state`     : installed versions + migration ledger.
- `docforge.installer.doctor`    : structured health checks.
- `docforge.installer.updater`   : check / download / apply / verify.
- `docforge.installer.rollback`  : list versions + revert.
- `docforge.installer.uninstaller`: safe uninstall plan (preserves user data).
- `docforge.installer.bootstrap` : CLI-facing install command.

Doctrine: application ≠ user data. Never delete input/, output/, work/,
.docforge/ inside a project during update or uninstall.
"""
from __future__ import annotations

from . import layout, version, integrity, state, doctor  # noqa: F401
from . import updater, rollback, uninstaller, bootstrap  # noqa: F401
