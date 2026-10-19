# TV Cat Editing — atelier de montage

Plateforme locale qui pilote des projets vidéo HyperFrames montés par l'IA.

## Lancer

Double-clic sur `Lancer-TVCatEditing.cmd`, ou :

```
node server.mjs
```

puis ouvrir http://localhost:4321. Aucune dépendance à installer (Node 18+).

## Onglets

- **Projets** — chaque dossier contenant `hyperframes.json` sous les racines de `config.json` (`roots`). Un projet peut contenir plusieurs vidéos (`renders/*.mp4`). Un rendu est **périmé** quand les sources ont changé après le dernier rendu.
- **Fiche projet** — lecteur, chemin du fichier, versions, et **Apporter des modifications** : retours horodatés écrits dans `FEEDBACK.md` + `editingos/feedback.json` du projet.
- **Studio** — timeline réelle (`hyperframes timeline`), retours placés dessus, lancement du Studio HyperFrames et des rendus avec journal.
- **Bibliothèques** — `library/formats.json` (disposition des éléments), `library/charte/` (mes animations), `library/references.json` (styles de chaînes).
- **Activité** — journal (`data/activity.jsonl`).

## Pour le monteur IA (Claude)

Avant de monter une vidéo : lire `library/formats.json`, `library/charte.json` (et les fichiers HTML qu'il cite), `library/references.json`.
Pour traiter des retours : lire `FEEDBACK.md` du projet, appliquer, re-rendre, passer les retours à `"status": "fait"` dans `editingos/feedback.json`.
Métadonnées d'un projet (titre, famille, type, tags, `utility`) : `editingos.json` à la racine du projet.

## Chaînes, genres et note automatique

- **Chaînes** : `library/channels.json` (TV Cat, Coaching Master, Seleckt…). Chaque projet indique la sienne dans `editingos.json` → `"channel": "TV Cat"` (sinon déduite du dossier : `montages/` → TV Cat, `montages-ow/` → Coaching Master, `seleckt/` → Seleckt). La page Projets les range par chaîne, puis par **genre** (`"genre"` dans `editingos.json`).
- **Note automatique /10** : calculée par `score.mjs` sur le dernier rendu, avec ffmpeg — format, durée (selon la chaîne), volume (−14 LUFS), rythme visuel, blancs, accroche, retours ouverts, rendu à jour. Mise en cache dans `editingos/score.json`, recalculée à chaque nouveau rendu.
- **Avis du monteur IA** : texte libre dans `"avis"` de `editingos.json`, affiché sur la fiche projet.
