# La Petite-Nation (MRC de Papineau) : commentaires

Toutes les municipalités de la MRC de Papineau (Outaouais) selon le
MRNF : 25 municipalités et le TNO aquatique (la rivière des Outaouais).
Rien n'a encore été envoyé à OSM.

Rapports générés : [régions](regions.md), [rues](rues.md) et
[adresses](adresses.md), avec leurs cartes ([regions.geojson](regions.geojson),
[rues.geojson](rues.geojson), [adresses.geojson](adresses.geojson)).
Configuration : [lieux/Petite-Nation.toml](../../lieux/Petite-Nation.toml).

Données : RQA version AQ20261001, Découpages administratifs V2026-09,
extrait OSM de Geofabrik du 16 octobre 2026.

## 1. Régions

### Constat

- Les 25 municipalités ont une relation de limite dans OSM, trouvée par
  son code (`ref:qc`). Deux particularités :
  - **Notre-Dame-de-la-Salette** est rattachée dans OSM à la MRC des
    Collines-de-l'Outaouais, alors que le MRNF la place dans Papineau;
  - le **TNO aquatique** de la MRC n'a pas de relation dans OSM.
- Les limites d'OSM sont surtout faites de chemins propres, mais huit
  municipalités du sud (Fassett, Montebello, Notre-Dame-de-Bonsecours,
  Papineauville, Plaisance, Thurso, Lochaber, Lochaber-Partie-Ouest)
  utilisent aussi le tracé de la rivière (`waterway=river`) : le cas à
  éviter.
- Avec les limites actuelles d'OSM, **23 adresses sur 20 659** tombent du
  mauvais côté ou hors de toute municipalité. Par exemple :
  - chemin de la Plage (Val-des-Bois), placé dans Notre-Dame-de-la-Salette;
  - chemin du Ruisseau (Notre-Dame-de-la-Salette), placé dans Val-des-Bois;
  - route 315 (Ripon), placée dans Montpellier;
  - chemin Monaghan (Mayo), placé dans Lochaber-Partie-Ouest;
  - 2112 et 2116 chemin du Tour-du-Lac (Lac-Simon), placés dans Duhamel.

### Remplacement proposé

- 80 chemins de limite neufs, d'après le MRNF (7 872 nœuds) : une limite
  commune à deux municipalités est un seul chemin, membre des deux
  relations. Cela vaut aussi pour les limites avec les municipalités
  voisines, hors de la MRC (règle 10 des régions).
- Frontière avec l'Ontario, dans la rivière des Outaouais : gardée telle
  qu'elle est dans OSM (règle 11). Les sept municipalités riveraines
  (Fassett, Montebello, Notre-Dame-de-Bonsecours, Papineauville,
  Plaisance, Thurso, Lochaber) reprennent les chemins de la frontière
  d'OSM, coupés en 9 points, sans être déplacés, là où leurs limites du
  MRNF les rejoignent; les relations du Québec, de l'Ontario et du
  Canada reçoivent les morceaux.
- 12 voisines hors de la MRC (Grenville-sur-la-Rouge, Harrington,
  Huberdeau, Amherst, La Minerve, Notre-Dame-du-Laus, Lac-Ernest,
  Gatineau, L'Ange-Gardien, Val-des-Monts, Denholm, Lac-Sainte-Marie)
  sont modifiées en partie : l'arc commun entre dans leur relation, leurs
  anciens chemins le long de la MRC en sortent, 7 chemins de limite sont
  coupés au bout de la partie gardée, et 17 courts raccords provisoires
  relient l'arc commun à leurs anciens points triples. Ils disparaîtront
  quand ces voisines seront traitées. Deux autres voisines n'ont pas de
  relation dans OSM (TNO aquatiques).
- MRC et régions (règle 12) : Argenteuil, Les Laurentides,
  Antoine-Labelle, Les Collines-de-l'Outaouais, La Vallée-de-la-Gatineau,
  la région des Laurentides et celle de l'Outaouais prennent les arcs de
  la MRC sur leur contour; 11 raccords provisoires les relient à leurs
  anciens chemins. La MRC de Papineau n'est pas modifiée (voir les
  questions en suspens).
