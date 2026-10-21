# Limites municipales : Lac-Témoin (région fictive de test)

Données OSM : extrait lac-temoin.osm.pbf du 2026-10-16.

Source : Découpages administratifs du MRNF (1/20 000). Règles : voir le [README](../../README.md#régions). Carte : [regions.geojson](regions.geojson) (propriété `source` : MRNF ou OSM actuel). Commentaires : [README](README.md).

## Limites actuelles dans OSM

| Municipalité | Relation | Anneaux | Chemins qui la forment |
|---|---|---|---|
| Lac-Témoin | [1001](https://www.openstreetmap.org/relation/1001) | 1 | limite seule 2, waterway=river 1 |
| Sainte-Vérification | [1002](https://www.openstreetmap.org/relation/1002) | 1 | limite seule 2, waterway=river 1, autre 1 |

## Limites officielles (MRNF)

| Municipalité | Code | Version | Polygones | Trous | Sommets |
|---|---|---|---|---|---|
| Lac-Témoin | 99001 | V2026-09 | 1 | 0 | 5 |
| Sainte-Vérification | 99002 | V2026-09 | 1 | 0 | 7 |

## Adresses : municipalité selon chaque limite

| Limite | Bonne municipalité | Autre ou aucune |
|---|---|---|
| MRNF | 35 | 0 |
| OSM actuel | 34 | 1 |
| OSM après le remplacement proposé | 35 | 0 |

| Adresse | Municipalité (RQA) | Selon le MRNF | Selon OSM |
|---|---|---|---|
| 15 Rue Principale | 99001 | 99001 | 99002 |

## Remplacement proposé

| Élément | Nombre |
|---|---|
| Nœuds créés | 5 |
| Chemins de limite créés | 8 |
| Relations modifiées | 3 |
| Chemins retirés des relations | 7 |
| dont supprimés (simples lignes de limite inutilisées) | 3 |
| Nœuds supprimés | 4 |

- arc de 2 sommets (99001 outer, 99002 outer) : 1 chemin(s) neuf(s)
- arc de 2 sommets (99001 outer, 99003 outer) : 1 chemin(s) neuf(s)
- arc de 3 sommets (99001 outer) : 1 chemin(s) neuf(s)
- arc de 3 sommets (99002 outer) : 1 chemin(s) neuf(s), 1 chemin(s) existant(s) déjà conforme(s)
- arc de 3 sommets (99002 outer, 99003 outer) : 1 chemin(s) neuf(s)
- Rivière-Contrôle : 2 chemin(s) retiré(s), 2 raccord(s), 1 copie(s), 1 chemin(s) coupé(s)

Chemins supprimés : [101](https://www.openstreetmap.org/way/101), [105](https://www.openstreetmap.org/way/105), [120](https://www.openstreetmap.org/way/120).

Le littoral et les autres objets retirés des relations ne sont pas modifiés : seule leur appartenance aux limites change.

## Routes coupées

2 routes coupées, 2 nœuds de coupure ajoutés sur les routes, 2 morceaux neufs, 1 relations de route mises à jour.

- way 301 (Route 999) coupé en 2 morceaux
- way 310 (Rue Principale) coupé en 2 morceaux

### Coupures inutiles fusionnées

Sur une ancienne limite, deux segments d'une même route aux étiquettes et aux relations identiques sont réunis en un seul chemin.

- way 300 et way 301 (Route 999) fusionnés : way 301 supprimé
- way 332 et way 333 (Allée du Témoin) : fusion refusée, relations différentes
- way 320 et way 328 (Chemin du Lac) fusionnés : way 328 supprimé

## Chemins protégés

Ces chemins portent une note, un fixme, une description ou une étiquette disputed* : ils sont retirés des relations mais jamais supprimés automatiquement. À traiter à la main.

| Chemin | Étiquettes | Note reportée sur |
|---|---|---|
| [104](https://www.openstreetmap.org/way/104) | note=Limite à vérifier sur le terrain | chemin neuf -4 |

## Lien avec le nœud de lieu

OsmAnd n'utilise une limite que si sa relation a un membre label ou admin_centre vers un nœud place portant exactement le même nom. Les membres existants sont gardés; les cas à régler sont signalés.

| Municipalité | Statut | Détail |
|---|---|---|
| Lac-Témoin | lié | label : node 11 place=village |
| Sainte-Vérification | sans lien | aucun membre label ni admin_centre |

## Routes qui traversent les limites

Une route nommée est coupée exactement là où elle traverse une limite municipale (à moins de 25 m), même si ses étiquettes sont identiques des deux côtés : Nominatim et Photon rattachent chaque segment de rue à une seule municipalité. Les coupures « à ajouter » et « à déplacer » sont faites dans le fichier d'envoi; une coupure « devenue inutile », et l'ancienne coupure d'une coupure déplacée, sont fusionnées quand c'est possible (voir plus haut).

| Situation | Nombre |
|---|---|
| déjà coupée | 0 |
| coupure à déplacer | 1 |
| coupure à ajouter | 1 |
| coupure devenue inutile | 2 |

| Situation | Rue | Chemin | Position | Écart |
|---|---|---|---|---|
| coupure devenue inutile | Allée du Témoin | [332](https://www.openstreetmap.org/way/332) | 47.01700, -71.99550 | 0 m |
| coupure devenue inutile | Chemin du Lac | [320](https://www.openstreetmap.org/way/320) | 47.01700, -71.99700 | 0 m |
| coupure à ajouter | Rue Principale | [310](https://www.openstreetmap.org/way/310) | 47.01500, -71.98000 |  |
| coupure à déplacer | Route 999 | [300](https://www.openstreetmap.org/way/300) | 47.00800, -71.98000 | 76 m |
