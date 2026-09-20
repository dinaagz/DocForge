# Architecture de l'installeur

## Séparation stricte application / utilisateur

```
INSTALLATION (runtime, géré par l'installeur)
─────────────────────────────────────────────
Linux / macOS   ~/.docforge/
Windows         %LOCALAPPDATA%\DocForge\

    versions/<version>/     ← code + resources par version
    venv/                   ← environnement Python privé (optionnel)
    cache/                  ← téléchargements
    state/                  ← ledger installés + migrations + config
    current                 ← pointeur (fichier texte) vers la version active
    bin/  (Windows)         ← docforge.cmd
~/.local/bin/docforge (POSIX)

PROJET (utilisateur, JAMAIS touché par update/uninstall)
─────────────────────────────────────────────
<CWD>/.docforge/            ← état projet, mémoire, audits, checklists
<CWD>/input/                ← documents source
<CWD>/work/                 ← étape intermédiaire
<CWD>/output/               ← livrables
<CWD>/logs/
```

## Modules Python

| Module | Rôle |
|--------|------|
| `docforge._version`         | Source unique de la version (`VERSION`). |
| `docforge.installer.layout` | Chemins runtime par OS. |
| `docforge.installer.version`| Comparaison semver-like (`compare`, `is_newer`). |
| `docforge.installer.integrity` | SHA-256 fichiers + manifests. |
| `docforge.installer.state`  | Registre des versions installées + config. |
| `docforge.installer.doctor` | Rapport structuré OK/WARNING/MISSING/ERROR. |
| `docforge.installer.updater`| `check_only`, `apply`, `preserves`. |
| `docforge.installer.rollback` | `list_versions`, `can_rollback`, `rollback`. |
| `docforge.installer.uninstaller` | `plan_uninstall`, `uninstall`. |
| `docforge.installer.bootstrap` | `install` (copie + launcher + migrations). |
| `docforge.migrations`       | Registre versionné, exécution idempotente. |

## Séquence d'installation

```
install.sh / install.ps1
  ├─ detect OS / arch
  ├─ locate Python ≥ 3.9
  ├─ locate source tree  (checkout, sinon tar.gz depuis GitHub)
  └─ python -m docforge.cli install --source <src>
        └─ docforge.installer.bootstrap.install()
              ├─ layout.ensure_layout()
              ├─ shutil.copytree src → versions/<ver>/
              ├─ écrit launcher POSIX ou Windows
              ├─ écrit `current` pointer
              ├─ state.record_installed(ver, path)
              └─ migrations.run_pending()
```

## Séquence de mise à jour

```
docforge update [--check | --archive <path> [--sha256 <hex>]]
  ├─ updater.check_only(source, channel)
  ├─ (optionnel) télécharge l'archive dans cache/
  ├─ integrity.verify_sha256
  ├─ tarfile.extractall → versions/<ver>-staging/  (path-traversal safe)
  ├─ rename staging → versions/<ver>/
  ├─ migrations.run_pending()
  ├─ state.record_installed(ver, path)  → current = ver
  └─ échec avant renommage ⇒ la version précédente reste active
```

## Rollback

- Chaque installation historique reste sous `versions/<ver>/`.
- `docforge update --rollback` bascule le pointeur `current` sur
  l'entrée précédente et met à jour `state/installed.json`.

## Migrations

Répertoire `docforge/migrations/`. Chaque migration :

- expose `ID` (`NNN_name`), `DESCRIPTION`, `apply()` ;
- est **idempotente** : elle peut être rejouée sans effet de bord ;
- est enregistrée dans `state/migrations.json` après exécution.

## Sécurité

- `updater.apply` refuse toute archive contenant un chemin remontant.
- L'installeur ne demande jamais `sudo`.
- Aucun code externe n'est exécuté depuis l'archive téléchargée : seuls
  les fichiers sont copiés, puis DocForge est invoqué par
  `python -m docforge.cli`.
