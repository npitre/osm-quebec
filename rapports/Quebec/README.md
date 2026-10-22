# Québec : frontières et municipalités absentes d'OSM

Première étape de l'import : remplacer les limites municipales de tout
le Québec par celles du MRNF, par bouchées assez petites pour être
acceptées par OSM. Avant de commencer, deux vérifications : les
frontières du Québec avec ses voisins, et les municipalités du MRNF qui
n'ont pas de relation dans OSM. Rien n'a été envoyé à OSM.

Rapports générés par `outils/frontieres.py` :
[frontières](frontieres.md), avec leur carte
([frontieres.geojson](frontieres.geojson) : les points de la frontière
du MRNF à plus de 100 m du tracé d'OSM), et
[municipalités absentes](municipalites.md).

Données : Découpages administratifs du MRNF, version V2026-09, extrait
OSM de Geofabrik du 16 octobre 2026, et contour de l'Ontario (jeu
« Province » de Géospatial Ontario, géométrie de 2019).

## 1. Frontières du Québec

En attendant d'en discuter, **les frontières extérieures existantes sont
gardées** : les municipalités qui les touchent reprendront les chemins
actuels de la relation du Québec, au lieu de tracer le MRNF par-dessus.

### Constat

Écart entre la frontière du MRNF et celle d'OSM (relation du Québec,
61549), en médiane et pour 90 % des points :

| Frontière | Médiane | 90 % à moins de |
|---|---|---|
| États-Unis | 0 m | 1 m |
| Nouveau-Brunswick | 11 m | 46 m |
| Ontario | 58 m | 193 m |
| Labrador, le long du 52e parallèle | 14 m | 80 m |
| Labrador, ligne de partage des eaux | 232 m | plus de 5 km |
| Nunavut | 189 m | 3,5 km |
| Golfe du Saint-Laurent | 44 m | 5,2 km |

- **États-Unis** : les deux tracés concordent. Aucun problème.
- **Nouveau-Brunswick** : bonne concordance, en rivière (Ristigouche,
  Patapédia) comme sur la ligne terrestre jusqu'au Maine, autour de
  10 m. Les deux tracés passent au milieu de la rivière, qui n'a que
  quelques dizaines de mètres de large. Les écarts de plus de 1 km sont
  dans l'estuaire, là où la rivière s'élargit vers la baie des Chaleurs.
- **Ontario** :
  - Dans la rivière des Outaouais, les deux tracés passent au milieu de
    l'eau, mais pas sur le même milieu : 60 m d'écart en médiane, plus
    de 200 m pour 10 % des points. Dans OSM, la frontière est sur un
    tiers de sa longueur l'axe même de la rivière (57 chemins
    `waterway=river`), ailleurs une ligne tracée à la main près de lui.
  - Ces écarts ne viennent pas d'OSM : sa frontière avec l'Ontario est,
    à quelques exceptions près, exactement le tracé officiel de
    l'Ontario (jeu « Province » de Géospatial Ontario, tenu par le
    bureau de l'arpenteur général; 94 % des nœuds d'OSM à moins de 5 m).
    C'est entre les deux gouvernements que le tracé diffère : 60 m en
    médiane entre l'Ontario et le MRNF. L'Ontario annonce une précision
    « à 100 m près », à partir de sources diverses.
  - La ligne terrestre, du lac Témiscamingue à la baie James, suit le
    méridien 79°31′ O. Aucun des tracés n'est exactement sur ce méridien
    mathématique :
    - le MRNF est de 70 à 87 m à l'ouest, de façon presque constante
      sur 400 km;
    - l'Ontario (et OSM, qui le suit) passe progressivement de 65 m à
      l'ouest, au 48e parallèle, à 8 m à l'est, au 51e.

    Un décalage constant est ce qu'on attendrait d'une ligne bornée sur
    le terrain au début du XXe siècle : les arpenteurs fixaient la
    longitude par l'astronomie, et cette longitude diffère de la
    longitude moderne (NAD83) de quelques dizaines de mètres, parce que
    la verticale locale n'est pas exactement perpendiculaire à
    l'ellipsoïde. Une fois bornée, la ligne légale est celle des bornes,
    pas le chiffre 79°31′. Le tracé ontarien, qui pivote régulièrement,
    ressemble plutôt à une ligne tracée entre quelques points éloignés.
    C'est une hypothèse, à vérifier avec la position de quelques bornes
    du méridien.
  - Près de la baie James, les tracés s'écartent de 0,6 à 2 km : les
    sources ne traitent pas la côte de la même façon.
