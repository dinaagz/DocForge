---
description: Lance la boucle complète DocForge (PLAN → BUILD → VERIFY → REPORT)
argument-hint: "[--budget <secondes>]"
---

Exécute `python -m docforge.cli run $ARGUMENTS` dans le projet courant.

1. Vérifie qu'un fichier est présent dans `input/`. Sinon, arrête et
   demande à l'utilisateur d'y déposer un document.
2. Lance le run, affiche le résultat final (`DONE`,
   `DONE_WITH_REVIEW_ITEMS`, `BLOCKED`, `FAILED_SYSTEM`).
3. À la fin, propose `/docforge-final-audit` pour l'audit complet et
   `/docforge-report` pour lire `output/DOCFORGE_REPORT.md`.
