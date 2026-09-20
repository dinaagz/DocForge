---
description: Completion Guard — refuse DONE sans preuves
---

Lance `python -m docforge.cli final-audit`.

Vérifie que **toutes les gates `required: true`** passent, que
**chaque exigence du CONTRACT.yaml** est couverte, et qu'il n'y a **pas
de régression bloquante**.

Rapporte :

- verdict DONE / NOT_DONE ;
- gates non satisfaites (avec raison) ;
- exigences non couvertes ;
- régression détectée le cas échéant ;
- nombre total de preuves enregistrées.

Doctrine : **NO CLAIM OF COMPLETION WITHOUT EVIDENCE.**
