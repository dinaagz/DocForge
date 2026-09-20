---
description: Génère la checklist priorisée à partir des Issues
---

Lance `python -m docforge.cli plan`.

La checklist est écrite dans `.docforge/checklists/current.json`. Elle
transforme chaque Issue en tâche avec :

- priorité (0 = CRITICAL … 3 = LOW) ;
- catégorie, sévérité, localisation ;
- action recommandée, dépendances ;
- preuve attendue.

Rappelle : la checklist est la source de vérité de ce qui reste à
corriger — un run `/docforge-improve` peut la consommer.
