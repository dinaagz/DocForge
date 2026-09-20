---
description: Génère (et affiche) le rapport final DocForge en français
---

1. Lance `python -m docforge.cli report`.
2. Affiche le chemin des deux fichiers produits :
   `output/DOCFORGE_REPORT.md` et `output/DOCFORGE_REPORT.json`.
3. Lit `output/DOCFORGE_REPORT.md` et présente-le à l'utilisateur.

Le rapport contient : statut final, itérations, tâches, structure du
document canonique, agents exécutés, corrections appliquées, décisions
du planificateur et éléments en revue manuelle.
