# Adresses : Lac-Témoin (région fictive de test)

Données OSM : extrait lac-temoin.osm.pbf du 2026-10-16.

Source : Référentiel québécois des adresses (MRNF), version AQ20261001. Règles : voir le [README](../../README.md#adresses). Carte : [adresses.geojson](adresses.geojson). Commentaires : [README](README.md).

## Résumé

| Résultat | Nombre |
|---|---|
| Nouvelles adresses | 29 |
| Déjà dans OSM, corrigées | 1 |
| Déjà dans OSM, inchangées | 2 |
| À revoir (non créées) | 6 |
| Exclues | 1 |
| Logements douteux écartés | 1 |
| Objets OSM modifiés | 1 |
| Lignes d'interpolation supprimées | 1 |
| Nœuds d'interpolation supprimés | 2 |

Source des positions : RQA 36, portes 3.

## À revoir

Ces adresses ne sont pas créées tant que la rue n'est pas réglée dans OSM.

### Rue absente ou sans nom dans OSM (5 adresses)

| Nom officiel (RQA) | Adresses |
|---|---|
| Allée des Bouleaux | 2 |
| Chemin des Érables | 2 |
| Chemin Fantôme | 1 |

### Autre (1 adresses)

| Rue | Détail | Adresses |
|---|---|---|
| Chemin du Lac | interpolation 404 gardée : nœuds partagés ou étiquettes inattendues | 1 |

## Logements douteux

Logements du RQA sans lot ni matricule, sur une adresse qui n'a qu'un logement selon le rôle d'évaluation : ils ne sont pas mis dans addr:unit. Liste à signaler au MRNF (géoboutique). Voir le [README](../../README.md#logements-douteux-du-rqa).

| Municipalité | Adresse | Créé le | Identifiant RQA |
|---|---|---|---|
| Lac-Témoin | 9999-260 Chemin du Lac | 2021-12-11 | 000000000000000000000000007e000d |

## Objets OSM modifiés

| Objet | Changements | Raison |
|---|---|---|
| [node/32](https://www.openstreetmap.org/node/32) | addr:street=Chemin du Lac, addr:postcode=J0T 1A0 | adresse 30 Chemin du Lac : addr:street=Chemin du Lac, addr:postcode=J0T 1A0 |

## Lignes d'interpolation supprimées

[400](https://www.openstreetmap.org/way/400)