- **Labrador** : le cas le plus délicat. Le long du 52e parallèle, la
  concordance est bonne (14 m en médiane), sauf par endroits (7 % des
  points à plus de 1 km). Le long de la ligne de partage des eaux, les
  tracés diffèrent souvent de plusieurs kilomètres. Une partie de cette
  frontière est toujours contestée par le Québec; aucun chemin d'OSM n'y
  porte d'étiquette `disputed*`, `note` ou `fixme`.
- **Nunavut et golfe du Saint-Laurent** : le Québec d'OSM s'arrête au
  littoral (820 de ses 1 358 chemins sont `natural=coastline`), alors
  que le MRNF suit une limite en mer. Ce sont deux conceptions
  différentes plutôt que des erreurs.

### Définition légale de la frontière avec l'Ontario

La frontière remonte à la proclamation de 1791 qui a divisé la province
de Québec en Haut et Bas-Canada[^1]; la *Canada (Ontario Boundary) Act*
de 1889 l'a confirmée telle que cette proclamation l'avait fixée[^2].
Deux documents d'experts décrivent ce que ces textes disent et comment
on les applique :

- Jean-Paul Lacasse (1977)[^3] : « Le segment de l'Outaouais, pour sa
  part, est délimité et la frontière se trouve au milieu du chenal
  principal de la rivière des Outaouais. Mais la frontière n'est pas
  démarquée [...] ». Seules les lignes terrestres droites sont bornées
  sur le terrain (Vaudreuil-Soulanges et le méridien 79°31′ jusqu'à la
  baie James). Pour la Ristigouche, la loi de 1851 retient aussi le
  milieu du chenal et attribue les îles au Nouveau-Brunswick, mais la
  rivière a changé depuis.
- Commission de toponymie du Québec (1984)[^4] : dans le lac
  Saint-François, le Saint-Laurent, l'Outaouais et le lac
  Témiscamingue, « les textes mentionnent le milieu du chenal comme
  étant la limite entre les deux provinces »; le terme peut désigner le
  point médian de la largeur maximale du plan d'eau, le chenal principal
  ou le chenal navigable. Une convention de 1980 règle le tracé dans le
  lac Saint-François et le Saint-Laurent; pour l'Outaouais, « le tracé
  apparaissant sur les cartes topographiques nationales est considéré
  satisfaisant pour le moment, même si la juridiction sur plusieurs îles
  reste à préciser ».

Conséquences :

- La limite légale est le milieu du **chenal principal**, pas le milieu
  de la rivière, ni l'axe `waterway=river` dessiné dans OSM; dans une
  rivière large et parsemée d'îles, le chenal principal peut être loin
  du centre géométrique.
- En pratique, le tracé de référence de l'Outaouais est celui des cartes
  topographiques nationales, dont celui du MRNF vient très probablement.
- Le méridien 79°31′ est borné sur le terrain : la ligne légale est
  celle des bornes. Le tracé du MRNF, décalé de façon constante du
  méridien mathématique, est compatible avec une ligne bornée; celui de
  l'Ontario, qui pivote, l'est moins (voir plus haut).

Ces deux documents sont anciens; le texte de la convention de 1980 et
d'éventuelles ententes plus récentes sur les îles de l'Outaouais restent
à trouver.

