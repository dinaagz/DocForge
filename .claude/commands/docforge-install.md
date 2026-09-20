---
description: Installe DocForge dans le layout utilisateur (bootstrap local)
argument-hint: "[--source <chemin>]"
---

Lance `python -m docforge.cli install $ARGUMENTS`.

Copie le code source dans `~/.docforge/versions/<version>/` (POSIX) ou
`%LOCALAPPDATA%\DocForge\versions\<version>\` (Windows), installe un
launcher `docforge` sur PATH-friendly, exécute les migrations.

Alternative distante (une commande) :

- POSIX : `curl -fsSL https://raw.githubusercontent.com/dinaagz/DocForge/main/install.sh | bash`
- Windows : `irm https://raw.githubusercontent.com/dinaagz/DocForge/main/install.ps1 | iex`

Après installation : `docforge --version` puis `/docforge-doctor`.
