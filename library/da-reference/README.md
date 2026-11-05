# DA de référence TV cat — validée le 05/11/2026 (« j'adore, on garde tout »)

Modèle complet de la vidéo GBH, à copier pour chaque nouvelle vidéo.

## Ce qu'est la DA
- **Fond** : vraies vidéos du sujet, nettes quand Grilou parle seul, floutées dès qu'on explique.
- **Grilou** : là dès la 1re image (arrivée en 0,15 s), gros sur le fond net, petit sur les petites illustrations, absent des gros plans. Une expression toutes les ≈ 2 s, accordée au propos.
- **Texte** : Lilita One en capitales, contour noir, ombre BD, mots-clés jaunes ; bandeaux penchés au feutre (Permanent Marker) ; cartes jaunes/blanches à bord noir. Aucun texte sur une image.
- **Explications** : 2D propre (barres, cercles, schémas), vrais clips Pixabay en cadre, dessins maison détourés (`montages/essence/assets/img/sprites`), 3D très rare (le caddie).
- **Voix** : aucun temps mort au début, ≈ 0,1 s entre les idées, jamais un mot coupé, dernière bonne prise.
- **Son** : musique discrète adaptée au sujet (-29 LUFS), bruitages de la compil sans en abuser.
- **CTA** : écran violet, chat aux yeux étoilés, gros « Like et abonne-toi <3 », arrivée sur « Si la vidéo t'a plu », texte pile sur « like », toujours avec sa voix.
- **Titre du début** : bien centré sur l'écran (x = 540 px).
- **TikTok** : centre visuel x ≈ 495 px, largeur ≤ 760 px, y entre 250 et 1480 px.

## Fabriquer une vidéo
1. `couper.py` puis `affiner.py` : voix.
2. `bg.py` : fonds net et flou.
3. `gen.py` : composition (`index.html`, `sfx.json`).
4. `npx hyperframes@0.8.164 render -o renders/_video.mp4 .` puis `mix.py`.
