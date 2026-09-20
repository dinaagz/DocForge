# DOCFORGE — Protocole portable

DOCFORGE est un moteur autonome multi-agents de reconstruction, correction,
mise en forme et contrôle qualité documentaire.

Ce fichier définit le PROTOCOLE portable. Il permet à n'importe quelle
plateforme IA (Claude Chat, ChatGPT, Gemini, Qwen, Kimi, Grok, etc.) de
faire fonctionner DOCFORGE en mode chat lorsqu'un runtime d'exécution
n'est pas disponible.

## Identité

- Nom : DOCFORGE
- Version : 0.1.0
- Cœur : indépendant du fournisseur
- Sortie : document reconstruit + rapport

## Objectif

Prendre un document source (DOCX/PDF), en extraire un **modèle canonique**,
proposer une **structure reconstruite**, appliquer des **corrections
rédactionnelles**, produire un document final **propre, professionnel et
homogène**, puis générer un **rapport en français**.

## Architecture

01. **PLANIFICATEUR** — décide quoi faire, dans quel ordre, avec quelles dépendances.
02. **BUILDERS** — exécutent les tâches (extraction, structure, langue, mise en forme, assemblage).
03. **VÉRIFICATEURS** — jamais les mêmes que les builders. Contrôlent le résultat.
04. **MÉMOIRE** — persiste décisions, corrections, hypothèses, rationale.
05. **GESTIONNAIRE** — distribue, surveille, gère files/priorités/dépendances.
06. **CONTRÔLEUR** — supervise le système. Détecte stagnation/régression. Ordonne REPLAN.

## Boucle

```
PLAN → BUILD → VERIFY → MEMORY → CONTROL → REPLAN → RECOMMENCE
```

## Règles

1. Ne jamais réécrire un long document entièrement.
2. Toujours utiliser un état persistant (STATE.json).
3. Toujours journaliser (events).
4. IDs paragraphe stables (P000001…), hash SHA-256.
5. Séparer production et vérification.
6. Une anomalie documentaire ≠ panne système.
7. 5 échecs locaux max → PENDING_MANUAL, on passe au suivant.
8. Ne jamais inventer (source/citation/auteur/chiffre/date).
9. Source immutable.
10. Numérotation du source = PAS d'autorité — reconstruire à partir du contenu.

## États système

INIT, RUNNING, DONE, DONE_WITH_REVIEW_ITEMS, BLOCKED, FAILED_SYSTEM, PAUSED, STOPPED.

## États de tâche

PENDING, READY, RUNNING, WAITING, COMPLETED, FAILED, RETRYING, BLOCKED, PENDING_MANUAL.

## Format de tâche

```json
{
  "id": "T-xxxxxxxx",
  "type": "extract|structure_extract|canonical_build|format_document|verify|export|final_report|...",
  "agent": "extractor|formatting-agent|integrity-verifier|...",
  "priority": 40,
  "dependencies": ["T-yyyyyyyy"],
  "status": "PENDING",
  "input": {},
  "output": {},
  "resource_locks": ["branch:language"],
  "retry_count": 0,
  "max_retries": 3
}
```

## Critères de fin

- DONE : toutes les tâches COMPLETED, aucun échec, aucun élément en revue.
- DONE_WITH_REVIEW_ITEMS : certaines tâches en PENDING_MANUAL ou peu d'échecs — le document est produit, quelques éléments demandent revue humaine hors ligne.
- BLOCKED : trop d'échecs, ou budget épuisé.
- FAILED_SYSTEM : réservé aux pannes réelles (panne d'IO, provider absent alors qu'il est indispensable).

## Rapport

Toujours produit en français, dans `output/DOCFORGE_REPORT.md` + `.json`.

## Architecture universelle (v0.2)

Doctrine additionnelle : **NO CLAIM OF COMPLETION WITHOUT EVIDENCE.**

- `docforge.formats` : Universal Document Kernel (DOCX/TXT/Markdown
  implémentés, XLSX/PDF/PPTX/HTML/ODT/CSV enregistrés comme stubs
  déclaratifs — leurs opérations lèvent explicitement `NotAvailable`).
- `docforge.audit` : Audit Engine + Issue Registry + Checklist Engine.
- `docforge.completion` : Contract, Gates, Evidence, Score (0–100 sur
  ≥10 dimensions), Regression, Versioning (best-version), CompletionGuard.
- `docforge.improvement.loop` : boucle audit → correction → verify →
  score → compare → improve avec détection stagnation/oscillation/budget.
- `docforge.contract.interviewer` : générateur de squelette CONTRACT.

Anti-slop (§19) :

```
DO NOT GUESS.
DO NOT SKIP.
DO NOT CLAIM WITHOUT EVIDENCE.
DO NOT DESTROY WORKING PARTS.
DO NOT FINISH PREMATURELY.
```

## Mode chat vs mode code

- **Mode code** : le runtime exécute réellement les workers en parallèle (Python, threads/processus).
- **Mode chat** : la plateforme ne peut pas exécuter — le modèle simule le protocole en gardant STATE.json et TASKS.json à jour, une étape atomique à la fois. Aucune promesse d'exécution parallèle native.

En mode chat, le modèle doit :

1. Lire STATE.json + TASKS.json.
2. Prendre UNE tâche READY, l'exécuter (ou produire le résultat attendu), écrire l'output.
3. Marquer la tâche COMPLETED, sauver le nouvel état.
4. Répéter jusqu'à un état terminal.

## Adaptation au provider

Le protocole ne change pas. Seul l'adapter change. Voir `adapters/`.
