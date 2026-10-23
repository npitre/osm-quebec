# Limites municipales : Les Îles-de-la-Madeleine

Données OSM : extrait quebec-latest.osm.pbf du 2026-10-16.

Source : Découpages administratifs du MRNF (1/20 000). Règles : voir le [README](../../README.md#régions). Carte : [regions.geojson](regions.geojson) (propriété `source` : MRNF ou OSM actuel). Commentaires : [README](README.md).

## Limites actuelles dans OSM

| Municipalité | Relation | Anneaux | Chemins qui la forment |
|---|---|---|---|
| Les Îles-de-la-Madeleine | [8402197](https://www.openstreetmap.org/relation/8402197) | 5 | natural=coastline 417, limite seule 5 |
| Grosse-Île | [8402196](https://www.openstreetmap.org/relation/8402196) | 3 | natural=coastline 65, limite seule 2 |

## Limites officielles (MRNF)

| Municipalité | Code | Version | Polygones | Trous | Sommets |
|---|---|---|---|---|---|
| Les Îles-de-la-Madeleine | 01023 | V2026-09 | 1 | 3 | 5759 |
| Grosse-Île | 01042 | V2026-09 | 3 | 0 | 5717 |

## Adresses : municipalité selon chaque limite

| Limite | Bonne municipalité | Autre ou aucune |
|---|---|---|
| MRNF | 7391 | 0 |
| OSM actuel | 7388 | 3 |
| OSM après le remplacement proposé | 7391 | 0 |

| Adresse | Municipalité (RQA) | Selon le MRNF | Selon OSM |
|---|---|---|---|
| 127 Chemin du Parc | 01023 | 01023 | aucune |
| 50 Chemin du Quai | 01023 | 01023 | aucune |
| 998 Chemin Principal | 01042 | 01042 | 01023 |

## Remplacement proposé

| Élément | Nombre |
|---|---|
| Nœuds créés | 5714 |
| Chemins de limite créés | 5 |
| Relations modifiées | 2 |
| Chemins retirés des relations | 487 |
| dont supprimés (simples lignes de limite inutilisées) | 2 |
| Nœuds supprimés | 1 |

- arc de 22 sommets (01023 inner, 01042 outer) : 1 chemin(s) neuf(s)
- arc de 5628 sommets (01023 inner, 01042 outer) : 3 chemin(s) neuf(s)
- arc de 67 sommets (01023 inner, 01042 outer) : 1 chemin(s) neuf(s)
- anneau extérieur de 42 sommets (01023) : 7 chemins de la relation 8405826 réutilisés

Chemins supprimés : [600699235](https://www.openstreetmap.org/way/600699235), [600699240](https://www.openstreetmap.org/way/600699240).

Le littoral et les autres objets retirés des relations ne sont pas modifiés : seule leur appartenance aux limites change.

## Routes coupées

1 routes coupées, 1 nœuds de coupure ajoutés sur les routes, 1 morceaux neufs, 3 relations de route mises à jour.

- way 1244695875 (Route 199) coupé en 2 morceaux

### Coupures inutiles fusionnées

Sur une ancienne limite, deux segments d'une même route aux étiquettes et aux relations identiques sont réunis en un seul chemin.

- way 1217383411 et way 1243689797 (Chemin de la Grave) : fusion refusée, relations différentes

## Lien avec le nœud de lieu

OsmAnd n'utilise une limite que si sa relation a un membre label ou admin_centre vers un nœud place portant exactement le même nom. Les membres existants sont gardés; les cas à régler sont signalés.

| Municipalité | Statut | Détail |
|---|---|---|
| Les Îles-de-la-Madeleine | lié | label : node 10753351413 place=town |
| Grosse-Île | sans lien | aucun membre label ni admin_centre |

## Routes qui traversent les limites

Une route nommée est coupée exactement là où elle traverse une limite municipale (à moins de 25 m), même si ses étiquettes sont identiques des deux côtés : Nominatim et Photon rattachent chaque segment de rue à une seule municipalité. Les coupures « à ajouter » et « à déplacer » sont faites dans le fichier d'envoi; une coupure « devenue inutile », et l'ancienne coupure d'une coupure déplacée, sont fusionnées quand c'est possible (voir plus haut).

| Situation | Nombre |
|---|---|
| déjà coupée | 1 |
| coupure à déplacer | 1 |
| coupure à ajouter | 0 |
| coupure devenue inutile | 1 |

| Situation | Rue | Chemin | Position | Écart |
|---|---|---|---|---|
| coupure devenue inutile | Chemin de la Grave | [1217383411](https://www.openstreetmap.org/way/1217383411) | 47.23693, -61.82790 | 13 m |
| coupure à déplacer | Route 199 | [27708492](https://www.openstreetmap.org/way/27708492) | 47.57047, -61.49746 | 355 m |
