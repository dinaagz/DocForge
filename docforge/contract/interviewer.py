"""Interview stub — records requirements answered by the user.

This is a non-interactive helper (a real chat interview belongs to the
provider adapter). It accepts a dict of answers, produces a skeleton
CONTRACT and a matching DEFINITION_OF_DONE skeleton, and persists them.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml

from ..paths import DOCFORGE_DIR, ensure_layout

PROJECT_DIR = DOCFORGE_DIR / "project"
INTERVIEW_QUESTIONS: List[Dict[str, Any]] = [
    {"key": "objective", "prompt": "Objectif documentaire ?"},
    {"key": "context", "prompt": "Contexte ?"},
    {"key": "audience", "prompt": "Public ?"},
    {"key": "expected_output", "prompt": "Résultat attendu ?"},
    {"key": "constraints", "prompt": "Contraintes ?"},
    {"key": "untouchable", "prompt": "Éléments intouchables ?"},
    {"key": "rewrite_freedom", "prompt": "Liberté de réécriture ?"},
    {"key": "correction_level", "prompt": "Niveau de correction souhaité ?"},
    {"key": "format_output", "prompt": "Format de sortie ?"},
    {"key": "acceptance", "prompt": "Critères d'acceptation ?"},
]


def questions() -> List[Dict[str, Any]]:
    return list(INTERVIEW_QUESTIONS)


def skeleton_contract(answers: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "objective": answers.get("objective") or "",
        "context": answers.get("context") or "",
        "audience": answers.get("audience") or "",
        "expected_output": answers.get("expected_output") or "",
        "constraints": answers.get("constraints") or "",
        "untouchable": answers.get("untouchable") or "",
        "rewrite_freedom": answers.get("rewrite_freedom") or "",
        "correction_level": answers.get("correction_level") or "",
        "format_output": answers.get("format_output") or "",
        "acceptance": answers.get("acceptance") or "",
    }


def write_contract(answers: Dict[str, Any],
                   path: Path = PROJECT_DIR / "USER_CONTRACT.yaml") -> Path:
    ensure_layout()
    PROJECT_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(skeleton_contract(answers),
                                   allow_unicode=True, sort_keys=False),
                    encoding="utf-8")
    return path
