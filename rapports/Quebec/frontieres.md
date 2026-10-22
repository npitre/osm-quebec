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
| OSM | en rivière | l'autre tracé | 5675 | 52 m | 209 m | 74 % | 30 % | 0 % |
| OSM | en rivière | l'axe de la rivière | 5675 | 44 m | 162 m | 76 % | 18 % | 2 % |
| OSM | ailleurs | l'autre tracé | 7433 | 65 m | 345 m | 79 % | 25 % | 4 % |

Distance aux rives non mesurée : la plupart des plans d'eau de la rivière ne portent pas son nom dans OSM (lacs, élargissements).

## Nouveau-Brunswick : Ristigouche et Patapédia

Chemins de la relation du Québec le long de cette frontière : limite seule 33, waterway=river 22, waterway=tidal_channel 9. Axe de la rivière dans OSM : 42 chemins `waterway=river`; rives : 223 chemins des polygones d'eau.

| Tracé | Partie | Distance à | Points | Médiane | 90 % à moins de | Plus de 20 m | Plus de 100 m | Plus de 1 km |
|---|---|---|---|---|---|---|---|---|
| MRNF | en rivière | l'autre tracé | 1887 | 11 m | 356 m | 30 % | 15 % | 0 % |
| MRNF | en rivière | l'axe de la rivière | 1887 | 13 m | 1,2 km | 36 % | 21 % | 11 % |
| MRNF | en rivière | la rive | 1887 | 32 m | 721 m | 68 % | 20 % | 9 % |
| MRNF | ailleurs | l'autre tracé | 2365 | 10 m | 36 m | 26 % | 1 % | 0 % |
| OSM | en rivière | l'autre tracé | 531 | 10 m | 37 m | 21 % | 6 % | 0 % |
| OSM | en rivière | l'axe de la rivière | 531 | 6 m | 886 m | 15 % | 12 % | 9 % |
| OSM | en rivière | la rive | 531 | 20 m | 181 m | 50 % | 11 % | 5 % |
| OSM | ailleurs | l'autre tracé | 2208 | 11 m | 40 m | 27 % | 3 % | 1 % |

## Ontario : ligne terrestre au nord du 48e parallèle

Ligne presque nord-sud, du lac Témiscamingue à la baie James : 697 sommets au MRNF. Écart est-ouest des nœuds d'OSM (positif : OSM plus à l'est).

| Latitude | Nœuds d'OSM | Écart médian |
|---|---|---|
| 48,0 | 53 | +12 m |
| 48,5 | 19 | +13 m |
| 49,0 | 7 | +45 m |
| 49,5 | 5 | +54 m |
| 50,0 | 5 | +69 m |
| 50,5 | 6 | +81 m |
| 51,0 | 21 | -1 m |
| 51,5 | 70 | -660 m |

## Ontario : tracé officiel de l'Ontario

Contour de la province selon l'Ontario (jeu « Province » de Géospatial Ontario, tenu par le bureau de l'arpenteur général, Licence du gouvernement ouvert de l'Ontario; précision annoncée : à 100 m près). Distances entre les sommets ou nœuds de chaque tracé et l'autre tracé, le long de la frontière Québec-Ontario.

| Tracé | Distance à | Points | Médiane | 90 % à moins de | Plus de 20 m | Plus de 100 m | Plus de 1 km |
|---|---|---|---|---|---|---|---|
| OSM | Ontario | 10096 | 0 m | 0 m | 4 % | 3 % | 3 % |
| Ontario | OSM | 11202 | 0 m | 29 m | 11 % | 5 % | 0 % |
| MRNF | Ontario | 12272 | 59 m | 195 m | 78 % | 25 % | 1 % |
| Ontario | MRNF | 11202 | 63 m | 216 m | 80 % | 29 % | 0 % |

Ligne terrestre au nord du 48e parallèle : écart est-ouest des sommets de l'Ontario par rapport au MRNF (positif : Ontario plus à l'est).

| Latitude | Sommets de l'Ontario | Écart médian |
|---|---|---|
| 48,0 | 59 | +8 m |
| 48,5 | 60 | +14 m |
| 49,0 | 60 | +46 m |
| 49,5 | 60 | +53 m |
| 50,0 | 60 | +69 m |
| 50,5 | 60 | +80 m |
| 51,0 | 92 | +85 m |
