# Adaptateurs DocForge

Chaque sous-dossier est un adaptateur mince pour un environnement IA
particulier. Le cœur (`docforge/`) reste unique et agnostique — les
adapters se contentent de :

- déclarer les capacités
- fournir l'entry point (fichiers, prompts, hooks) que la plateforme attend
- déléguer la logique à `python -m docforge.cli`

## Adapters livrés

- `claude-code/` — pour Claude Code CLI (fichiers `.claude/agents/`, `.claude/skills/`).
- `codex/` — pour Codex CLI.
- `gemini/` — pour Gemini CLI.
- `cursor/` — pour Cursor Agent.
- `qwen/` — pour Qwen Code.
- `opencode/` — pour OpenCode.
- `generic/` — pour tout runtime capable d'exécuter `bash` + `python`.

Ajouter un nouveau provider : dupliquer `generic/`, adapter le manifeste.
