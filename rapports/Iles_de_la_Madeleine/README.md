# Îles-de-la-Madeleine : commentaires

Banc d'essai convenu à la [rencontre du 16 octobre 2026](https://community.openstreetmap.org/t/148901).
Deux municipalités : Les Îles-de-la-Madeleine (01023) et Grosse-Île (01042).
Rien n'a encore été envoyé à OSM.

Rapports générés : [régions](regions.md), [rues](rues.md) et
[adresses](adresses.md), avec leurs cartes ([regions.geojson](regions.geojson),
[rues.geojson](rues.geojson), [adresses.geojson](adresses.geojson)).
Configuration : [lieux/Iles_de_la_Madeleine.toml](../../lieux/Iles_de_la_Madeleine.toml).

Données : RQA version AQ20261001, Découpages administratifs V2026-09,
extrait OSM de Geofabrik du 16 octobre 2026.

## 1. Régions

### Constat

Les deux limites municipales d'OSM sont faites du littoral : 417 chemins
`natural=coastline` sur 422 pour Les Îles-de-la-Madeleine, 65 sur 67
pour Grosse-Île. C'est le cas à éviter : corriger une rive déplace la
limite.

Au MRNF, la municipalité des Îles couvre 33 924 km², eaux du golfe
comprises; ses trois trous sont exactement les trois morceaux de
Grosse-Île (mêmes 5 714 sommets), dont le contour suit la rive.

Avec les limites actuelles d'OSM, 3 adresses sur 7 391 tombent du
mauvais côté :

- 127 chemin du Parc et 50 chemin du Quai : hors de toute municipalité
  (dans l'eau selon le littoral d'OSM);
- 998 chemin Principal, Grosse-Île : dans Les Îles-de-la-Madeleine.

### Remplacement proposé

- Les trois contours de Grosse-Île deviennent 5 chemins de limite neufs
  (5 714 nœuds à eux), membres des deux relations : `outer` pour
  Grosse-Île, `inner` pour Les Îles-de-la-Madeleine.
- Le contour extérieur des Îles, en mer, reprend les 7 chemins de la
  relation de la Communauté maritime (8405826) au lieu d'en tracer de
  nouveaux.
- 487 chemins sont retirés des relations, sans être modifiés : les 482
  du littoral et 5 autres. Deux simples lignes de limite devenues
  inutiles sont supprimées.
- Vérification : avec les limites proposées, les 7 391 adresses tombent
  dans la bonne municipalité.
- Lien avec le nœud de lieu : la relation des Îles-de-la-Madeleine a son
  membre `label`; celle de **Grosse-Île n'en a pas**, et OsmAnd
  n'utilisera pas sa limite tant que ce n'est pas réglé (à la main).

### Routes qui traversent les limites

Une route nommée doit être coupée là où elle traverse une limite, pour
que chaque côté garde son nom. Avec les limites proposées :

- la route 199 entre dans Grosse-Île à 47,57047 N, 61,49746 O; la coupure
  actuelle la plus proche est à 355 m : **coupure à déplacer**. Le
  chemin 1244695875 est coupé à ce point, et le nouveau segment est
  ajouté aux trois relations qui le contiennent (route 199, Route verte 1
  et une ligne d'autobus);
- le chemin de La Grave a une coupure au bord de l'ancienne limite (le
  littoral), entre deux segments aux étiquettes identiques : **coupure
  devenue inutile**. Elle n'est pas fusionnée, car la Route verte 1 ne
  suit qu'un des deux segments (les deux sont dans la relation de la
  route 199) : la fusion changerait le tracé de la Route verte.

L'ancienne coupure de la route 199 n'est pas sur l'ancienne limite
(elle est à 355 m) : elle est gardée.

### Questions en suspens

1. **Le contour en mer.** Celui de la Communauté maritime dans OSM
   s'écarte de celui du MRNF d'environ 15 km au nord et à l'ouest (aire
   de 37 378 km² dans OSM contre 33 902 au MRNF), mais concorde à
   quelques dizaines de mètres au sud et à l'est. Ce sont des limites
   interprovinciales en mer : on n'y touche pas pour l'instant. Faut-il
   les aligner sur le MRNF, et qui en décide?
2. **Le niveau des chemins créés** : `admin_level=8`, celui des
   municipalités. À confirmer.
3. **Les anciennes municipalités** (Cap-aux-Meules, L'Étang-du-Nord,
   Fatima) : niveau 9 ou 10? Les arrondissements de Montréal sont au
   niveau 10 dans OSM. Aucune source de tracé autorisée trouvée pour
   l'instant.

## 2. Rues

Détail : [rues.md](rues.md), carte : [rues.geojson](rues.geojson).
Rues du RQA comparées aux voies d'OSM autour de leurs adresses :

| Situation | Rues | Adresses |
|---|---|---|
| Conforme | 252 | 6 649 |
| À renommer (casse, accents, tirets) | 10 | 547 |
| Nom différent dans OSM | 3 | 49 |
| Voie sans nom dans OSM | 6 | 23 |
| Absente d'OSM | 1 | 1 |

