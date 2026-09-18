# DocForge — Mode chat (CHAT COMPATIBILITY MODE)

Ce dossier contient les artefacts permettant à un modèle sans exécution
locale (ChatGPT, Claude Chat, Gemini, Qwen, Kimi, Grok, etc.) de faire
avancer DocForge à la main.

## Comment charger DocForge dans un chat

Envoyez ces fichiers dans la conversation, dans l'ordre :

1. `DOCFORGE.md` — le protocole.
2. `AGENTS.md` — la liste des agents.
3. `LOOP.yaml` — le format machine.
4. Votre `STATE.json` initial (ou vide) et votre `TASKS.json`.
5. Le document source (extrait/paragraphes).

## Contrainte honnête

Un chat sans exécution :

- NE peut PAS lancer plusieurs agents en parallèle.
- NE peut PAS maintenir un heartbeat.
- NE peut PAS accéder au filesystem.

Le mode chat exécute les tâches **séquentiellement**, une par tour. À
chaque tour, le modèle :

1. Lit STATE.json + TASKS.json.
2. Choisit UNE tâche READY (dépendances satisfaites).
3. Produit son output selon le protocole.
4. Met à jour TASKS.json (status COMPLETED) et STATE.json.
5. Répond avec les deux fichiers mis à jour.

## Prompt d'entrée

Copiez `entrypoint.md` dans le chat pour amorcer la session.
