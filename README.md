# DOCFORGE

**Moteur autonome multi-agents de reconstruction, correction, mise en
forme et contrôle qualité documentaire.**

DocForge prend un document source (DOCX/PDF), en construit un **modèle
canonique**, propose une **structure reconstruite**, applique des
**corrections rédactionnelles** et une **mise en forme professionnelle**,
puis produit un document final propre, un PDF audité et un **rapport
complet en français** — sans intervention humaine intermédiaire.

> Ce dépôt s'appelait auparavant **Loop**. Il a été migré vers
> **DocForge** : nouveau cœur agnostique, orchestration multi-agents,
> exécution parallèle, mode chat portable.

---

## Sommaire

1. [Pourquoi DocForge](#pourquoi-docforge)
2. [Architecture](#architecture)
3. [Système multi-agents](#système-multi-agents)
4. [Boucle récursive](#boucle-récursive)
5. [Parallélisation](#parallélisation)
6. [Mémoire persistante](#mémoire-persistante)
7. [État système](#état-système)
8. [Providers](#providers)
9. [Mode code / mode chat](#mode-code--mode-chat)
10. [Installation](#installation)
11. [Commandes](#commandes)
12. [Configuration](#configuration)
13. [Profils documentaires](#profils-documentaires)
14. [Traitement documentaire](#traitement-documentaire)
15. [Exemples](#exemples)
16. [Extension à un nouveau provider](#extension-à-un-nouveau-provider)
17. [Dépannage](#dépannage)
18. [Migration Loop → DocForge](#migration-loop--docforge)

---

## Pourquoi DocForge

Corriger un mémoire, une thèse, un rapport de 200 pages est un travail
que les outils actuels effectuent mal :

- les modèles réécrivent tout et perdent la voix de l'auteur ;
- ils inventent des chiffres, des citations, des dates ;
- ils oublient la moitié du document ;
- il n'y a ni traçabilité, ni rapport, ni rejeu possible.

DocForge résout ce problème comme une **organisation numérique** : un
planificateur, un gestionnaire, un contrôleur, une mémoire, et des
dizaines d'agents spécialisés qui travaillent en parallèle sur des
tâches indépendantes, avec vérification systématique par des agents
distincts.

## Architecture

```
                        ┌──────────────┐
                        │  PLANIFICATEUR│
                        └──────┬───────┘
                               │
                        ┌──────▼───────┐
                        │  GESTIONNAIRE│
                        └──────┬───────┘
        ┌──────────┬──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼          ▼
   EXTRACTION  STRUCTURE   LANGUE    COHÉRENCE   RÉFÉRENCES
        │          │          │          │          │
        └──────────┴──────────┼──────────┴──────────┘
                              ▼
                       ┌──────────────┐
                       │ MODÈLE CANONIQUE│
                       └──────┬───────┘
                              ▼
                       ┌──────────────┐
                       │ RECONSTRUCTION│
                       └──────┬───────┘
                              ▼
        ┌──────────┬──────────┼──────────┬──────────┐
        ▼          ▼          ▼          ▼          ▼
   INTEGRITY   FORMAT     LAYOUT   REFERENCES   PDF AUDIT
        │          │          │          │          │
        └──────────┴──────────┼──────────┴──────────┘
                              ▼
                       ┌──────────────┐
                       │  CONTRÔLEUR   │
                       └──────┬───────┘
                              ▼
                    PLAN → REPLAN → RECOMMENCE
```

Arborescence :

```
DocForge/
├── docforge/            # cœur agnostique (Python)
│   ├── planner.py
│   ├── manager.py
│   ├── controller.py
│   ├── scheduler.py
│   ├── tasks.py
│   ├── state.py
│   ├── memory.py
│   ├── canonical.py
│   ├── orchestrator.py
│   ├── report.py
│   ├── capabilities.py
│   ├── config.py
│   ├── cli.py
│   ├── providers/       # adapters d'exécution
│   └── workers/         # builders + verifiers déterministes
│
├── .docforge/           # état persistant + configuration
│   ├── config/
│   ├── profiles/
│   ├── providers/
│   ├── connectors/
│   ├── state/
│   ├── memory/
│   ├── model/           # canonical_document.json
│   └── chat/            # mode chat portable
│
├── adapters/            # adaptateurs plateforme (claude, codex, ...)
│
├── .claude/             # legacy — agents/skills Claude Code
├── scripts/             # scripts déterministes (DOCX/PDF) — réutilisés
├── config/              # config héritée (compatibilité)
├── input/  work/  output/  logs/
├── bin/docforge         # exécutable
├── docforge_cli.py      # exécutable Python (alt)
├── run.sh               # wrapper LEGACY vers docforge
├── install.sh install.ps1
├── DOCFORGE.md AGENTS.md LOOP.yaml
├── requirements.txt
└── README.md
```

## Système multi-agents

Trois familles :

- **Gouvernance** : `planner`, `manager`, `controller`, `report-agent`.
- **Builders** : `extractor`, `structure-architect`, `structure-applier`, `manifest-builder`, `formatting-agent`, `layout-agent`, `language-editor`, `style-editor`, `document-builder`, `assembler`, `exporter`.
- **Verifiers** (jamais les mêmes que les builders — règle §5) : `integrity-verifier`, `content-verifier`, `format-verifier`, `layout-verifier`, `language-verifier`, `structure-verifier`, `reference-verifier`, `pdf-verifier`, `coherence-agent`.

Voir `AGENTS.md` pour la liste complète.

## Boucle récursive

```
PLAN → BUILD → VERIFY → MEMORY → CONTROL → REPLAN → …
```

Le Contrôleur détecte stagnation, oscillation, régression, agent bloqué,
échec répété. Il ordonne un **REPLAN** au Planificateur, qui ajoute des
tâches correctives ciblées. La boucle n'est **pas** une pipeline linéaire.

## Parallélisation

Le scheduler exécute plusieurs workers simultanément (par défaut 4).
Les tâches indépendantes tournent réellement en parallèle. Un système
de **resource locks** empêche deux agents de modifier la même ressource.
Chaque tâche déclare ses `dependencies` et éventuellement ses
`resource_locks`.

## Mémoire persistante

`\.docforge/memory/` conserve, en `jsonl`, toutes les :

- **décisions** — quoi, pourquoi, quel agent.
- **corrections** — cible, avant/après, raison.
- **hypothèses** — texte, source, confiance.

Le système peut répondre à :

- « Pourquoi cette modification a-t-elle été faite ? »
- « Quel agent l'a faite ? »
- « Quel vérificateur l'a validée ? »

## État système

Un seul état canonique : `.docforge/state/`. La conversation IA n'est
jamais la source de vérité.

- `system.json` — statut global + itération.
- `tasks.json` — file de tâches persistante.
- `manual_review.json` — éléments laissés en revue humaine.
- `.docforge/model/canonical_document.json` — modèle documentaire.
- `.docforge/memory/events.jsonl` — journal d'événements.

## Providers

DocForge fonctionne avec n'importe quel provider :

| Provider    | Statut     | Détection                |
| ----------- | ---------- | ------------------------ |
| claude-code | pris en charge | `claude` dans PATH   |
| codex       | pris en charge | `codex` dans PATH    |
| gemini      | pris en charge | `gemini` dans PATH   |
| cursor      | pris en charge | `cursor-agent`       |
| qwen        | pris en charge | `qwen` dans PATH     |
| opencode    | pris en charge | `opencode` dans PATH |
| generic     | toujours   | fallback local (Python)  |

Le core ne contient jamais de `if claude:` — tout passe par
`ProviderAdapter`. Un provider absent n'est pas une erreur : DocForge
sélectionne automatiquement le suivant, en descendant jusqu'à `generic`.

## Mode code / mode chat

- **Mode code** — exécution réelle : threads, shell, filesystem, workers déterministes, boucle continue. C'est le mode par défaut.
- **Mode chat** — portable, pour Claude Chat, ChatGPT, Gemini, Qwen, Kimi, Grok, etc. La plateforme n'exécute pas ; elle simule le protocole en tenant à jour `STATE.json` + `TASKS.json`. Voir `.docforge/chat/`.

Nous n'affirmons **pas** qu'un chat sans exécution fournit un heartbeat
ou une exécution parallèle réelle. Le mode chat exécute les tâches
séquentiellement, une par tour.

## Installation

```bash
./install.sh                # POSIX
# ou
powershell -File install.ps1 # Windows

export PATH="$PWD/bin:$PATH"

docforge doctor              # vérifier l'environnement
docforge init                # créer la structure
```

Pré-requis : Python 3.9+, `python-docx`, `lxml`, `PyYAML`. LibreOffice
ou Pandoc facultatif pour le PDF.

## Commandes

```bash
docforge init         # initialise .docforge/
docforge doctor       # audit environnement + providers
docforge providers    # liste les providers disponibles
docforge workers      # liste les workers/agents enregistrés
docforge run          # exécute la boucle jusqu'à un état terminal
docforge status       # affiche l'état courant
docforge audit        # liste les tâches et leur statut
docforge report       # regénère le rapport final
docforge resume       # reprend depuis l'état sauvegardé
docforge pause        # marque le système en pause
docforge stop         # arrête (rejouable ensuite via resume)
docforge reset --force  # remise à zéro complète
```

L'ancienne interface `./run.sh …` reste disponible en mode LEGACY.

## Configuration

Layer merge : valeurs par défaut → `.docforge/config/*.yaml` → profil
(`.docforge/profiles/<name>.yaml`) → config héritée
`config/document_config.yaml` → variables d'environnement.

Variables :

- `DOCFORGE_PROFILE=academic|corporate|technical|institutional|minimal|custom`
- `DOCFORGE_CONCURRENCY=4`

## Profils documentaires

`.docforge/profiles/` contient : `academic`, `corporate`, `technical`,
`institutional`, `minimal`, `custom`. Chaque profil contrôle
police/tailles/interligne/marges/style rédactionnel/audience/ton.

## Traitement documentaire

1. Extraction paragraphes + inspection DOCX.
2. Extraction de structure brute (headings existants ignorés en tant qu'autorité).
3. Construction du **modèle canonique** (`canonical_document.json`).
4. Analyses parallèles (langue, cohérence, structure).
5. Reconstruction : structure verrouillée, mise en forme, assemblage.
6. Vérifications parallèles (intégrité, format, langue, structure).
7. Export DOCX + PDF.
8. Audit visuel PDF.
9. Rapport final français.

Si une tâche échoue 5 fois, elle passe en `PENDING_MANUAL` et le
workflow continue avec les autres.

## Exemples

```bash
# Traiter un document en profil académique avec 8 workers
DOCFORGE_PROFILE=academic DOCFORGE_CONCURRENCY=8 docforge run

# Reprendre après interruption
docforge resume

# Voir ce qui a été fait
docforge audit
docforge report
```

## Extension à un nouveau provider

1. Ajouter `docforge/providers/<name>.py` implémentant `ProviderAdapter`.
2. Ajouter `.docforge/providers/<name>.yaml` avec les capacités.
3. Ajouter `adapters/<name>/adapter.yaml` (mince).
4. Optionnel : `_registry.register(...)` dans `providers/__init__.py`.

Le core reste inchangé.

## Dépannage

- **`docforge: command not found`** — `export PATH="$PWD/bin:$PATH"`.
- **PDF non généré** — installez LibreOffice ou Pandoc.
- **Tâches bloquées** — `docforge audit` puis `docforge reset --force`.
- **Provider absent** — normal : `generic` prend le relais.

## Migration Loop → DocForge

Le repository GitHub doit être renommé de `dinaagz/Loop` en
`dinaagz/DocForge` (ou `dinaagz/docforge` si GitHub normalise). La
commande recommandée :

```bash
gh repo rename DocForge --repo dinaagz/Loop
# puis dans une copie locale :
git remote set-url origin https://github.com/dinaagz/DocForge.git
```

Statut de renommage : **à effectuer côté GitHub** — voir la section
« Statut du renommage GitHub » dans le rapport final.

---

_DocForge — 2026._
