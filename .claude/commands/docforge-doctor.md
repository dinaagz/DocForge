---
description: Rapport de santé DocForge (Python, formats, outils, providers)
---

Lance `python -m docforge.cli doctor` et présente le rapport.

Chaque ligne est classée OK / WARNING / MISSING / ERROR. Un
`WARNING` ou `MISSING` sur un outil optionnel (LibreOffice, Pandoc,
Ghostscript) ou un provider (Claude Code, Codex, Gemini, …) n'est
**pas** un blocage : DocForge fonctionne sans.

Si une ligne `ERROR` remonte, propose un correctif ciblé (installation,
mise à jour Python, PATH).
