---
description: Initialise un projet DocForge dans le répertoire courant
---

Crée la structure d'un projet DocForge dans le CWD :

1. Vérifie que `docforge --version` fonctionne (sinon, indique
   `install.sh` / `install.ps1`).
2. Lance `python -m docforge.cli init`.
3. Confirme l'apparition de `.docforge/`, `input/`, `work/`, `output/`,
   `logs/`.
4. Rappelle à l'utilisateur qu'il peut déposer un DOCX dans `input/`
   puis lancer `/docforge-run`.
