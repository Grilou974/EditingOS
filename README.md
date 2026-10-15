# EditingOS — atelier de montage

Plateforme locale qui pilote des projets vidéo HyperFrames montés par l'IA.

## Lancer

Double-clic sur `Lancer-EditingOS.cmd`, ou :

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
