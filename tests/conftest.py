"""Pytest fixtures for document processing loop tests."""

import json
import os
import shutil
import sys
from pathlib import Path

import pytest

# Add scripts/ to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from common import STATE_DIR, WORK_DIR, INPUT_DIR, OUTPUT_DIR, LOGS_DIR


@pytest.fixture(autouse=True)
def clean_state(tmp_path):
    """Use temporary directories for state during tests."""
    # We don't want to overwrite real state during tests
    pass


@pytest.fixture
def sample_docx(tmp_path):
    """Create a minimal test DOCX document."""
    from docx import Document
    from docx.shared import Pt

    doc = Document()

    # Add title
    doc.add_heading("Document de Test", level=0)

    # Add some sections with headings
    sections = [
        ("Introduction", 1, "Ceci est l'introduction du document de test. "
         "Elle contient plusieurs phrases pour simuler un vrai document académique."),
        ("Chapitre 1 : Contexte", 1, "Le contexte de cette étude est important. "
         "Nous examinons les facteurs qui influencent les résultats."),
        ("1.1 Historique", 2, "L'historique remonte à plusieurs décennies. "
         "Les premières études ont été menées dans les années 1990."),
        ("1.2 État de l'art", 2, "L'état de l'art actuel montre des avancées significatives. "
         "Plusieurs auteurs ont contribué à ce domaine."),
        ("Chapitre 2 : Méthodologie", 1, "La méthodologie employée repose sur une approche mixte. "
         "Nous combinons des méthodes quantitatives et qualitatives."),
        ("2.1 Collecte de données", 2, "Les données ont été collectées sur une période de six mois. "
         "L'échantillon comprend 150 participants."),
        ("Chapitre 3 : Résultats", 1, "Les résultats montrent une corrélation significative. "
         "Le coefficient de détermination est de 0,85."),
        ("Conclusion", 1, "En conclusion, cette étude démontre l'importance du sujet. "
         "Des recherches futures sont nécessaires."),
        ("Bibliographie", 1, "Dupont, J. (2020). Titre de l'ouvrage. Éditeur.\n"
         "Martin, A. (2019). Autre titre. Éditeur."),
    ]

    for title, level, body in sections:
        doc.add_heading(title, level=level)
        p = doc.add_paragraph(body)
        # Add a few more paragraphs to simulate real content
        for i in range(3):
            doc.add_paragraph(
                f"Paragraphe supplémentaire {i+1} de la section « {title} ». "
                f"Ce texte sert à simuler un document plus long avec du contenu réel."
            )

    path = tmp_path / "test_document.docx"
    doc.save(str(path))
    return path