- **Renommage proposé : 28 segments**, uniquement des différences de
  casse, d'accents ou d'espaces : « Chemin de L'Étang-du-Nord » devient
  « Chemin de l'Étang-du-Nord »; « Chemin de la Martinique », « Chemin de
  La Martinique »; « Chemin de la Grave », « Chemin de La Grave »;
  « Chemin le Pré », « Chemin Le Pré »; « Chemin Noel », « Chemin Noël »;
  etc. S'y ajoute le tronçon de Cap-aux-Meules du chemin du Gros-Cap,
  renommé « Chemin de Gros-Cap » (décision du sujet t/148723).

### Exceptions à valider

- **Nom différent** : « Chemin du Marconi » (officiel) contre « Chemin
  Marconi » et des voies de service sans nom; « Chemin de la Promenade »
  dont les adresses longent le « Chemin Cormier »; « Chemin Airport »
  contre « Chemin de l'Aéroport ».
- **Voies sans nom** le long des adresses : Allée Gérard-Noël, Allée
  Oscar-Nadeau, Chemin des Falaises, Allée de la Petite-École, Allée des
  Belles-Vues, Allée du Cap-de-l'Hôpital. Candidates pour recevoir le
  nom officiel.
- **Absente** : « Chemin Path », une seule adresse, aucune voie à moins
  de 60 m.

### Questions en suspens

1. **Le renommage par la casse** suit la Commission de toponymie
   (particule majuscule quand elle fait partie d'un nom propre : « de La
   Martinique », « Le Pré »). D'accord pour l'appliquer sans exception?
2. **Nommer les voies sans nom** d'après le RQA : par règle (une seule
   voie sans nom dessert toutes les adresses de la rue), ou à la main?
3. **« Chemin Airport »** : le RQA garde la forme anglaise, OSM a
   « Chemin de l'Aéroport ». Lequel suit l'usage local?
4. **« Chemin Seacow Path »** (RQA) contre « Chemin Sea Cow Path »
   (OSM) : renommé selon la règle, mais à confirmer localement.

## 3. Adresses

### Résumé

7 449 adresses retenues (7 144 aux Îles, 305 à Grosse-Île), une par
numéro de base. Les chiffres tiennent compte des renommages de rues
prévus (section 2) :

| Résultat | Nombre |
|---|---|
| Nouvelles, prêtes à créer | 7 218 |
| Déjà dans OSM, corrigées | 48 |
| Déjà dans OSM, inchangées | 35 |
| À revoir, non créées | 129 |
| Exclues : pas encore certifiées au RQA | 3 |

- Logements et suffixes fusionnés à leur numéro de base : 628 adresses
  en avaient. Les logements vont dans `addr:unit` (509 adresses), les
  suffixes en lettre dans `addr:housenumber` (156 adresses, par exemple
  « 19;19A;19B »). 17 suffixes placés ailleurs que leur numéro de base sont
  gardés comme adresses distinctes (310A et 310B chemin Principal,
  996A et 996B chemin de La Grave, etc.).
- 14 logements douteux écartés de `addr:unit` (sans lot ni matricule,
  sur une adresse d'un seul logement selon le rôle; voir
  [adresses.md](adresses.md#logements-douteux)). Contrairement à la
  Petite-Nation, ils viennent de plusieurs chargements du RQA.
- 55 numéros n'ont pas d'adresse principale au RQA, seulement des
  logements ou des suffixes : on prend le point d'un logement.
- Corrections d'adresses existantes : code postal ajouté, nom de rue
  corrigé, ou les deux. Rien d'autre n'est touché.
- 12 lignes d'interpolation CanVec supprimées, avec leurs 269 nœuds.
- Positions : toutes du RQA pour l'instant. Qualité des nouvelles
  adresses : surtout « Bâtiment » (environ 80 %), le reste
  « Incertaine », « Géocodée », « Centre lot » ou « Front lot ».

### Exceptions à valider

Les 129 adresses « à revoir » attendent que leur rue existe dans OSM
sous son nom officiel (détail dans [adresses.md](adresses.md#à-revoir)) :
surtout le chemin du Marconi (44), la route 199 (14 adresses à plus de
300 m de la route), et les allées et chemins sans nom de la section 2.

### Questions en suspens

1. **Route 199** : 14 adresses à plus de 300 m de la route. Longues
   entrées, ou points mal placés? Les portes d'entrée de Pierre-Léo
   Bourbonnais aideraient.
2. **Positions** : la Chaire Mobilité a placé des portes d'entrée à la
   main pour l'est du Québec. Si les Îles sont couvertes, l'outil peut
   les utiliser (section `[adresses.positions]`), avec repli sur le RQA.
3. **addr:city** : absent, en attendant les limites des anciennes
   municipalités. À vérifier avec Nominatim et Photon une fois les
   limites en place.

## 4. Prochaines étapes

1. Discussion publique du remplacement des limites, puis envoi.
2. Noms de rue.
3. Adresses, rue par rue ou d'un bloc selon l'avis de la communauté.
