#!/usr/bin/env python3
"""
export_pdf.py — Export a DOCX to PDF using LibreOffice.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from common import OUTPUT_DIR, get_logger, log_event

logger = get_logger("export_pdf")


def export(docx_path: Path, output_dir: Path) -> Path | None:
    """Convert DOCX to PDF via LibreOffice. Return PDF path or None."""
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if not soffice:
        logger.error("LibreOffice not found")
        return None

    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        soffice,
        "--headless",
        "--convert-to", "pdf",
        "--outdir", str(output_dir),
        str(docx_path),
    ]

    logger.info("Running: %s", " ".join(cmd))
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

    if result.returncode != 0:
        logger.error("LibreOffice failed: %s", result.stderr)
        return None

    pdf_name = docx_path.stem + ".pdf"
    pdf_path = output_dir / pdf_name
    if pdf_path.exists():
        logger.info("PDF exported: %s", pdf_path)
        return pdf_path

    logger.error("PDF not found after conversion")
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Export DOCX to PDF")
    parser.add_argument("input", help="Path to DOCX")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR), help="Output directory")
    args = parser.parse_args()

    inp = Path(args.input)
    if not inp.exists():
        logger.error("File not found: %s", inp)
        return 1

    pdf = export(inp, Path(args.output_dir))
    if pdf:
        log_event("PDF_EXPORTED", source=str(inp), output=str(pdf))
        print(json.dumps({"status": "ok", "pdf": str(pdf)}))
        return 0
    else:
        print(json.dumps({"status": "error", "message": "PDF export failed"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
