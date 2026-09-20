"""003_universal_document_model — sanity-check the extended canonical schema."""
from __future__ import annotations

ID = "003_universal_document_model"
DESCRIPTION = "Verify canonical.new_model exposes the extended field set."


def apply() -> None:
    from ..canonical import new_model
    m = new_model()
    required = {"sections", "blocks", "pages", "slides", "sheets",
                "tables", "figures", "images", "charts", "formulas",
                "styles", "references", "citations", "bibliography",
                "hyperlinks", "embedded_objects", "external_dependencies",
                "calculations", "accessibility", "provenance",
                "issue_links", "verification_evidence"}
    missing = sorted(required - set(m.keys()))
    if missing:
        raise RuntimeError(f"canonical model missing fields: {missing}")
