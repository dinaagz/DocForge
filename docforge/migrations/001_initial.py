"""001_initial — ensure the runtime layout exists."""
from __future__ import annotations

ID = "001_initial"
DESCRIPTION = "Create the DocForge runtime directory layout."


def apply() -> None:
    from ..installer import layout
    layout.ensure_layout()
