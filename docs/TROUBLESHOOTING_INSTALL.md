# Dépannage de l'installation

## `python3 not found` (macOS / Linux)

Installez Python ≥ 3.9 (`brew install python`, `apt install python3`, …)
puis relancez `./install.sh`.

## `Aucun Python >= 3.9 detecte` (Windows)

Installez Python depuis <https://python.org> **en cochant** « Add Python
to PATH ». Redémarrez PowerShell puis relancez.

## PATH ne contient pas `~/.local/bin`

L'installeur affiche la ligne à ajouter à votre shell rc, par exemple :

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Sur Windows :

```powershell
setx PATH "%LOCALAPPDATA%\DocForge\bin;%PATH%"
```

Puis rouvrez le terminal.

## Politique d'exécution PowerShell

Si `install.ps1` refuse de s'exécuter :

```
powershell -ExecutionPolicy Bypass -File install.ps1
```

## `docforge doctor` signale un warning

Les warnings pour LibreOffice, Pandoc, Ghostscript ou les CLI providers
(Claude Code, Codex, Gemini, …) ne bloquent pas DocForge. Installez ces
outils uniquement si vous en avez besoin (export PDF, provider externe).

## Mise à jour interrompue

DocForge extrait toujours dans un dossier de staging avant de faire
basculer le pointeur `current`. Un `docforge update` interrompu ne
modifie donc pas la version active. Relancez la commande.

## Rollback

```
docforge update --rollback
```

Revient à la version précédente déclarée dans le registre
(`~/.docforge/state/installed.json`).

## Désinstaller

```
docforge uninstall
```

Ou depuis un checkout : `./uninstall.sh`. Vos projets `.docforge/`,
`input/`, `output/`, `work/` ne sont **jamais** supprimés par la
désinstallation.
