---
description: Boucle d'amélioration autonome bornée
argument-hint: "[--max-iters N]"
---

Lance `python -m docforge.cli improve $ARGUMENTS` (par défaut 3
itérations).

Chaque itération :

1. **audit** → issues.
2. **correction** (si branché) → applique les fixes proposés.
3. **verify** (subset rapide de gates).
4. **score** sur 100.
5. **compare** au meilleur score connu.
6. **stop** si stagnation, oscillation, régression bloquante, budget
   ou DONE.

Rapport final : nombre d'itérations, raison d'arrêt, meilleur score.
Rappelle : la meilleure version connue est préservée
(`.docforge/scores/versions.json`).
