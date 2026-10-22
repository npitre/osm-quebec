# Frontières du Québec : MRNF et OSM

Comparaison des frontières du Québec selon les Découpages administratifs du MRNF (table `regio_l`) et de la relation du Québec dans OSM ([61549](https://www.openstreetmap.org/relation/61549)), extrait de Geofabrik du 2026-10-16. Un point tous les 200 m le long de chaque frontière du MRNF; écart : distance au tracé d'OSM le plus proche. Produit par `outils/frontieres.py`. Commentaires : [README](README.md).

| Frontière | Code | Points | Écart médian | 90 % à moins de | Plus de 20 m | Plus de 100 m | Plus de 1 km |
|---|---|---|---|---|---|---|---|
| États-Unis | `FROINT` | 7385 | 0 m | 1 m | 0 % | 0 % | 0 % |
| Nouveau-Brunswick | `FRONB` | 4252 | 11 m | 46 m | 28 % | 7 % | 0 % |
| Ontario | `FROONT` | 12272 | 58 m | 193 m | 77 % | 25 % | 0 % |
| Labrador, le long du 52e parallèle | `FRO52` | 10078 | 14 m | 80 m | 40 % | 9 % | 7 % |
| Labrador, ligne de partage des eaux | `FROTN` | 66359 | 232 m | plus de 5 km | 92 % | 70 % | 23 % |
| Nunavut (baies d'Hudson et d'Ungava, détroit d'Hudson) | `FRONT` | 52584 | 189 m | 3,5 km | 75 % | 59 % | 26 % |
| Golfe du Saint-Laurent (limites en mer) | `FROGSL` | 5027 | 44 m | 5,2 km | 63 % | 40 % | 27 % |

Chemins de la relation du Québec : natural=coastline 820, limite seule 450, waterway=river 79, waterway=tidal_channel 9. Avec une étiquette `disputed*`, `note`, `fixme` ou `description` : 0.

## Ontario : rivière des Outaouais

Chemins de la relation du Québec le long de cette frontière : limite seule 104, waterway=river 57, natural=coastline 2. Axe de la rivière dans OSM : 163 chemins `waterway=river`; rives : 31 chemins des polygones d'eau.

| Tracé | Partie | Distance à | Points | Médiane | 90 % à moins de | Plus de 20 m | Plus de 100 m | Plus de 1 km |
|---|---|---|---|---|---|---|---|---|
| MRNF | en rivière | l'autre tracé | 9095 | 62 m | 212 m | 80 % | 30 % | 0 % |
| MRNF | en rivière | l'axe de la rivière | 9095 | 76 m | 300 m | 83 % | 39 % | 1 % |
| MRNF | ailleurs | l'autre tracé | 3177 | 51 m | 104 m | 68 % | 11 % | 0 % |
| OSM | en rivière | l'autre tracé | 9276 | 63 m | 225 m | 80 % | 30 % | 0 % |
| OSM | en rivière | l'axe de la rivière | 9276 | 14 m | 106 m | 46 % | 11 % | 1 % |
| OSM | ailleurs | l'autre tracé | 3832 | 53 m | 461 m | 70 % | 20 % | 7 % |

Distance aux rives non mesurée : la plupart des plans d'eau de la rivière ne portent pas son nom dans OSM (lacs, élargissements).

## Nouveau-Brunswick : Ristigouche et Patapédia

Chemins de la relation du Québec le long de cette frontière : limite seule 33, waterway=river 22, waterway=tidal_channel 9. Axe de la rivière dans OSM : 42 chemins `waterway=river`; rives : 223 chemins des polygones d'eau.

| Tracé | Partie | Distance à | Points | Médiane | 90 % à moins de | Plus de 20 m | Plus de 100 m | Plus de 1 km |
|---|---|---|---|---|---|---|---|---|
| MRNF | en rivière | l'autre tracé | 1887 | 11 m | 356 m | 30 % | 15 % | 0 % |
| MRNF | en rivière | l'axe de la rivière | 1887 | 13 m | 1,2 km | 36 % | 21 % | 11 % |
| MRNF | en rivière | la rive | 1887 | 32 m | 721 m | 68 % | 20 % | 9 % |
| MRNF | ailleurs | l'autre tracé | 2365 | 10 m | 36 m | 26 % | 1 % | 0 % |
| OSM | en rivière | l'autre tracé | 1122 | 9 m | 29 m | 20 % | 4 % | 0 % |
| OSM | en rivière | l'axe de la rivière | 1122 | 0 m | 14 m | 7 % | 6 % | 4 % |
| OSM | en rivière | la rive | 1122 | 30 m | 76 m | 72 % | 6 % | 2 % |
| OSM | ailleurs | l'autre tracé | 1617 | 13 m | 43 m | 30 % | 4 % | 2 % |

## Ontario : ligne terrestre du lac Témiscamingue à la baie James

La frontière y suit le méridien 79°31' O, borné sur le terrain. Écart de chaque tracé au méridien mathématique (positif : à l'est), médiane des sommets ou nœuds par demi-degré de latitude.

| Latitude | MRNF | Ontario | OSM |
|---|---|---|---|
| 48,0 | -72 m (143) | -65 m (60) | -63 m (53) |
| 48,5 | -68 m (120) | -53 m (60) | -55 m (19) |
| 49,0 | -87 m (122) | -40 m (60) | -42 m (7) |
| 49,5 | -80 m (103) | -27 m (60) | -25 m (5) |
| 50,0 | -79 m (75) | -11 m (60) | -10 m (5) |
| 50,5 | -78 m (67) | +1 m (60) | +3 m (6) |
| 51,0 | -78 m (65) | +8 m (91) | -78 m (21) |
| 51,5 | -127 m (2) |  | -780 m (70) |

## Ontario : tracé officiel de l'Ontario

Contour de la province selon l'Ontario (jeu « Province » de Géospatial Ontario, tenu par le bureau de l'arpenteur général, Licence du gouvernement ouvert de l'Ontario; précision annoncée : à 100 m près). Distances entre les sommets ou nœuds de chaque tracé et l'autre tracé, le long de la frontière Québec-Ontario.

| Tracé | Distance à | Points | Médiane | 90 % à moins de | Plus de 20 m | Plus de 100 m | Plus de 1 km |
|---|---|---|---|---|---|---|---|
| OSM | Ontario | 10096 | 0 m | 0 m | 4 % | 3 % | 3 % |
| Ontario | OSM | 11202 | 0 m | 29 m | 11 % | 5 % | 0 % |
| MRNF | Ontario | 12272 | 59 m | 195 m | 78 % | 25 % | 1 % |
| Ontario | MRNF | 11202 | 63 m | 216 m | 80 % | 29 % | 0 % |
