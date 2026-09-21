"""Fix typography issues in a DOCX file.

Corrections applied:
  1. Double spaces → single space
  2. French non-breaking spaces before ; : ? !
  3. Straight quotes → typographic quotes (« » and ')
  4. Trailing whitespace stripped
  5. Capitalize first letter of paragraphs (body text only, >30 chars)
"""
from __future__ import annotations

import argparse
import copy
import re
import sys
from pathlib import Path

import docx

NBSP = " "  # non-breaking space


def _fix_run_text(text: str, lang: str = "fr") -> str:
    """Apply all text-level fixes to a single run's text."""
    original = text

    # 1. Double spaces → single
    while "  " in text:
        text = text.replace("  ", " ")

    # 2. French nbsp before high punctuation
    if lang.startswith("fr"):
        text = re.sub(r" ([?!;])", NBSP + r"\1", text)
        text = re.sub(r" :", NBSP + ":", text)

    # 3. Straight quotes → typographic
    if lang.startswith("fr"):
        text = text.replace('" ', "« ")
        text = text.replace(' "', " »")
        if text.startswith('"'):
            text = "« " + text[1:]
        if text.endswith('"'):
            text = text[:-1] + " »"
    text = text.replace("'", "’")  # apostrophe typographique

    # 4. Trailing whitespace
    text = text.rstrip()

    return text


def fix_document(docx_path: Path, output_path: Path, lang: str = "fr") -> dict:
    doc = docx.Document(str(docx_path))
    stats = {
        "double_spaces": 0,
        "nbsp_fixes": 0,
        "quote_fixes": 0,
        "trailing_ws": 0,
        "capitalized": 0,
        "paragraphs_touched": 0,
    }

    for para in doc.paragraphs:
        touched = False
        full_text = para.text

        for run in para.runs:
            if not run.text:
                continue
            original = run.text
            fixed = _fix_run_text(original, lang)
            if fixed != original:
                if "  " in original:
                    stats["double_spaces"] += original.count("  ")
                if re.search(r" [?!;:]", original):
                    stats["nbsp_fixes"] += len(re.findall(r" [?!;:]", original))
                if '"' in original or "'" in original:
                    stats["quote_fixes"] += original.count('"') + original.count("'")
                if original != original.rstrip():
                    stats["trailing_ws"] += 1
                run.text = fixed
                touched = True

        # 5. Capitalize first letter (body paragraphs >30 chars only)
        if para.runs and para.text.strip():
            first_run = None
            for r in para.runs:
                if r.text and r.text.strip():
                    first_run = r
                    break
            if first_run and len(para.text) > 30:
                t = first_run.text
                # Find first alpha char
                for i, ch in enumerate(t):
                    if ch.isalpha():
                        if ch.islower():
                            first_run.text = t[:i] + ch.upper() + t[i + 1:]
                            stats["capitalized"] += 1
                            touched = True
                        break

        if touched:
            stats["paragraphs_touched"] += 1

    doc.save(str(output_path))
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="Fix typography in DOCX")
    parser.add_argument("--input", type=str, help="Input DOCX path")
    parser.add_argument("--output", type=str, help="Output DOCX path")
    parser.add_argument("--lang", default="fr", help="Language (default: fr)")
    args = parser.parse_args()

    src = Path(args.input) if args.input else Path("input/Memoire_Fin_d_annee_FINAL_V6.docx")
    out = Path(args.output) if args.output else Path("output/Memoire_Fin_d_annee_CORRIGE.docx")

    if not src.exists():
        print(f"Fichier introuvable : {src}", file=sys.stderr)
        return 1

    out.parent.mkdir(parents=True, exist_ok=True)
    stats = fix_document(src, out, lang=args.lang)

    print("Corrections appliquées :")
    print(f"  Double espaces corrigés   : {stats['double_spaces']}")
    print(f"  Espaces insécables ajoutés: {stats['nbsp_fixes']}")
    print(f"  Guillemets corrigés       : {stats['quote_fixes']}")
    print(f"  Espaces en fin de ligne   : {stats['trailing_ws']}")
    print(f"  Majuscules ajoutées       : {stats['capitalized']}")
    print(f"  Paragraphes modifiés      : {stats['paragraphs_touched']}")
    print(f"\nFichier corrigé : {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
