# INSTALLATION_AUDIT.md — DocForge

_Audit installation avant modification._

## Existant

- `install.sh` (31 lignes) : `pip install --user -r requirements.txt` puis
  `docforge init && docforge doctor`. Pas de venv, pas de résolution de
  PATH, pollue le Python utilisateur.
- `install.ps1` (14 lignes) : équivalent Windows, mêmes défauts,
  `python` (souvent 2.x sur Windows), pas d'`ExecutionPolicy`, pas
  d'AppData, pas de PATH.
- `bin/docforge` : wrapper bash qui exporte `DOCFORGE_ROOT` et exécute
  `python3 -m docforge.cli`. Suppose un checkout local.
- `docforge_cli.py` : shim exécutable.
- `requirements.txt` : `python-docx`, `lxml`, `PyYAML`, `pytest`.
- `docforge/__init__.py` : `__version__ = "0.1.0"` (obsolète : la v0.2
  est déjà mergée).
- CLI existante : `init`, `run`, `status`, `audit`, `plan`, `verify`,
  `score`, `improve`, `report`, `final-audit`, `doctor`, `install`,
  `pause`, `stop`, `reset`, `interview`, `inspect`, `structure`,
  `format`, `layout`, `visual`, `tables`, `figures`, `formulas`,
  `references`, `language`, `resume`, `providers`, `workers`,
  `audit-tasks` (21+ commandes).
- `cmd_install` : appelle `cmd_init` et affiche « Pour une installation
  complète : ./install.sh ». Stub.
- `cmd_doctor` : détection basique de providers + `docx`, `libreoffice`.

## Problèmes identifiés

1. **Pas de bootstrap sans clone préalable.** L'installer suppose
   `HERE = repo checkout` — inutilisable via `curl … | bash`.
2. **Pas de venv privé.** Pollution du Python utilisateur.
3. **Pas de PATH configuré.** L'utilisateur doit ajouter manuellement.
4. **Pas de commande `docforge update`.** Aucun update path.
5. **Pas de commande `docforge uninstall`.** Aucun retour arrière.
6. **Pas de gestion de versions.** `__version__` obsolète.
7. **Pas de rollback.** Une mise à jour ratée casse l'installation.
8. **Pas de vérification d'intégrité** des téléchargements.
9. **Pas de migrations** des schémas entre versions.
10. **Windows** : `python` vs `python3`, pas de PATH, pas d'AppData.
11. **Confusion install/projet.** L'`install.sh` initialise un `.docforge/`
    dans le CWD au lieu de séparer runtime vs projet.
12. **Version** dispersée : `docforge/__init__.py`, README, DOCFORGE.md
    n'ont pas la même valeur.

## À réutiliser

- `docforge/cli.py` : point d'entrée déjà solide.
- `docforge/capabilities.py` : détection providers.
- `.docforge/completion/gates.py` : peut évaluer les gates d'installation.

## Décisions

- **Emplacement runtime** : `~/.docforge/` (Linux/macOS) et
  `%LOCALAPPDATA%\DocForge` (Windows) avec sous-dossiers
  `versions/<version>/`, `venv/`, `current` (symlink ou pointer
  fichier), `cache/`, `state/`.
- **Projet** : `.docforge/` dans le CWD (déjà en place), inchangé.
- **PATH** : `~/.local/bin/docforge` (POSIX) et
  `%LOCALAPPDATA%\DocForge\bin\docforge.cmd` (Windows). L'installeur
  ajoute ce dossier au PATH s'il n'y est pas.
- **Bootstrap** : `install.sh` et `install.ps1` téléchargeables et
  exécutables via `curl | bash` / `irm | iex`. Ils clonent (ou
  téléchargent l'archive) puis appellent `python3 -m docforge.installer
  bootstrap`.
- **Version** : source unique `docforge/_version.py` (`VERSION = "0.2.0"`),
  ré-exportée par `docforge/__init__.py`.
- **Migrations** : `docforge/migrations/` (`001_initial.py`,
  `002_completion_engine.py`, …), registre append-only, exécutées lors
  d'`update`.
- **Intégrité** : SHA-256 sur les archives téléchargées.
- **Rollback** : `~/.docforge/versions/<vprev>/` conservé.

## Ce qui NE sera pas fait dans cette session

- Publication PyPI / Homebrew / winget (l'architecture est prête ; la
  publication est un acte externe).
- Test réel du bootstrap depuis internet (le sandbox n'y a pas accès —
  les tests utiliseront un tarball local).
- Auto-update silencieux (interdit par le prompt §21).
