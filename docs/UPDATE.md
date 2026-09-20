# Mise à jour

## Vérifier

```
docforge update --check
```

Renvoie un JSON :

```json
{
  "channel": "stable",
  "current": "0.2.0",
  "latest": "0.2.1",
  "source": "github",
  "update_available": true
}
```

Rien n'est écrit sur disque à cette étape.

## Appliquer

```
docforge update
```

- télécharge la dernière release GitHub (canal `stable`) ;
- vérifie l'intégrité SHA-256 lorsqu'un manifest est publié ;
- extrait dans un dossier de staging (`versions/<version>-staging/`) ;
- passe atomiquement le pointeur `current` sur la nouvelle version ;
- exécute les migrations pendantes ;
- **ne touche à AUCUN dossier de projet** :
  `input/`, `output/`, `work/`, `logs/`, `.docforge/` restent
  strictement préservés.

En cas d'erreur (téléchargement corrompu, migration en échec, archive
invalide), la version courante n'est pas modifiée.

## Options

- `docforge update --force` : réinstalle même si vous êtes déjà à jour.
- `docforge update --channel beta` : canal alternatif (par défaut : `stable`).
- `docforge update --archive ./df.tar.gz --sha256 <hex>` : installe une
  archive locale déjà téléchargée.
- `docforge update --rollback` : revient à la version précédente
  installée (celle listée dans `~/.docforge/versions/`).
- `docforge update --rollback --to 0.1.0` : rollback ciblé.

## Auto-update

DocForge ne met **jamais** à jour silencieusement. Toute mise à jour est
explicite. Une option `auto_update: false` par défaut se trouve dans
`~/.docforge/state/config.json` (activable manuellement pour les
environnements CI).

## Depuis n'importe quel projet

`docforge update` met à jour l'application globale, indépendamment du
répertoire courant. Vos projets ne sont pas concernés.
