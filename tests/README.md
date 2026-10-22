# Tests

Depuis la racine du dépôt :

```
python3 -m unittest discover tests
```

Aucun test n'a besoin de données téléchargées ni d'accès réseau.

## Une règle, un test

`tests/test_readme.py` vérifie les règles sur de petits exemples
construits à la main, au moins un par règle du
[README](../README.md#règles-appliquées), nommé d'après elle :

| Règle | Tests |
|---|---|
| Ordre des étapes, 2 | `test_rues_4_adresses_apres_renommage`, `test_adresses_4_rue_dans_osm` |
| Régions, 1 à 12 | `test_regions_1_trace_du_mrnf` à `test_regions_12_mrc_et_region` (règle 12 : aussi `test_mrc_et_region`, dans Lac-Témoin) (règle 5 : suppression, chemins protégés, report de la note, étiquettes des relations; règle 7 : nœud ajouté au croisement, chemin coupé, relation de route mise à jour) |
| Rues, 1 à 4 | `test_rues_1_nom_officiel` (dont les abréviations) à `test_rues_4_adresses_apres_renommage` (règle 2 : `old_name` et `alt_name`) |
| Adresses, 1 à 8 | `test_adresses_1_logements_et_suffixes` à `test_adresses_8_positions_et_entree` |
| Groupe de modifications | `test_groupe` (`import=yes`, discussion obligatoire pour un envoi réel) |

## Lac-Témoin, région fictive de bout en bout

`tests/test_lac_temoin.py` lance les vraies commandes (`adresses
extraire`, `adresses osm`, `regions preparer`, `rues preparer`,
`adresses preparer`) sur Lac-Témoin, une région inventée : trois
municipalités, Lac-Témoin, Sainte-Vérification et Rivière-Contrôle, dans
une MRC du Témoin tout aussi fictive. Ses données sources (extrait du RQA,
découpages du MRNF, extrait d'OSM, portes de la Chaire Mobilité) sont
fabriquées par `tests/lac_temoin/fabriquer.py`, qui décrit chaque cas :
une limite faite d'une rivière, un chemin de limite avec une note, une
frontière, une route à couper avec sa relation, une relation sans nœud
de lieu, des rues à renommer (casse, tirets, « St. »), des rues
absentes ou sans nom, des doublons, des interpolations, des logements
et des suffixes, un logement douteux, des portes, un bout de limite
qui suit déjà le MRNF, deux sommets du MRNF confondus, et une voisine
hors du lot (Rivière-Contrôle) dont l'ancienne limite double celle du
lot, faite en partie d'un ruisseau et d'un chemin partagé avec une aire
protégée, et une ancienne limite en bosse où deux routes ont gardé une
coupure (l'une fusionnée, l'autre non : un sentier de motoneige ne suit
qu'un de ses deux segments). Au sud, la frontière du Québec avec une
province voisine, 55 m plus au sud dans OSM qu'au MRNF : gardée, et
coupée là où la limite commune la rejoint. La MRC et la région du
Témoin partagent un ancien contour tracé à part : le premier lot les
raccorde à ses arcs, le second les fait suivre le MRNF. Le tout tourne
en mode hors ligne.

Le test enchaîne aussi deux lots, comme on enverra une région par
bouchées : le premier (Lac-Témoin et Sainte-Vérification, fichier
`tests/lac_temoin/Lac-Temoin.toml`) modifie Rivière-Contrôle en partie;
son envoi est simulé (`extrait.appliquer` applique le fichier d'envoi à
l'extrait, comme si OSM l'avait accepté); le second lot
(`Riviere-Controle.toml`) traite Rivière-Contrôle, et son envoi est
simulé à son tour. Après chaque envoi, toutes les relations de limite
doivent former des anneaux fermés, sans chemin de limite créé
orphelin; à la fin, raccords et copies ont
disparu, la réserve est restée entière, et relancer les deux lots ne
produit plus rien.

Deux vérifications :

- des attentes écrites cas par cas, nommées d'après les règles
  (`test_regions_7_coupures`, `test_adresses_8_positions_et_entree`,
  etc.);
- une sortie de référence, `tests/lac_temoin/attendu/` : les fichiers
  d'envoi et les rapports. Toute différence fait échouer le test. Après
  un changement voulu, on régénère la référence et on relit le diff de
  git, qui montre exactement ce qui change dans la sortie :

```
OSMQC_REGENERER=1 python3 -m unittest tests.test_lac_temoin
git diff tests/lac_temoin/attendu
```

Pour ajouter un cas : le décrire dans `fabriquer.py`, ajouter son
attente dans `test_lac_temoin.py`, puis régénérer la référence.

## Fonctions de base

`tests/test_regles.py` et `tests/test_rues_coupures.py` vérifient plus
en détail les fonctions de base :

| Groupe | Ce qui est vérifié |
|---|---|
| Géométrie | distances; point dans un polygone avec trou; assemblage de segments en anneaux fermés |
| Noms de rue | nom tiré de la forme recomposée du RQA, sans le discriminant (« Chemin du Gros-Cap »), dans l'ordre usuel (« 4e Rang Sud »); recomposition à partir des parties (« Rue d'Amiens », « Rue Sherbrooke Est »); comparaison insensible à la casse, aux accents et aux tirets |
| Regroupement des adresses | logements fusionnés au numéro de base; suffixe au même point fusionné; suffixe ailleurs gardé comme adresse distincte (120A); suffixes sans numéro de base (« 300A;300B », sans « 300 »); numéro sans adresse principale |
| Doublons | adresse OSM au même numéro à moins de 30 m, ou bâtiment qui contient le point, reconnue; numéro différent ou trop loin, non reconnue |
| Limites | trou d'une municipalité occupé par une autre : un seul arc, intérieur pour l'une et extérieur pour l'autre; deux municipalités voisines : un arc commun et un arc propre à chacune |
| Rues | nom identique déclaré conforme; différence de casse renommée sur toute la rue, segments reliés compris; tirets et accents (« Tour du Lac » devient « Tour-du-Lac »); autre nom signalé sans être renommé; voie sans nom proposée comme candidate; rue absente; chemin réclamé par deux noms officiels mis en conflit |
| Coupures de routes | coupure déjà sur la limite; coupure à ajouter; coupure à déplacer; cul-de-sac au bord de l'ancienne limite ignoré; coupure devenue inutile entre deux segments identiques; coupure qui sert à autre chose (un pont) ignorée |

Ils ne remplacent pas la révision des rapports : les vérifications sur
les données réelles (municipalité de chaque adresse avant et après le
remplacement des limites, entre autres) sont dans les rapports de
chaque lieu.
