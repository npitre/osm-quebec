# Laval : commentaires

Demandée par Pierre-Léo Bourbonnais, qui y testera l'import des
adresses. Laval seule (65005), sans le reste de la bouchée 94 : ses
voisines sont modifiées en partie.

**Version préliminaire, pour examen.** Préparée avec les Découpages
administratifs V2026-09 et l'extrait OSM de Geofabrik du 24 novembre
2026. Elle sera refaite avec la version de novembre des Découpages
avant l'envoi.

Rapport : [régions](regions.md), avec sa carte ([regions.geojson](regions.geojson) :
en bleu le tracé du MRNF, en rouge la limite actuelle d'OSM).
Configuration : [lieux/Laval.toml](../../lieux/Laval.toml).

Fichier d'envoi : [regions.osc](regions.osc) (osmChange, 1 573 objets,
un seul groupe de modifications); les objets créés y ont des
identifiants négatifs. Validé par `outils/valider.py` : toutes les
relations touchées restent des anneaux fermés, aucun orphelin, et une
nouvelle préparation après l'envoi ne produit plus rien.

## Constat

Le contour actuel de Laval est fait à 90 % de l'axe des rivières (33
chemins `waterway=river`). Le tracé du MRNF est à moins de 24 m de
l'ancien sur la moitié des 84 km du contour, à plus de 100 m sur 11 %;
les grands écarts (jusqu'à 1 km) sont autour d'îles attribuées
autrement, dans la rivière des Mille Îles et le lac des Deux Montagnes.
Deux adresses du RQA (1 et 44 Île aux Vaches) ne tombent aujourd'hui
dans aucune municipalité; avec le tracé du MRNF, toutes les 135 691
adresses de Laval sont dans Laval.

## Ce que contient l'envoi

- le contour de Laval selon le MRNF, sur des chemins de limite
  distincts des rivières;
- ses voisines (Montréal, Terrebonne, Saint-Eustache, Deux-Montagnes,
  Boisbriand, Rosemère, Lorraine, Bois-des-Filion), leurs MRC et leurs
  régions, modifiées en partie avec des raccords provisoires;
- les 12 secteurs de Laval (anciennes villes) qui touchent le contour,
  et 6 arrondissements de Montréal le long de la rivière des Prairies :
  leur bord extérieur suit le nouveau contour, avec un court raccord
  (5 à 76 m) vers chaque limite intérieure (règle 13 des régions);
- 5 routes coupées exactement sur la limite, et leurs relations (routes
  numérotées, lignes d'autobus).
