---
description: Désinstalle DocForge (préserve les projets utilisateur)
argument-hint: "[--dry-run] [--purge]"
---

Lance `python -m docforge.cli uninstall $ARGUMENTS`.

- `--dry-run` : imprime le plan JSON, aucune suppression.
- `--purge` : supprime aussi le ledger runtime (versions installées,
  config). Sans `--purge`, il est conservé pour rollback.

**Jamais** touché : les dossiers projet `input/`, `output/`, `work/`,
`.docforge/`, `logs/`.

Rappelle à l'utilisateur : la désinstallation ne touche pas non plus au
Python système ni à `pip`.