- 45 relations modifiées; 53 chemins retirés des relations, tous de
  simples lignes de limite devenues inutiles, supprimées. Les rivières
  qui ne sont pas la frontière ne sont pas touchées.
- Essai : le fichier d'envoi a été appliqué à une copie de l'extrait du
  Québec, comme si OSM l'avait accepté. Les 69 relations entièrement
  présentes dans l'extrait forment toutes des anneaux fermés (les 13
  autres, comme l'Ontario ou le Canada, débordent de l'extrait), et
  relancer la préparation ne produit plus rien.
- Vérification : avec les limites proposées, les 20 659 adresses tombent
  dans la bonne municipalité.
- Lien avec le nœud de lieu : 16 relations sur 25 ont leur membre
  `label`. Sept n'en ont pas (Lochaber-Partie-Ouest, Mulgrave-et-Derry,
  Montpellier, Lac-Simon, Lac-des-Plages, Duhamel, Val-des-Bois), et
  deux pointent vers un nœud sans `place` (Notre-Dame-de-Bonsecours,
  Lochaber). À régler à la main; détail dans
  [regions.md](regions.md#lien-avec-le-nœud-de-lieu).

### Routes qui traversent les limites

| Situation | Nombre |
|---|---|
| Déjà coupée au bon endroit | 22 |
| Coupure à déplacer | 39 |
| Coupure à ajouter | 140 |

Les coupures à ajouter touchent surtout les routes numérotées et les
grands chemins : autoroute Guy-Lafleur (6), chemin Townline (5), chemin
du Lac-Gagnon Est (4), routes 309, 315 et 323. Liste complète dans
[regions.md](regions.md#routes-qui-traversent-les-limites).

Les coupures à ajouter et à déplacer sont faites dans le fichier
d'envoi : 143 chemins coupés, 163 nœuds ajoutés sur les routes, 178
segments neufs, et 19 relations de route mises à jour (détail dans
[regions.md](regions.md#routes-coupées)). Une ancienne coupure devenue
inutile est fusionnée (chemin Ivall). Celle du chemin du Marais est
gardée : la route traverse trois fois la nouvelle limite, et l'ancienne
coupure sert encore à l'un de ces croisements. Les autres anciennes
coupures séparent des segments aux étiquettes différentes (un pont, un
changement de revêtement) et sont gardées.

### Questions en suspens

1. **Relation de la MRC** (7572164) : elle garde ses anciens chemins.
   Le long de la rivière des Outaouais, son contour borde le TNO
   aquatique de la MRC, qui n'a pas de relation dans OSM : aucune
   municipalité ne reprend la frontière d'OSM sur ce tronçon, et
   l'outil ne sait pas encore y raccorder la MRC. Faut-il créer la
   relation du TNO aquatique (question 3), ou faire suivre la frontière
   d'OSM à la MRC elle-même?
2. **Notre-Dame-de-la-Salette** : corriger son rattachement à la MRC de
   Papineau dans OSM?
3. **TNO aquatique** : créer sa relation, ou laisser la rivière hors des
   municipalités comme aujourd'hui?
4. **Coupures** : 140 à ajouter et 39 à déplacer, toutes faites selon
   la règle 7. À vérifier dans la discussion publique avant l'envoi.

## 2. Rues

| Situation | Rues | Adresses |
|---|---|---|
| Conforme | 1 260 | 19 497 |
| À renommer (casse, accents, tirets, abréviations) | 33 | 741 |
| Nom différent dans OSM | 49 | 278 |
| Voie sans nom dans OSM | 30 | 112 |
| Absente d'OSM | 73 | 269 |

- **Renommage proposé : 45 segments**, par exemple « Chemin du Tour du
  Lac » qui devient « Chemin du Tour-du-Lac » (310 adresses), « Rue De La
  Forge » qui devient « Rue de la Forge », « Rang Des Sources » qui
  devient « Rang des Sources », « Impasse L P Lesage » qui devient
  « Impasse L.-P.-Lesage », « Rue St. Andrew » qui devient « Rue
  Saint-Andrew ».
- **Abréviations** : le RQA écrit « Rue St-Julien », « Rue St-Denis »
  (Papineauville) ou « Chemin St-Pierre » (Saint-André-Avellin, Ripon);
  OSM a la forme complète. Selon la règle d'OSM, la forme complète est
  gardée (« Saint- »), et ces rues sont maintenant conformes.

### Exceptions à valider

- **Point cardinal** : « Route 321 Sud » (RQA) contre « Route 321 »
  (OSM), 60 adresses.
- **Ordinaux** : « 1re Avenue » (RQA) contre « 1e Avenue » (OSM).
- **Générique** : « Rue Sainte-Julie Est » (RQA) contre « Rang
  Sainte-Julie Est » (OSM).
- **Voies sans nom** le long des adresses (30 rues), par exemple Impasse
  des Conifères (Val-des-Bois, 20 adresses), Chemin des Chênes-Rouges.
- **Rues absentes** (73 rues, 269 adresses), dont l'**Île du
  Canard-Blanc** (lac Simon, 103 adresses), une île sans route.

### Questions en suspens

1. **Adresses d'une île** (Île du Canard-Blanc) : dans OSM, une adresse
   sans rue utilise `addr:place` plutôt que `addr:street`. Faut-il
   traiter ces cas ainsi?
2. **Nommer les voies sans nom** d'après le RQA : par règle, ou à la main?

## 3. Adresses

| Résultat | Nombre |
|---|---|
| Nouvelles, prêtes à créer | 19 430 |
| Déjà dans OSM, corrigées | 173 |
| Déjà dans OSM, inchangées | 52 |
| À revoir, non créées | 1 544 |
| Exclues | 1 |

- Les chiffres tiennent compte des renommages de rues prévus.
- Logements et suffixes fusionnés : 1 263 adresses en avaient; 676
  numéros n'ont pas d'adresse principale au RQA (on prend le point d'un
  logement ou d'un suffixe). Les logements vont dans `addr:unit` (401
  adresses), les suffixes en lettre dans `addr:housenumber` (576
  adresses, par exemple « 1;1A;1B »).
- **363 logements douteux écartés** de `addr:unit` : sans lot ni
  matricule, sur une adresse d'un seul logement selon le rôle (voir
  [Logements douteux du RQA](../../README.md#logements-douteux-du-rqa)).
  288 viennent du chargement du RQA du 11 décembre 2021. Surtout à
  Lac-Simon (97), Duhamel (61) et Saint-André-Avellin (38). Ceux de
  Duhamel ont été signalés au MRNF le 13 octobre 2026; les autres
  restent à signaler. Liste complète, avec l'identifiant du RQA, dans
  [adresses.md](adresses.md#logements-douteux).
- Exclusion : le 131 chemin du Tour-du-Lac (Duhamel), absent du rôle
  d'évaluation.
- **3 925 lignes d'interpolation CanVec supprimées** (48 380 nœuds),
  seulement celles des rues importées, à moins de 300 m d'une adresse de
  la même rue et attribuées à une municipalité de la MRC.
- **Positions peu précises** : parmi les nouvelles adresses, seulement
  3 507 sont de qualité « Bâtiment »; 9 538 sont « Géocodée », 6 016
  « Incertaine », 301 « Centre lot » et 68 « Front lot ». Le point est
  souvent au bord de la route plutôt que sur le bâtiment.

### Questions en suspens

1. **Précision** : avec 80 % de points « Géocodée » ou « Incertaine »,
   l'import vaut-il mieux que les interpolations qu'il remplace? Les
   numéros deviennent exacts, mais la position reste approximative. Les
   portes d'entrée de la Chaire Mobilité couvrent l'est du Québec, pas
   l'Outaouais.
2. **Ampleur** : 19 430 nœuds et 3 925 interpolations supprimées en un
   seul envoi, ou par municipalité?

## 4. Prochaines étapes

1. Régler les questions des limites (contour de la MRC, TNO,
   Notre-Dame-de-la-Salette), puis discussion publique.
2. Noms de rue : appliquer les renommages sûrs, trancher les autres.
3. Adresses, probablement municipalité par municipalité.