[^1]: Archives publiques de l'Ontario, [limites de l'Ontario en 1791](https://www.archives.gov.on.ca/en/maps/textdocs/ontario-boundaries-1791.aspx).
[^2]: [Canada (Ontario Boundary) Act, 1889](https://primarydocuments.ca/canada-ontario-boundary-act-1889/).
[^3]: Jean-Paul Lacasse, [« L'état des frontières du Québec »](https://www.erudit.org/en/revue/rgd/1977/v8/n1/1059611ar.pdf), *Revue générale de droit*, vol. 8, no 1, 1977.
[^4]: Renaud Dugas, Commission de toponymie du Québec, [communication sur la toponymie transfrontalière](https://unstats.un.org/unsd/geoinfo/UNGEGN/docs/11th-gegn-docs/11th_gegn_WP%20no%207_F.pdf), document de travail no 7, 11e session du Groupe d'experts des Nations Unies pour les noms géographiques, Genève, 1984.

### Questions en suspens

1. **Ontario** : OSM suit le tracé officiel de l'Ontario, qui diffère
   de celui du Québec. Lequel suit les bornes et les textes légaux? Sur
   la ligne terrestre, la position de quelques bornes du méridien
   (levés de l'arpenteur général, repères géodésiques de RNCan)
   permettrait de trancher. Remplacer la frontière par le tracé du MRNF
   voudrait dire préférer la version québécoise : à discuter avec les
   contributeurs ontariens, puisque la relation de l'Ontario partage ces
   chemins. Et faut-il que frontière et rivière partagent la même
   ligne? La règle 2 des régions (décidée à la rencontre du 16 octobre)
   dit non : l'axe de la rivière est un tracé approximatif de
   l'écoulement, corrigé au fil des améliorations, alors que la
   frontière est le milieu du chenal principal, une ligne officielle
   fixe (voir ci-dessus); ici, les deux sont à 76 m l'une de l'autre en
   médiane. La question mérite toutefois d'être reposée.
2. **Nouveau-Brunswick** : même question, mais les écarts sont faibles;
   seul l'estuaire de la Ristigouche mérite un examen.
3. **Labrador** : garder le tracé actuel d'OSM; faut-il y ajouter une
   étiquette `disputed_by` ou une note là où le Québec conteste la
   frontière?
4. **Nunavut et golfe** : les municipalités côtières doivent-elles
   s'arrêter au littoral, comme aujourd'hui, ou suivre la limite en mer
   du MRNF, comme aux Îles-de-la-Madeleine?

## 2. Municipalités absentes d'OSM

Sur les 1 342 municipalités du MRNF, 1 243 ont une relation dans OSM
portant leur code (`ref:qc`). Les 99 autres :

- **52 TNO aquatiques** (les parties en eau de chaque MRC, comme dans la
  Petite-Nation).
- **29 réserves et établissements autochtones** (Kahnawake, Kanesatake,
  Kitigan Zibi, Manawan, Mashteuiatsh, etc.). Dans OSM, ces territoires
  sont généralement des `boundary=aboriginal_lands`, pas des limites
  administratives; à vérifier un par un.
- **8 territoires non organisés de la Jamésie** au nom « Toponyme à
  venir ».
- **Terres autochtones du Nord** : Killiniq et Kiggaluk (terres
  inuites), la terre réservée naskapie de Kawawachikamach, Oujé-Bougoumou
  (terre réservée crie).
- **Cas particuliers** :
  - La Pocatière : sa relation porte `ref:qc=14085`, le MRNF donne
    14082;
  - le village naskapi de Kawawachikamach : sa relation porte
    `ref:qc=99605`, le MRNF donne 99065 (deux chiffres inversés?);
  - La Romaine et Akwesasne : une relation existe, mais sans `ref:qc`;
  - Lac-Simon et Cacouna : les réserves de ce nom n'ont pas de relation,
    seulement les municipalités homonymes.

À l'inverse, trois relations d'OSM ont un code inconnu du MRNF :
Hébertville, Hébertville-Station et Saint-Bruno, au niveau 10, avec leur
ancien code. Elles ont fusionné dans la nouvelle municipalité
d'Hébertville (93022), qui a déjà sa relation : OSM garde ici les
anciennes municipalités au niveau 10, un précédent pour la question des
anciennes municipalités (Îles-de-la-Madeleine).

### Questions en suspens

5. **TNO aquatiques** : créer leur relation, ou laisser l'eau hors des
   municipalités comme aujourd'hui?
6. **Territoires autochtones** : les traiter comme des municipalités
   (relation `boundary=administrative`), ou garder
   `boundary=aboriginal_lands` et seulement vérifier leur tracé?
7. **TNO de la Jamésie** sans nom : attendre leur nom officiel?
