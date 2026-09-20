# Installation

## Une commande

**macOS / Linux**

```bash
curl -fsSL https://raw.githubusercontent.com/dinaagz/DocForge/main/install.sh | bash
```

**Windows PowerShell**

```powershell
irm https://raw.githubusercontent.com/dinaagz/DocForge/main/install.ps1 | iex
```

L'installeur :

1. détecte votre OS et votre architecture ;
2. localise un Python ≥ 3.9 (aucune installation Python globale n'est
   modifiée) ;
3. télécharge le code source depuis GitHub si le répertoire courant
   n'est pas déjà un checkout ;
4. copie DocForge dans un dossier utilisateur privé :
   - `~/.docforge/versions/<version>/` (macOS/Linux)
   - `%LOCALAPPDATA%\DocForge\versions\<version>\` (Windows)
5. installe un lanceur `docforge` dans un dossier PATH-friendly :
   - `~/.local/bin/docforge` (macOS/Linux)
   - `%LOCALAPPDATA%\DocForge\bin\docforge.cmd` (Windows)
6. exécute les migrations internes ;
7. imprime, si nécessaire, la ligne à ajouter à votre PATH.

Aucun droit administrateur n'est requis pour l'installation normale.

## Vérifier

```
docforge --version
docforge doctor
```

`doctor` affiche un rapport structuré (OK / WARNING / MISSING / ERROR)
pour Python, les modules internes, les outils optionnels (LibreOffice,
Pandoc, Ghostscript) et les providers (Claude Code, Codex, Gemini, …).

## Utiliser DocForge dans un projet

```
mkdir mon-doc && cd mon-doc
docforge init             # crée .docforge/, input/, work/, output/, logs/
cp mon-fichier.docx input/
docforge run
```

`docforge init` ne réinstalle jamais DocForge. Il ne crée que le layout
d'un projet.

## Options

- Installation dev (checkout local) :
  ```
  git clone https://github.com/dinaagz/DocForge && cd DocForge
  ./install.sh --dev
  ```
- Emplacement personnalisé :
  ```
  DOCFORGE_HOME=/opt/docforge ./install.sh
  ```
- Sur Windows, si l'exécution du script est bloquée par la politique :
  ```
  powershell -ExecutionPolicy Bypass -File install.ps1
  ```
