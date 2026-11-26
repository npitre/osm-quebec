# Limites municipales : L'Île-d'Anticosti

Données OSM : extrait quebec-latest.osm.pbf du 2026-11-24.

Source : Découpages administratifs du MRNF (1/20 000). Règles : voir le [README](../../README.md#régions). Carte : [regions.geojson](regions.geojson) (propriété `source` : MRNF ou OSM actuel). Commentaires : [README](README.md).

## Limites actuelles dans OSM

| Municipalité | Relation | Anneaux | Chemins qui la forment |
|---|---|---|---|
| L'Île-d'Anticosti | [7734508](https://www.openstreetmap.org/relation/7734508) | 1 | limite seule 17 |

## Limites officielles (MRNF)

| Municipalité | Code | Version | Polygones | Trous | Sommets |
|---|---|---|---|---|---|
| L'Île-d'Anticosti | 98020 | V2026-09 | 1 | 0 | 32 |

## Adresses : municipalité selon chaque limite

| Limite | Bonne municipalité | Autre ou aucune |
|---|---|---|
| MRNF | 201 | 0 |
| OSM actuel | 201 | 0 |
| OSM après le remplacement proposé | 201 | 0 |

## Remplacement proposé

| Élément | Nombre |
|---|---|
| Nœuds créés | 30 |
| Chemins de limite créés | 1 |
| Relations modifiées | 1 |
| Chemins retirés des relations | 17 |
| dont supprimés (simples lignes de limite inutilisées) | 11 |
| Nœuds supprimés | 26 |

- arc de 32 sommets (98020 outer) : 1 chemin(s) neuf(s)

Chemins supprimés : [541770099](https://www.openstreetmap.org/way/541770099), [776297543](https://www.openstreetmap.org/way/776297543), [776298128](https://www.openstreetmap.org/way/776298128), [802076517](https://www.openstreetmap.org/way/802076517), [802076518](https://www.openstreetmap.org/way/802076518), [802076519](https://www.openstreetmap.org/way/802076519), [802076520](https://www.openstreetmap.org/way/802076520), [802076521](https://www.openstreetmap.org/way/802076521), [802076524](https://www.openstreetmap.org/way/802076524), [802076526](https://www.openstreetmap.org/way/802076526), [802076527](https://www.openstreetmap.org/way/802076527).

Le littoral et les autres objets retirés des relations ne sont pas modifiés : seule leur appartenance aux limites change.

## Routes coupées

0 routes coupées, 0 nœuds de coupure ajoutés sur les routes, 0 morceaux neufs, 0 relations de route mises à jour.



## Lien avec le nœud de lieu

OsmAnd n'utilise une limite que si sa relation a un membre label ou admin_centre vers un nœud place portant exactement le même nom. Les membres existants sont gardés; les cas à régler sont signalés.

| Municipalité | Statut | Détail |
|---|---|---|
| L'Île-d'Anticosti | sans lien | aucun membre label ni admin_centre |

## Routes qui traversent les limites

Une route nommée est coupée exactement là où elle traverse une limite municipale (à 5 cm près, la précision des coordonnées d'OSM), même si ses étiquettes sont identiques des deux côtés : Nominatim et Photon rattachent chaque segment de rue à une seule municipalité. Les coupures « à ajouter » et « à déplacer » sont faites dans le fichier d'envoi; une coupure « devenue inutile », et l'ancienne coupure d'une coupure déplacée, sont fusionnées quand c'est possible (voir plus haut). Une « voie à cheval », qui croise la limite à moins de 200 m d'un autre de ses croisements, la longe plutôt que de la traverser : elle n'est pas coupée, à revoir à la main.

| Situation | Nombre |
|---|---|
| déjà coupée | 0 |
| coupure à déplacer | 0 |
| coupure à ajouter | 0 |
| coupure devenue inutile | 0 |
| voie à cheval | 0 |
