---
description: Met à jour DocForge (avec vérification d'intégrité)
argument-hint: "[--check | --rollback [--to VER] | --channel stable|beta|dev]"
---

Lance `python -m docforge.cli update $ARGUMENTS`.

- Sans argument : applique la dernière release stable si une est
  disponible.
- `--check` : rapport JSON, aucun changement disque.
- `--rollback` : revient à la version précédente installée.
- `--archive <fichier.tar.gz> --sha256 <hex>` : installe depuis une
  archive locale vérifiée.

Rappelle à l'utilisateur : les dossiers projet (`input/`, `output/`,
`work/`, `.docforge/`, `logs/`) sont **strictement préservés**. Une mise
à jour interrompue laisse la version courante active.
