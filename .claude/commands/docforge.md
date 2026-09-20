---
description: Pilote DocForge — dispatch vers audit/run/doctor/update/…
argument-hint: "<sous-commande> [args…]"
---

Exécute la sous-commande DocForge : `$ARGUMENTS`.

1. Lance `python -m docforge.cli $ARGUMENTS` depuis la racine du repo
   (ou `./bin/docforge $ARGUMENTS` si le PATH utilisateur est configuré).
2. Rapporte la sortie fidèlement, sans réinterpréter — DocForge doit
   rester la source de vérité.
3. Si `$ARGUMENTS` est vide, montre `docforge --help` et propose les
   sous-commandes usuelles (`init`, `audit`, `run`, `doctor`, `update`,
   `verify`, `score`, `improve`, `final-audit`).

Doctrine DocForge : **NO CLAIM OF COMPLETION WITHOUT EVIDENCE.**
