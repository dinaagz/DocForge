---
description: Audit engine — détecte les anomalies et persiste les Issues
---

Lance `python -m docforge.cli audit`.

Le Audit Engine parcourt le modèle canonique et produit des `Issue`
persistées dans `.docforge/audits/issues.jsonl`. Rapporte :

- le nombre d'anomalies détectées ;
- les catégories touchées (metadata, structure, language, accessibility,
  intégrité, …) ;
- le fichier de persistance.

Enchaîne avec `/docforge-plan` pour transformer les Issues en checklist
priorisée.
