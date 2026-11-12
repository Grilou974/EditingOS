# DA « droits du quotidien » — validée le 13/11/2026

« c'est super, on enregistre vraiment cette DA »

Exemples complets : `exemples/barista-tasses`, `exemples/caution-mur-jauni` (gen.py, detoure.py, prises.json).

## Règles
- Personnage principal : TOUJOURS Grilou, qui raconte à la 1re personne (« Je suis barista et j'ai cassé ma 4e tasse du mois »). Vouvoiement du public pour les conseils de fin.
- Trame (réf. explication pro) : la situation dès la 1re phrase → l'article de loi → le calcul → ce que je fais (mail, lettre) → le recours → la chute.
- Plus de chat 2D : sa voix + ses éléments 3D (planche fournie, détourée élément par élément) + mes schémas faits maison.
- Fond : un décor qui correspond au sujet (illustration fournie : café, appartement…), assombri par un dégradé et un vignettage, avec un lent zoom de 7 %.
- Tout est descendu : scène entre y ≈ 560 et 1200, sous-titres vers y 1330, rien d'important au-dessus de y ≈ 450 (interface TikTok).
- Persos PETITS sur les côtés (≈ 300-400 px, gauche x≈300 / droite x≈760) ; l'autre perso arrive en face et le premier reste. Un perso qui pointe pointe VERS l'autre (miroir si besoin). Les persos ne bougent pas davantage.
- Schémas maison en HTML avec nos polices : fiche de paie, article de loi tapé et surligné à la main, cartes en verre sombre, échelle ✔/✖, jauge, frise, compteurs, étapes avec icônes, lettre recommandée qui se coche, cartes de fin côte à côte. Ne jamais entourer ce qui est déjà annoté sur ses images.
- Chaque info apparaît DÈS le début de la phrase qui en parle, reste jusqu'à la fin de la scène et s'accumule à l'écran. Les éléments liés vont l'un sous l'autre ; les pastilles d'une même rangée sont alignées automatiquement (jamais l'une sur l'autre).
- Vie à l'écran sans bouger les persos : cartes qui respirent, pastilles rouges/jaunes qui pulsent, poussières qui montent, pièces ou éclats qui tombent, compteurs, petites secousses. Le reflet lumineux seulement sur 2-3 cartes clés, invisible tant qu'il ne passe pas.
- Sous-titres mot à mot en bas, Lilita One en capitales, mots-clés en jaune.
- Voix : dernières bonnes prises, blancs serrés sans couper de mot (contrôle automatique par transcription), 0,12 s de silence avant le 1er mot ; CTA violet avec un Grilou 3D et SA phrase de fin de la prise.
- Détourage : vérifier chaque élément en grand sur fond clair (bords coupés, morceaux des voisins) avant de monter.

## Fabriquer une vidéo
1. `blocs.py` sur la voix pour repérer les prises, puis `prises.json` (dernières bonnes prises).
2. `voix_ref.py` : voix serrée + words.json.
3. `detoure.py` : éléments de la planche → `assets/img`, puis contrôle sur fond clair.
4. `gen.py` (moteur `da_pro.py`, `finir(..., fond=...)`), snapshots de chaque scène.
5. `npx hyperframes@0.8.164 render -o renders/_video.mp4 .` puis `mix_ref.py <sortie>.mp4`.
