---
description: Évalue les gates DocForge (CHECK/EXPECT)
argument-hint: "[--gate G-XXX]"
---

Lance `python -m docforge.cli verify $ARGUMENTS`.

Sans argument : évalue toutes les gates listées dans
`.docforge/completion/GATES.yaml` et affiche un tableau PASS/FAIL avec
le nombre total.

Avec `--gate G-XXX` : évalue une seule gate et affiche la raison de
l'éventuel échec (regex non trouvée, exit code, output).

Une gate ne peut pas être marquée PASS si son processus quitte non-zéro
ou si sa sortie ne matche pas le regex EXPECT — le passage à `DONE` est
gouverné par le CompletionGuard.
