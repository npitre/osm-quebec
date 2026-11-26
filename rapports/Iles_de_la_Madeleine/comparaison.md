# Adresses : Les Îles-de-la-Madeleine, comparaison avec OSM

Données OSM : extrait du 2026-11-24. Source : Référentiel québécois des adresses (MRNF), version AQ20261001.

Comparaison faite selon la [méthode de validation des noms de rues et des adresses](https://wiki.openstreetmap.org/wiki/FR:Qu%C3%A9bec/Validation_des_noms_de_rues_et_des_adresses) et les [règles d'osmqc](../../README.md#adresses). Une adresse du RQA est retrouvée dans OSM par un objet au même numéro à moins de 30 m, ou par le bâtiment ou le terrain qui contient son point, ou au même numéro sur la même rue à moins de 300 m. Un objet à plusieurs numéros (`47;49`) est retrouvé par chacun. Rien n'est envoyé : ce rapport sert à repérer les différences. Carte de toutes les lignes : [comparaison.geojson](comparaison.geojson).

## Résumé

| Résultat | Nombre |
|---|---|
| Adresses du RQA (après regroupement des logements) | 7433 |
| Retrouvées dans OSM | 7026 |
| Retrouvées, nom de rue différent dans OSM | 7 |
| Retrouvées, logements différents | 45 |
| Absentes d'OSM, rue présente | 352 |
| Absentes d'OSM, rue introuvable sous ce nom | 52 |
| Non certifiées au RQA (ignorées) | 3 |
| Adresses d'OSM sans pendant au RQA | 243 |

## Questions

### addr:city

Pour les 7026 adresses retrouvées, comparaison de `addr:city` dans OSM avec ce que donne la méthode du wiki (le discriminant de la rue au RQA, sinon le nom de la municipalité) : 1876 pareilles, 5146 différentes, 4 sans `addr:city`.

| Selon le RQA | Dans OSM | Adresses |
|---|---|---|
| Les Îles-de-la-Madeleine | L'Étang-du-Nord | 1280 |
| Les Îles-de-la-Madeleine | Fatima | 1184 |
| Les Îles-de-la-Madeleine | Bassin | 719 |
| Les Îles-de-la-Madeleine | Havre-aux-Maisons | 711 |
| Les Îles-de-la-Madeleine | Cap-aux-Meules | 568 |
| Les Îles-de-la-Madeleine | Havre-Aubert | 366 |
| Les Îles-de-la-Madeleine | L'Île-d'Entrée | 94 |
| Les Îles-de-la-Madeleine | Grande-Entrée | 83 |
| Havre-aux-Maisons | Pointe-aux-Loups | 64 |
| Les Îles-de-la-Madeleine | Pointe-aux-Loups | 41 |
| Havre-Aubert | Bassin | 32 |
| Les Îles-de-la-Madeleine | Havre-aux-maisons | 1 |
| L'Étang-du-Nord | Cap-aux-Meules | 1 |
| Les Îles-de-la-Madeleine | L'Île-du-Havre-Aubert | 1 |
| L'Étang-du-Nord | l'Étang-du-Nord | 1 |

Le RQA ne donne de discriminant qu'aux rues dont le nom se répète dans la municipalité. D'où viennent les localités inscrites dans OSM? Si elles sont voulues, la page du wiki serait à préciser, et osmqc à ajuster.

### addr:postcode

329 des 7026 adresses retrouvées ont un `addr:postcode` dans OSM (8 différent du RQA). Le RQA donne un code postal pour chaque adresse, sous sa propre licence. Est-ce voulu de ne pas l'ajouter?

## Retrouvées, nom de rue différent dans OSM (7)

| Objet | Dans OSM | Nom officiel (RQA) | Numéro |
|---|---|---|---|
| [node/6177291491](https://www.openstreetmap.org/node/6177291491) | Chemin de la Pointe Basse | Chemin de la Pointe-Basse | 149 |
| [node/6177291785](https://www.openstreetmap.org/node/6177291785) | Chemin de la Dune du Sud | Chemin de la Dune-du-Sud | 430 |
| [node/6881247785](https://www.openstreetmap.org/node/6881247785) | Chemin de la Grande Allée | Chemin de la Grande-Allée | 225 |
| [node/11036037805](https://www.openstreetmap.org/node/11036037805) | Chemin de la Dune du Sud | Chemin de la Dune-du-Sud | 436 |
| [node/11073936341](https://www.openstreetmap.org/node/11073936341) | chemin John Aucoin | Chemin John-Aucoin | 115 |
| [node/11073936595](https://www.openstreetmap.org/node/11073936595) | Chemin du Grand Ruisseau | Chemin du Grand-Ruisseau | 984 |
| [node/11161788088](https://www.openstreetmap.org/node/11161788088) | Chemin du Gros Cap | Chemin du Gros-Cap | 547 |

## Retrouvées, logements différents (45)

Logements selon le RQA (sans les logements douteux : ni lot ni matricule, sur une adresse que le rôle d'évaluation dit à un seul logement) et dans OSM (`addr:flats`, sinon `addr:unit`).

| Adresse | Objet | RQA | OSM | Écart |
|---|---|---|---|---|
| 10 Allée Hormidas-Cyr | [node/14374962692](https://www.openstreetmap.org/node/14374962692) |  | ;2 | 1 de plus dans OSM |
| 75 Allée Robert-Vigneau | [node/14391904564](https://www.openstreetmap.org/node/14391904564) |  | ;1 | 1 de plus dans OSM |
| 342 Chemin Arsenault | [node/14374961364](https://www.openstreetmap.org/node/14374961364) |  | ;2 | 1 de plus dans OSM |
| 499 Chemin Boisville Ouest | [node/6534386765](https://www.openstreetmap.org/node/6534386765) | ;2 |  | 1 de plus au RQA |
| 260 Chemin Boudreau | [node/14384409273](https://www.openstreetmap.org/node/14384409273) | ;2 |  | 1 de plus au RQA |
| 26 Chemin Garneau | [node/14374960933](https://www.openstreetmap.org/node/14374960933) |  | ;1 | 1 de plus dans OSM |
| 6 Chemin Jerry | [node/9376922277](https://www.openstreetmap.org/node/9376922277) | ;1;2A;3;5 |  | 4 de plus au RQA |
| 25 Chemin Noël | [node/14381000195](https://www.openstreetmap.org/node/14381000195) |  | ;1 | 1 de plus dans OSM |
| 38 Chemin Park | [node/14356684350](https://www.openstreetmap.org/node/14356684350) | ;1;3 | 1 | 1 de plus au RQA |
| 40 Chemin Principal | [node/11188939739](https://www.openstreetmap.org/node/11188939739) | ;1 |  | 1 de plus au RQA |
| 205 Chemin Principal | [node/11190959782](https://www.openstreetmap.org/node/11190959782) | ;109;126 |  | 2 de plus au RQA |
| 221 Chemin Principal | [node/9385891761](https://www.openstreetmap.org/node/9385891761) | ;1;2;4 |  | 3 de plus au RQA |
| 246 Chemin Principal | [node/14355484268](https://www.openstreetmap.org/node/14355484268) | ;1-4;6 |  | 5 de plus au RQA |
| 248 Chemin Principal | [node/11203418477](https://www.openstreetmap.org/node/11203418477) | ;2 |  | 1 de plus au RQA |
| 280 Chemin Principal | [node/11203418105](https://www.openstreetmap.org/node/11203418105) | ;5;9-12 |  | 5 de plus au RQA |
| 380 Chemin Principal | [node/5512813858](https://www.openstreetmap.org/node/5512813858) | ;201 | 200 | 1 de plus au RQA, 1 de plus dans OSM |
| 425 Chemin Principal | [node/9374923215](https://www.openstreetmap.org/node/9374923215) | ;1 |  | 1 de plus au RQA |
| 485 Chemin Principal | [node/11203418332](https://www.openstreetmap.org/node/11203418332) | ;205 |  | 1 de plus au RQA |
| 596 Chemin Principal | [node/11200705075](https://www.openstreetmap.org/node/11200705075) | ;L104;L105;L112;L115;L117;L119;L229;L304;L309;L320;L325;L334;L405;L414;L419;L429;L434;1-10;100-121;201-237;301-337;401-437;466 | 237;301;302;303;304;305;306;307;308;309;310;311;312;313;314;315;316;317;318;319;320;321;322;323;324;325;326;327;328;329;330;331;332;333;334;335;336;337;401;402;403;404;405;406;407;408;409;410;411;412;413;414;415;416;417;418;419;420;421;422;423;424;425;426 | 97 de plus au RQA |
| 725 Chemin Principal | [node/9854287418](https://www.openstreetmap.org/node/9854287418) | ;1;2 |  | 2 de plus au RQA |
| 782 Chemin Principal | [node/14355484348](https://www.openstreetmap.org/node/14355484348) | ;2 |  | 1 de plus au RQA |
| 806 Chemin Principal | [node/11534968933](https://www.openstreetmap.org/node/11534968933) | ;1 |  | 1 de plus au RQA |
| 1011 Chemin de La Vernière | [node/9651710013](https://www.openstreetmap.org/node/9651710013) | ;100;110;115;150;155;180;185;195;200;210 |  | 10 de plus au RQA |
| 1090 Chemin de La Vernière | [node/11165537345](https://www.openstreetmap.org/node/11165537345) | ;1 |  | 1 de plus au RQA |
| 210 Chemin de l'Aéroport | [node/14396246777](https://www.openstreetmap.org/node/14396246777) |  | 1 | 1 de plus dans OSM |
| 28 Chemin de l'École | [node/11343828322](https://www.openstreetmap.org/node/11343828322) | ;1-6 |  | 6 de plus au RQA |
| 32 Chemin de l'École | [node/11343828337](https://www.openstreetmap.org/node/11343828337) | ;101-105;201-206 |  | 11 de plus au RQA |
| 1912 Chemin de l'Étang-du-Nord | [node/11102143203](https://www.openstreetmap.org/node/11102143203) | ;1 |  | 1 de plus au RQA |
| 290 Chemin de la Dune-du-Sud | [node/14374934700](https://www.openstreetmap.org/node/14374934700) | ;1-7 |  | 7 de plus au RQA |
| 436 Chemin de la Dune-du-Sud | [node/11036037805](https://www.openstreetmap.org/node/11036037805) | ;4;8;12;292 |  | 4 de plus au RQA |
| 15 Chemin de la Piscine | [node/10179147419](https://www.openstreetmap.org/node/10179147419) | ;1 |  | 1 de plus au RQA |
| 25 Chemin de la Piscine | [node/14374960874](https://www.openstreetmap.org/node/14374960874) |  | 1 | 1 de plus dans OSM |
| 587 Chemin des Caps | [node/14374935427](https://www.openstreetmap.org/node/14374935427) | ;1;3 | ;1;2;3 | 1 de plus dans OSM |
| 711 Chemin des Caps | [node/14397155502](https://www.openstreetmap.org/node/14397155502) |  | ;2 | 1 de plus dans OSM |
| 1300 Chemin des Caps | [node/14374976725](https://www.openstreetmap.org/node/14374976725) | ;1;5 |  | 2 de plus au RQA |
| 280 Chemin du Bassin | [node/14389201133](https://www.openstreetmap.org/node/14389201133) | ;102;103;106 |  | 3 de plus au RQA |
| 125 Chemin du Parc | [node/14374960636](https://www.openstreetmap.org/node/14374960636) | ;107;118;308 |  | 3 de plus au RQA |
| 61 Chemin du Rivage | [node/14374795892](https://www.openstreetmap.org/node/14374795892) | ;1;2 | ;1 | 1 de plus au RQA |
| 63 Chemin du Rivage | [node/14374795895](https://www.openstreetmap.org/node/14374795895) | ;1;2 | ;1 | 1 de plus au RQA |
| 65 Chemin du Rivage | [node/14374935373](https://www.openstreetmap.org/node/14374935373) | ;1;2 | ;1 | 1 de plus au RQA |
| 214 Route 199 | [node/9376917092](https://www.openstreetmap.org/node/9376917092) | ;8 |  | 1 de plus au RQA |
| 251 Route 199 | [node/9377981700](https://www.openstreetmap.org/node/9377981700) | ;1;2 |  | 2 de plus au RQA |
| 493 Route 199 | [node/14374934390](https://www.openstreetmap.org/node/14374934390) |  | ;1 | 1 de plus dans OSM |
| 590 Route 199 | [node/14398214973](https://www.openstreetmap.org/node/14398214973) | ;1;2 | 2 | 1 de plus au RQA |
| 592 Route 199 | [node/14397155407](https://www.openstreetmap.org/node/14397155407) | ;1;2 |  | 2 de plus au RQA |

## Absentes d'OSM, rue présente (352)

Par qualité de la position au RQA : Incertaine 120, Bâtiment 87, Géocodée 81, Centre lot 51, Front lot 13.

| Adresse | Qualité | Logements | Position |
|---|---|---|---|
| 19 Allée Blaquière | Incertaine | ;1;3 | [carte](https://www.openstreetmap.org/?mlat=47.370153&mlon=-61.895571#map=19/47.370153/-61.895571) |
| 50 Allée Béatrice-Hubert | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.391139&mlon=-61.798911#map=19/47.391139/-61.798911) |
| 7 Allée Conrad-Miousse | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.369992&mlon=-61.902626#map=19/47.369992/-61.902626) |
| 24 Allée Elphège-Noël | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.410321&mlon=-61.912362#map=19/47.410321/-61.912362) |
| 16 Allée Gérard-Noël | Front lot | ;101-104;201-204;301-304 | [carte](https://www.openstreetmap.org/?mlat=47.369834&mlon=-61.871064#map=19/47.369834/-61.871064) |
| 100 Allée Jeffrey-Gaudet | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.364762&mlon=-61.888371#map=19/47.364762/-61.888371) |
| 4 Allée Joseph-Déraspe | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.405316&mlon=-61.918864#map=19/47.405316/-61.918864) |
| 1 Allée Longuépée | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.406519&mlon=-61.913715#map=19/47.406519/-61.913715) |
| 48 Allée Mauril-Lapierre | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.400527&mlon=-61.783914#map=19/47.400527/-61.783914) |
| 50 Allée Mauril-Lapierre | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.400656&mlon=-61.785371#map=19/47.400656/-61.785371) |
| 54 Allée Mauril-Lapierre | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.401555&mlon=-61.784676#map=19/47.401555/-61.784676) |
| 58 Allée Mauril-Lapierre | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.402168&mlon=-61.784367#map=19/47.402168/-61.784367) |
| 56 Allée Nelson-Renaud | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.360077&mlon=-61.921351#map=19/47.360077/-61.921351) |
| 5 Allée Oscar-Nadeau | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.372632&mlon=-61.894208#map=19/47.372632/-61.894208) |
| 12 Allée Oscar-Nadeau | Centre lot | ;1;3;4;6 | [carte](https://www.openstreetmap.org/?mlat=47.371639&mlon=-61.894056#map=19/47.371639/-61.894056) |
| 14 Allée Oscar-Nadeau | Centre lot | ;1;2;6 | [carte](https://www.openstreetmap.org/?mlat=47.371280&mlon=-61.894319#map=19/47.371280/-61.894319) |
| 13 Allée Wilfrid-Poirier | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.410265&mlon=-61.891313#map=19/47.410265/-61.891313) |
| 12 Allée des Deux-Ruisseaux | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.363745&mlon=-61.935000#map=19/47.363745/-61.935000) |
| 11 Allée des Marguerites | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.368852&mlon=-61.897176#map=19/47.368852/-61.897176) |
| 13 Allée des Marguerites | Centre lot | ;2 | [carte](https://www.openstreetmap.org/?mlat=47.369020&mlon=-61.896829#map=19/47.369020/-61.896829) |
| 15 Allée des Marguerites | Centre lot | ;2 | [carte](https://www.openstreetmap.org/?mlat=47.369229&mlon=-61.896610#map=19/47.369229/-61.896610) |
| 16 Allée des Marguerites | Incertaine | ;1;2 | [carte](https://www.openstreetmap.org/?mlat=47.368873&mlon=-61.896362#map=19/47.368873/-61.896362) |
| 17 Allée des Marguerites | Centre lot | ;2 | [carte](https://www.openstreetmap.org/?mlat=47.369416&mlon=-61.896320#map=19/47.369416/-61.896320) |
| 19 Allée des Marguerites | Centre lot | ;1;2 | [carte](https://www.openstreetmap.org/?mlat=47.369561&mlon=-61.896057#map=19/47.369561/-61.896057) |
| 21 Allée des Marguerites | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.369679&mlon=-61.895761#map=19/47.369679/-61.895761) |
| 22 Allée des Marguerites | Incertaine | ;1;2 | [carte](https://www.openstreetmap.org/?mlat=47.369321&mlon=-61.895476#map=19/47.369321/-61.895476) |
| 23 Allée des Marguerites | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.369827&mlon=-61.895428#map=19/47.369827/-61.895428) |
| 4 Allée des Petits-Fruits | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.414655&mlon=-61.771803#map=19/47.414655/-61.771803) |
| 51 Allée des Petits-Fruits | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.415667&mlon=-61.767965#map=19/47.415667/-61.767965) |
| 21 Allée des Puits | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.399730&mlon=-61.904186#map=19/47.399730/-61.904186) |
| 34 Allée des Puits | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.396965&mlon=-61.905817#map=19/47.396965/-61.905817) |
| 16 Allée des Épinettes | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.362200&mlon=-61.882562#map=19/47.362200/-61.882562) |
| 18 Allée des Épinettes | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.361841&mlon=-61.882424#map=19/47.361841/-61.882424) |
| 9 Allée du Versant | Centre lot | ;1;2 | [carte](https://www.openstreetmap.org/?mlat=47.368483&mlon=-61.884509#map=19/47.368483/-61.884509) |
| 22 Allée à Damas | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.223642&mlon=-61.983773#map=19/47.223642/-61.983773) |
| 26 Chemin Alphonse | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.412544&mlon=-61.777831#map=19/47.412544/-61.777831) |
| 48 Chemin Armand-Décoste | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.412557&mlon=-61.892962#map=19/47.412557/-61.892962) |
| 50 Chemin Armand-Décoste | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.412474&mlon=-61.893072#map=19/47.412474/-61.893072) |
| 67 Chemin Armand-Décoste | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.410374&mlon=-61.895916#map=19/47.410374/-61.895916) |
| 1 Chemin Big Hill | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.272502&mlon=-61.705590#map=19/47.272502/-61.705590) |
| 483 Chemin Boisville Ouest | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.369011&mlon=-61.955569#map=19/47.369011/-61.955569) |
| 13 Chemin Boudreau | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.238706&mlon=-61.885774#map=19/47.238706/-61.885774) |
| 127 Chemin Boudreau | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.418421&mlon=-61.765380#map=19/47.418421/-61.765380) |
| 41 Chemin Bouffard | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.366794&mlon=-61.940488#map=19/47.366794/-61.940488) |
| 81 Chemin Bouffard | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.368525&mlon=-61.944137#map=19/47.368525/-61.944137) |
| 206 Chemin Bouffard | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.369910&mlon=-61.952857#map=19/47.369910/-61.952857) |
| 27 Chemin Bourgeois | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.404944&mlon=-61.903232#map=19/47.404944/-61.903232) |
| 36 Chemin Bourgeois | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.405367&mlon=-61.903173#map=19/47.405367/-61.903173) |
| 43 Chemin Bourgeois | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.354542&mlon=-61.886507#map=19/47.354542/-61.886507) |
| 71 Chemin Chevarie | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.377350&mlon=-61.935187#map=19/47.377350/-61.935187) |
| 87 Chemin Chevrier | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.222528&mlon=-61.971455#map=19/47.222528/-61.971455) |
| 40 Chemin Chiasson | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.362740&mlon=-61.920968#map=19/47.362740/-61.920968) |
| 34 Chemin Cormier | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.375566&mlon=-61.916285#map=19/47.375566/-61.916285) |
| 138 Chemin Coulombe | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.356926&mlon=-61.939525#map=19/47.356926/-61.939525) |
| 148 Chemin Coulombe | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.356630&mlon=-61.938320#map=19/47.356630/-61.938320) |
| 62 Chemin E.-Bourque | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.374607&mlon=-61.955811#map=19/47.374607/-61.955811) |
| 12 Chemin Errol | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.616036&mlon=-61.472754#map=19/47.616036/-61.472754) |
| 45 Chemin F.-Longuépée | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.408020&mlon=-61.897204#map=19/47.408020/-61.897204) |
| 49 Chemin F.-Longuépée | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.408781&mlon=-61.897870#map=19/47.408781/-61.897870) |
| 570 Chemin Fougère | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.372923&mlon=-61.957640#map=19/47.372923/-61.957640) |
| 24 Chemin Garneau | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.365724&mlon=-61.883642#map=19/47.365724/-61.883642) |
| 11 Chemin Head | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.572417&mlon=-61.475646#map=19/47.572417/-61.475646) |
| 51 Chemin Jerry | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.619998&mlon=-61.512338#map=19/47.619998/-61.512338) |
| 70 Chemin John-Aucoin | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403884&mlon=-61.886746#map=19/47.403884/-61.886746) |
| 120 Chemin John-Aucoin | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.402084&mlon=-61.890112#map=19/47.402084/-61.890112) |
| 47 Chemin Lapierre | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.402753&mlon=-61.911472#map=19/47.402753/-61.911472) |
| 83 Chemin Lapierre | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.401860&mlon=-61.914687#map=19/47.401860/-61.914687) |
| 257 Chemin Lapierre | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.399266&mlon=-61.926151#map=19/47.399266/-61.926151) |
| 378 Chemin Lapierre | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.399993&mlon=-61.930238#map=19/47.399993/-61.930238) |
| 200 Chemin Le Pré | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.359947&mlon=-61.909145#map=19/47.359947/-61.909145) |
| 32 Chemin Leblanc | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.525999&mlon=-61.704955#map=19/47.525999/-61.704955) |
| 85 Chemin Leblanc | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.527059&mlon=-61.700837#map=19/47.527059/-61.700837) |
| 114 Chemin Loiseau | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.400473&mlon=-61.789683#map=19/47.400473/-61.789683) |
| 336 Chemin Léonard-Aucoin | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.410559&mlon=-61.884399#map=19/47.410559/-61.884399) |
| 276 Chemin Main | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.272609&mlon=-61.707758#map=19/47.272609/-61.707758) |
| 499 Chemin Main | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.270279&mlon=-61.701543#map=19/47.270279/-61.701543) |
| 47 Chemin Martinet | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.413461&mlon=-61.885864#map=19/47.413461/-61.885864) |
| 57 Chemin Martinet | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.413990&mlon=-61.885695#map=19/47.413990/-61.885695) |
| 88 Chemin Martinet | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.229190&mlon=-61.865783#map=19/47.229190/-61.865783) |
| 161 Chemin Martinet | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.226342&mlon=-61.861588#map=19/47.226342/-61.861588) |
| 83 Chemin Massé | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.224284&mlon=-61.979794#map=19/47.224284/-61.979794) |
| 99 Chemin Massé | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.224522&mlon=-61.981468#map=19/47.224522/-61.981468) |
| 120 Chemin Massé | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.224508&mlon=-61.979129#map=19/47.224508/-61.979129) |
| 49 Chemin Miousse | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.408849&mlon=-61.884490#map=19/47.408849/-61.884490) |
| 1 Chemin North | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.622735&mlon=-61.516785#map=19/47.622735/-61.516785) |
| 80 Chemin Noël | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.403554&mlon=-61.868975#map=19/47.403554/-61.868975) |
| 395 Chemin Oscar | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.379882&mlon=-61.864877#map=19/47.379882/-61.864877) |
| 403 Chemin Oscar | Centre lot | ;101-104;201-204 | [carte](https://www.openstreetmap.org/?mlat=47.379954&mlon=-61.866580#map=19/47.379954/-61.866580) |
| 40 Chemin Park | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.627115&mlon=-61.523153#map=19/47.627115/-61.523153) |
| 539 Chemin Petitpas | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.382295&mlon=-61.873519#map=19/47.382295/-61.873519) |
| 575 Chemin Petitpas | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.381893&mlon=-61.873885#map=19/47.381893/-61.873885) |
| 24 Chemin Philippe-Thorne | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403729&mlon=-61.906140#map=19/47.403729/-61.906140) |
| 44 Chemin Philippe-Thorne | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.404731&mlon=-61.907192#map=19/47.404731/-61.907192) |
| 120 Chemin Philippe-Thorne | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.408078&mlon=-61.909637#map=19/47.408078/-61.909637) |
| 63 Chemin Poirier | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.414309&mlon=-61.805586#map=19/47.414309/-61.805586) |
| 68 Chemin Poirier | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.409946&mlon=-61.873657#map=19/47.409946/-61.873657) |
| 1 Chemin Principal | Centre lot | ;101-106;201-206 | [carte](https://www.openstreetmap.org/?mlat=47.389572&mlon=-61.856919#map=19/47.389572/-61.856919) |
| 3 Chemin Principal | Centre lot | ;101-106;201-206 | [carte](https://www.openstreetmap.org/?mlat=47.389067&mlon=-61.857138#map=19/47.389067/-61.857138) |
| 5 Chemin Principal | Centre lot | ;101-106;201-206 | [carte](https://www.openstreetmap.org/?mlat=47.388574&mlon=-61.857465#map=19/47.388574/-61.857465) |
| 118 Chemin Principal | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.617079&mlon=-61.540137#map=19/47.617079/-61.540137) |
| 195 Chemin Principal | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.380182&mlon=-61.860756#map=19/47.380182/-61.860756) |
| 195 Chemin Principal | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.618714&mlon=-61.533632#map=19/47.618714/-61.533632) |
| 244 Chemin Principal | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.620358&mlon=-61.528068#map=19/47.620358/-61.528068) |
| 282 Chemin Principal | Incertaine | ;1;10-12 | [carte](https://www.openstreetmap.org/?mlat=47.378877&mlon=-61.863252#map=19/47.378877/-61.863252) |
| 284 Chemin Principal | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.378597&mlon=-61.863685#map=19/47.378597/-61.863685) |
| 288 Chemin Principal | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.378767&mlon=-61.863832#map=19/47.378767/-61.863832) |
| 352 Chemin Principal | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.377348&mlon=-61.865478#map=19/47.377348/-61.865478) |
| 417 Chemin Principal | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.620949&mlon=-61.515531#map=19/47.620949/-61.515531) |
| 503 Chemin Principal | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.616163&mlon=-61.514155#map=19/47.616163/-61.514155) |
| 530 Chemin Principal | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.615556&mlon=-61.512396#map=19/47.615556/-61.512396) |
| 535 Chemin Principal | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.615788&mlon=-61.512481#map=19/47.615788/-61.512481) |
| 562 Chemin Principal | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.374404&mlon=-61.872986#map=19/47.374404/-61.872986) |
| 677 Chemin Principal | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.373266&mlon=-61.877529#map=19/47.373266/-61.877529) |
| 696 Chemin Principal | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.372806&mlon=-61.878011#map=19/47.372806/-61.878011) |
| 730 Chemin Principal | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.372198&mlon=-61.879744#map=19/47.372198/-61.879744) |
| 789 Chemin Principal | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.570809&mlon=-61.480325#map=19/47.570809/-61.480325) |
| 29 Chemin Prudent-Harvie | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.391006&mlon=-61.872830#map=19/47.391006/-61.872830) |
| 120 Chemin Prudent-Harvie | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.393830&mlon=-61.877852#map=19/47.393830/-61.877852) |
| 9 Chemin Red | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.615461&mlon=-61.509211#map=19/47.615461/-61.509211) |
| 583 Chemin Réginald | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.372282&mlon=-61.873299#map=19/47.372282/-61.873299) |
| 98 Chemin School | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.275508&mlon=-61.706574#map=19/47.275508/-61.706574) |
| 101 Chemin School | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.275904&mlon=-61.706930#map=19/47.275904/-61.706930) |
| 255 Chemin School | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.279527&mlon=-61.706663#map=19/47.279527/-61.706663) |
| 32 Chemin Seacow Path | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.572913&mlon=-61.483182#map=19/47.572913/-61.483182) |
| 74 Chemin Seacow Path | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.574028&mlon=-61.482468#map=19/47.574028/-61.482468) |
| 20 Chemin Turbide | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.226375&mlon=-61.927562#map=19/47.226375/-61.927562) |
| 160 Chemin Valentin-Cummings | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403585&mlon=-61.896848#map=19/47.403585/-61.896848) |
| 200 Chemin Wide | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.614759&mlon=-61.527681#map=19/47.614759/-61.527681) |
| 11 Chemin d'en Bas | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.223138&mlon=-61.926230#map=19/47.223138/-61.926230) |
| 232 Chemin d'en Haut | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.235688&mlon=-61.856329#map=19/47.235688/-61.856329) |
| 360 Chemin d'en Haut | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.237650&mlon=-61.846503#map=19/47.237650/-61.846503) |
| 15 Chemin de Ceinture | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.545744&mlon=-61.536686#map=19/47.545744/-61.536686) |
| 194 Chemin de Gros-Cap | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.370597&mlon=-61.873568#map=19/47.370597/-61.873568) |
| 996A Chemin de La Grave | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.237417&mlon=-61.834440#map=19/47.237417/-61.834440) |
| 996B Chemin de La Grave | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.237417&mlon=-61.834440#map=19/47.237417/-61.834440) |
| 1000 Chemin de La Grave | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.237645&mlon=-61.834342#map=19/47.237645/-61.834342) |
| 2001 Chemin de La Grave | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.236562&mlon=-61.827667#map=19/47.236562/-61.827667) |
| 55 Chemin de La Martinique | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.369381&mlon=-61.914145#map=19/47.369381/-61.914145) |
| 347 Chemin de La Martinique | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.353892&mlon=-61.914629#map=19/47.353892/-61.914629) |
| 428 Chemin de La Martinique | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.349542&mlon=-61.916077#map=19/47.349542/-61.916077) |
| 433 Chemin de La Martinique | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349070&mlon=-61.915537#map=19/47.349070/-61.915537) |
| 1055 Chemin de La Vernière | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.370853&mlon=-61.886564#map=19/47.370853/-61.886564) |
| 1098 Chemin de La Vernière | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.371524&mlon=-61.889406#map=19/47.371524/-61.889406) |
| 1099 Chemin de La Vernière | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.371121&mlon=-61.889831#map=19/47.371121/-61.889831) |
| 1110 Chemin de La Vernière | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.373815&mlon=-61.889073#map=19/47.373815/-61.889073) |
| 1137 Chemin de La Vernière | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.372267&mlon=-61.892900#map=19/47.372267/-61.892900) |
| 1156 Chemin de La Vernière | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.373387&mlon=-61.894246#map=19/47.373387/-61.894246) |
| 1297 Chemin de La Vernière | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.370119&mlon=-61.904898#map=19/47.370119/-61.904898) |
| 25 Chemin de Millerand | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.221433&mlon=-61.983743#map=19/47.221433/-61.983743) |
| 48 Chemin de Millerand | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.222990&mlon=-61.985001#map=19/47.222990/-61.985001) |
| 26 Chemin de l'Anse-à-la-Cabane | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.219099&mlon=-61.985927#map=19/47.219099/-61.985927) |
| 33 Chemin de l'Anse-à-la-Cabane | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.217872&mlon=-61.985664#map=19/47.217872/-61.985664) |
| 139 Chemin de l'Aéroport | Incertaine | ;1-3 | [carte](https://www.openstreetmap.org/?mlat=47.419588&mlon=-61.775585#map=19/47.419588/-61.775585) |
| 182 Chemin de l'Aéroport | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.421586&mlon=-61.774086#map=19/47.421586/-61.774086) |
| 115 Chemin de l'Hôpital | Centre lot | ;1;2 | [carte](https://www.openstreetmap.org/?mlat=47.415513&mlon=-61.891117#map=19/47.415513/-61.891117) |
| 183 Chemin de l'Hôpital | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.415017&mlon=-61.894907#map=19/47.415017/-61.894907) |
| 291 Chemin de l'Hôpital | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.410816&mlon=-61.900053#map=19/47.410816/-61.900053) |
| 307 Chemin de l'Hôpital | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.409931&mlon=-61.899998#map=19/47.409931/-61.899998) |
| 20 Chemin de l'École | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.530052&mlon=-61.707869#map=19/47.530052/-61.707869) |
| 40 Chemin de l'Église | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.562154&mlon=-61.524114#map=19/47.562154/-61.524114) |
| 478 Chemin de l'Église | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.396587&mlon=-61.896588#map=19/47.396587/-61.896588) |
| 44 Chemin de l'Étang | Géocodée | 0001;0002;0003 | [carte](https://www.openstreetmap.org/?mlat=47.242558&mlon=-61.906169#map=19/47.242558/-61.906169) |
| 1423 Chemin de l'Étang-des-Caps | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.221680&mlon=-61.996428#map=19/47.221680/-61.996428) |
| 1442 Chemin de l'Étang-des-Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.221909&mlon=-61.997977#map=19/47.221909/-61.997977) |
| 1510 Chemin de l'Étang-des-Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.222136&mlon=-62.002782#map=19/47.222136/-62.002782) |
| 1961 Chemin de l'Étang-des-Caps | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.241899&mlon=-62.013311#map=19/47.241899/-62.013311) |
| 2111 Chemin de l'Étang-des-Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.250917&mlon=-62.010952#map=19/47.250917/-62.010952) |
| 2120 Chemin de l'Étang-des-Caps | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.250781&mlon=-62.010225#map=19/47.250781/-62.010225) |
| 1461 Chemin de l'Étang-du-Nord | Incertaine | 4 | [carte](https://www.openstreetmap.org/?mlat=47.373627&mlon=-61.917348#map=19/47.373627/-61.917348) |
| 1526 Chemin de l'Étang-du-Nord | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.375208&mlon=-61.922267#map=19/47.375208/-61.922267) |
| 1599 Chemin de l'Étang-du-Nord | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.372986&mlon=-61.927900#map=19/47.372986/-61.927900) |
| 1660 Chemin de l'Étang-du-Nord | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.374790&mlon=-61.933583#map=19/47.374790/-61.933583) |
| 175 Chemin de la Baie | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.232445&mlon=-61.873705#map=19/47.232445/-61.873705) |
| 102 Chemin de la Baie-de-Plaisance | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.242220&mlon=-61.883313#map=19/47.242220/-61.883313) |
| 76 Chemin de la Belle-Anse | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.397422&mlon=-61.931450#map=19/47.397422/-61.931450) |
| 195 Chemin de la Belle-Anse | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.396172&mlon=-61.938476#map=19/47.396172/-61.938476) |
| 219 Chemin de la Belle-Anse | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.394851&mlon=-61.937527#map=19/47.394851/-61.937527) |
| 221 Chemin de la Belle-Anse | Incertaine | ;1;2 | [carte](https://www.openstreetmap.org/?mlat=47.394922&mlon=-61.938705#map=19/47.394922/-61.938705) |
| 98 Chemin de la Dune-du-Sud | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.411695&mlon=-61.771847#map=19/47.411695/-61.771847) |
| 123 Chemin de la Dune-du-Sud | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.411950&mlon=-61.769915#map=19/47.411950/-61.769915) |
| 322 Chemin de la Dune-du-Sud | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.416250&mlon=-61.756097#map=19/47.416250/-61.756097) |
| 348 Chemin de la Dune-du-Sud | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.417629&mlon=-61.756312#map=19/47.417629/-61.756312) |
| 360 Chemin de la Dune-du-Sud | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.419159&mlon=-61.756294#map=19/47.419159/-61.756294) |
| 380 Chemin de la Dune-du-Sud | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.419663&mlon=-61.755571#map=19/47.419663/-61.755571) |
| 293 Chemin de la Grande-Allée | Incertaine | ;1;2 | [carte](https://www.openstreetmap.org/?mlat=47.371327&mlon=-61.880455#map=19/47.371327/-61.880455) |
| 297 Chemin de la Grande-Allée | Centre lot | ;1;3 | [carte](https://www.openstreetmap.org/?mlat=47.371507&mlon=-61.880705#map=19/47.371507/-61.880705) |
| 299 Chemin de la Grande-Allée | Centre lot | ;1;3 | [carte](https://www.openstreetmap.org/?mlat=47.371387&mlon=-61.881112#map=19/47.371387/-61.881112) |
| 25 Chemin de la Gravel Point | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.277913&mlon=-61.716906#map=19/47.277913/-61.716906) |
| 376 Chemin de la Mine | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.373707&mlon=-61.881539#map=19/47.373707/-61.881539) |
| 2179 Chemin de la Montagne | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.251029&mlon=-62.006148#map=19/47.251029/-62.006148) |
| 2696 Chemin de la Montagne | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.243364&mlon=-61.982208#map=19/47.243364/-61.982208) |
| 2846 Chemin de la Montagne | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.247242&mlon=-61.969467#map=19/47.247242/-61.969467) |
| 2959 Chemin de la Montagne | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.244955&mlon=-61.958928#map=19/47.244955/-61.958928) |
| 95 Chemin de la Petite-Baie | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.407275&mlon=-61.823058#map=19/47.407275/-61.823058) |
| 130 Chemin de la Petite-Baie | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.407872&mlon=-61.825644#map=19/47.407872/-61.825644) |
| 23 Chemin de la Pointe | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.404569&mlon=-61.836751#map=19/47.404569/-61.836751) |
| 61 Chemin de la Pointe-Basse | Incertaine | 1 | [carte](https://www.openstreetmap.org/?mlat=47.398890&mlon=-61.810341#map=19/47.398890/-61.810341) |
| 238 Chemin de la Pointe-Basse | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.393839&mlon=-61.797002#map=19/47.393839/-61.797002) |
| 254 Chemin de la Pointe-Basse | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.393589&mlon=-61.796162#map=19/47.393589/-61.796162) |
| 55 Chemin de la Pointe-des-Canots | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.248716&mlon=-61.973865#map=19/47.248716/-61.973865) |
| 59 Chemin de la Pointe-à-Marichite | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.227136&mlon=-61.915833#map=19/47.227136/-61.915833) |
| 42 Chemin des Arpenteurs | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.237493&mlon=-62.009851#map=19/47.237493/-62.009851) |
| 38 Chemin des Bas | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.414199&mlon=-61.785043#map=19/47.414199/-61.785043) |
| 13 Chemin des Bouchard | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.241628&mlon=-61.901236#map=19/47.241628/-61.901236) |
| 97 Chemin des Buttes | Incertaine | 2 | [carte](https://www.openstreetmap.org/?mlat=47.398029&mlon=-61.782776#map=19/47.398029/-61.782776) |
| 321 Chemin des Buttes | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.407898&mlon=-61.774956#map=19/47.407898/-61.774956) |
| 60 Chemin des Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.392566&mlon=-61.860444#map=19/47.392566/-61.860444) |
| 509 Chemin des Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.408906&mlon=-61.886466#map=19/47.408906/-61.886466) |
| 584 Chemin des Caps | Géocodée | 5 | [carte](https://www.openstreetmap.org/?mlat=47.408918&mlon=-61.890990#map=19/47.408918/-61.890990) |
| 1069 Chemin des Caps | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.395843&mlon=-61.923197#map=19/47.395843/-61.923197) |
| 1081 Chemin des Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.395702&mlon=-61.924289#map=19/47.395702/-61.924289) |
| 1116 Chemin des Caps | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.395118&mlon=-61.926901#map=19/47.395118/-61.926901) |
| 1172 Chemin des Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.394486&mlon=-61.931495#map=19/47.394486/-61.931495) |
| 1231 Chemin des Caps | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.393964&mlon=-61.936244#map=19/47.393964/-61.936244) |
| 1865 Chemin des Caps | Géocodée | 1 | [carte](https://www.openstreetmap.org/?mlat=47.373056&mlon=-61.950387#map=19/47.373056/-61.950387) |
| 6 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349078&mlon=-61.915050#map=19/47.349078/-61.915050) |
| 12 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349282&mlon=-61.914595#map=19/47.349282/-61.914595) |
| 14 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349378&mlon=-61.914380#map=19/47.349378/-61.914380) |
| 18 Chemin des Chalets | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.349333&mlon=-61.914064#map=19/47.349333/-61.914064) |
| 20 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349518&mlon=-61.913877#map=19/47.349518/-61.913877) |
| 22 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349596&mlon=-61.913748#map=19/47.349596/-61.913748) |
| 25 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349949&mlon=-61.913698#map=19/47.349949/-61.913698) |
| 26 Chemin des Chalets | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.349596&mlon=-61.913748#map=19/47.349596/-61.913748) |
| 30 Chemin des Chalets | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.349642&mlon=-61.913258#map=19/47.349642/-61.913258) |
| 31 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350045&mlon=-61.913349#map=19/47.350045/-61.913349) |
| 33 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350157&mlon=-61.913139#map=19/47.350157/-61.913139) |
| 35 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350201&mlon=-61.913027#map=19/47.350201/-61.913027) |
| 38 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.349975&mlon=-61.912726#map=19/47.349975/-61.912726) |
| 40 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350063&mlon=-61.912536#map=19/47.350063/-61.912536) |
| 46 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350222&mlon=-61.911981#map=19/47.350222/-61.911981) |
| 50 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350281&mlon=-61.911747#map=19/47.350281/-61.911747) |
| 56 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350417&mlon=-61.911381#map=19/47.350417/-61.911381) |
| 58 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350546&mlon=-61.911032#map=19/47.350546/-61.911032) |
| 71 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.351081&mlon=-61.910309#map=19/47.351081/-61.910309) |
| 74 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.350853&mlon=-61.909893#map=19/47.350853/-61.909893) |
| 79 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.351169&mlon=-61.909522#map=19/47.351169/-61.909522) |
| 81 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.351291&mlon=-61.909516#map=19/47.351291/-61.909516) |
| 83 Chemin des Chalets | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.351287&mlon=-61.909342#map=19/47.351287/-61.909342) |
| 85 Chemin des Chalets | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.351269&mlon=-61.909193#map=19/47.351269/-61.909193) |
| 155 Chemin des Chalets | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.353347&mlon=-61.904804#map=19/47.353347/-61.904804) |
| 187 Chemin des Chalets | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.354464&mlon=-61.902764#map=19/47.354464/-61.902764) |
| 584 Chemin des Cyr | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.386420&mlon=-61.863562#map=19/47.386420/-61.863562) |
| 127 Chemin des Gaudet | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.364524&mlon=-61.885350#map=19/47.364524/-61.885350) |
| 81 Chemin des Marais | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.399705&mlon=-61.795246#map=19/47.399705/-61.795246) |
| 3 Chemin des Pealey | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.550056&mlon=-61.548958#map=19/47.550056/-61.548958) |
| 39 Chemin des Pealey | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.549711&mlon=-61.552280#map=19/47.549711/-61.552280) |
| 92 Chemin des Prés | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.408050&mlon=-61.801749#map=19/47.408050/-61.801749) |
| 13 Chemin des Vigneau | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.380095&mlon=-61.947112#map=19/47.380095/-61.947112) |
| 27 Chemin des Vigneau | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.380002&mlon=-61.948034#map=19/47.380002/-61.948034) |
| 45 Chemin des Vigneau | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.407979&mlon=-61.809159#map=19/47.407979/-61.809159) |
| 76 Chemin des Échoueries | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.391146&mlon=-61.777818#map=19/47.391146/-61.777818) |
| 100 Chemin des Échoueries | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.391453&mlon=-61.776219#map=19/47.391453/-61.776219) |
| 261 Chemin des Échoueries | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.399172&mlon=-61.775752#map=19/47.399172/-61.775752) |
| 65 Chemin du Bassin | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.240791&mlon=-61.899735#map=19/47.240791/-61.899735) |
| 577 Chemin du Bassin | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.221826&mlon=-61.932520#map=19/47.221826/-61.932520) |
| 753 Chemin du Bassin | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.217581&mlon=-61.944772#map=19/47.217581/-61.944772) |
| 930 Chemin du Bassin | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.218972&mlon=-61.959853#map=19/47.218972/-61.959853) |
| 965 Chemin du Bassin | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.217251&mlon=-61.961903#map=19/47.217251/-61.961903) |
| 1129 Chemin du Bassin | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.215428&mlon=-61.975122#map=19/47.215428/-61.975122) |
| 1133 Chemin du Bassin | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.215600&mlon=-61.975463#map=19/47.215600/-61.975463) |
| 38 Chemin du Bassin Ouest | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.550992&mlon=-61.547361#map=19/47.550992/-61.547361) |
| 131 Chemin du Bassin Ouest | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.547594&mlon=-61.541104#map=19/47.547594/-61.541104) |
| 150 Chemin du Bassin Ouest | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.545668&mlon=-61.540418#map=19/47.545668/-61.540418) |
| 153 Chemin du Bassin Ouest | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.546268&mlon=-61.540644#map=19/47.546268/-61.540644) |
| 59 Chemin du Bois-Brûlé | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.358962&mlon=-61.928941#map=19/47.358962/-61.928941) |
| 205 Chemin du Cap-Rouge | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.409073&mlon=-61.812302#map=19/47.409073/-61.812302) |
| 321 Chemin du Cap-Rouge | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.413150&mlon=-61.803696#map=19/47.413150/-61.803696) |
| 457 Chemin du Cap-Rouge | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.412221&mlon=-61.792554#map=19/47.412221/-61.792554) |
| 515 Chemin du Grand-Pré | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.229495&mlon=-61.927219#map=19/47.229495/-61.927219) |
| 560 Chemin du Grand-Pré | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.225926&mlon=-61.925699#map=19/47.225926/-61.925699) |
| 648 Chemin du Grand-Ruisseau | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.385917&mlon=-61.873614#map=19/47.385917/-61.873614) |
| 864 Chemin du Grand-Ruisseau | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.393295&mlon=-61.886003#map=19/47.393295/-61.886003) |
| 329 Chemin du Gros-Cap | Bâtiment | 1-4 | [carte](https://www.openstreetmap.org/?mlat=47.365259&mlon=-61.872411#map=19/47.365259/-61.872411) |
| 390 Chemin du Gros-Cap | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.361860&mlon=-61.873886#map=19/47.361860/-61.873886) |
| 541 Chemin du Gros-Cap | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.354746&mlon=-61.878184#map=19/47.354746/-61.878184) |
| 691 Chemin du Gros-Cap | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.352217&mlon=-61.889053#map=19/47.352217/-61.889053) |
| 1010 Chemin du Gros-Cap | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.367556&mlon=-61.896092#map=19/47.367556/-61.896092) |
| 1026 Chemin du Gros-Cap | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.368394&mlon=-61.897352#map=19/47.368394/-61.897352) |
| 529 Chemin du Marconi | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.385240&mlon=-61.860162#map=19/47.385240/-61.860162) |
| 650 Chemin du Marconi | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.388005&mlon=-61.866706#map=19/47.388005/-61.866706) |
| 89 Chemin du P'tit-Bois Nord | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.240685&mlon=-61.944187#map=19/47.240685/-61.944187) |
| 120 Chemin du P'tit-Bois Sud | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.224944&mlon=-61.943089#map=19/47.224944/-61.943089) |
| 60 Chemin du Parc | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.375538&mlon=-61.888785#map=19/47.375538/-61.888785) |
| 127 Chemin du Parc | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.378664&mlon=-61.853108#map=19/47.378664/-61.853108) |
| 55 Chemin du Phare | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.382326&mlon=-61.950111#map=19/47.382326/-61.950111) |
| 51 Chemin du Portage | Front lot |  | [carte](https://www.openstreetmap.org/?mlat=47.243363&mlon=-61.900972#map=19/47.243363/-61.900972) |
| 24 Chemin du Quai | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.392019&mlon=-61.790384#map=19/47.392019/-61.790384) |
| 40 Chemin du Quai | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.390633&mlon=-61.789772#map=19/47.390633/-61.789772) |
| 49 Chemin du Quai | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.390128&mlon=-61.788117#map=19/47.390128/-61.788117) |
| 313 Chemin du Quai | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.379104&mlon=-61.859230#map=19/47.379104/-61.859230) |
| 345 Chemin du Quai | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.379225&mlon=-61.859354#map=19/47.379225/-61.859354) |
| 25 Chemin du Quai Nord | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.527623&mlon=-61.711407#map=19/47.527623/-61.711407) |
| 31 Chemin du Quai Nord | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.528517&mlon=-61.711701#map=19/47.528517/-61.711701) |
| 56 Chemin du Quai Sud | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.523589&mlon=-61.709229#map=19/47.523589/-61.709229) |
| 58 Chemin du Quai Sud | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.523187&mlon=-61.709088#map=19/47.523187/-61.709088) |
| 116 Chemin du Sable | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.226711&mlon=-61.846972#map=19/47.226711/-61.846972) |
| 240 Chemin du Sable | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.225416&mlon=-61.838592#map=19/47.225416/-61.838592) |
| 231 Chemin Éloquin | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.385984&mlon=-61.868363#map=19/47.385984/-61.868363) |
| 30 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.570168&mlon=-61.498535#map=19/47.570168/-61.498535) |
| 82 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.402739&mlon=-61.835485#map=19/47.402739/-61.835485) |
| 91 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.247321&mlon=-61.899757#map=19/47.247321/-61.899757) |
| 97 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403356&mlon=-61.833449#map=19/47.403356/-61.833449) |
| 101 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.403379&mlon=-61.833146#map=19/47.403379/-61.833146) |
| 112 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403112&mlon=-61.833387#map=19/47.403112/-61.833387) |
| 122 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.401709&mlon=-61.830825#map=19/47.401709/-61.830825) |
| 131 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.401091&mlon=-61.827675#map=19/47.401091/-61.827675) |
| 155 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.401048&mlon=-61.827509#map=19/47.401048/-61.827509) |
| 173 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.401018&mlon=-61.827367#map=19/47.401018/-61.827367) |
| 185 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.242922&mlon=-61.895604#map=19/47.242922/-61.895604) |
| 185 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.400970&mlon=-61.827228#map=19/47.400970/-61.827228) |
| 189 Route 199 | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.401097&mlon=-61.826309#map=19/47.401097/-61.826309) |
| 198 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.400601&mlon=-61.826526#map=19/47.400601/-61.826526) |
| 202 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.566471&mlon=-61.512688#map=19/47.566471/-61.512688) |
| 206 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.567061&mlon=-61.513668#map=19/47.567061/-61.513668) |
| 225 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.401146&mlon=-61.822987#map=19/47.401146/-61.822987) |
| 253 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.563674&mlon=-61.515503#map=19/47.563674/-61.515503) |
| 265 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.399244&mlon=-61.821239#map=19/47.399244/-61.821239) |
| 285 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.399321&mlon=-61.818772#map=19/47.399321/-61.818772) |
| 295 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.399461&mlon=-61.818294#map=19/47.399461/-61.818294) |
| 303 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.561813&mlon=-61.518975#map=19/47.561813/-61.518975) |
| 323 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.561078&mlon=-61.519640#map=19/47.561078/-61.519640) |
| 363 Route 199 | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.390062&mlon=-61.853877#map=19/47.390062/-61.853877) |
| 373 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.558873&mlon=-61.522117#map=19/47.558873/-61.522117) |
| 380 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.401021&mlon=-61.811713#map=19/47.401021/-61.811713) |
| 403 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.557967&mlon=-61.525161#map=19/47.557967/-61.525161) |
| 403 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.388135&mlon=-61.856531#map=19/47.388135/-61.856531) |
| 455 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.402764&mlon=-61.806133#map=19/47.402764/-61.806133) |
| 460 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.402507&mlon=-61.805478#map=19/47.402507/-61.805478) |
| 483 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.238973&mlon=-61.872829#map=19/47.238973/-61.872829) |
| 485 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403213&mlon=-61.804375#map=19/47.403213/-61.804375) |
| 498 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.402894&mlon=-61.802390#map=19/47.402894/-61.802390) |
| 500 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403095&mlon=-61.802244#map=19/47.403095/-61.802244) |
| 503 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403504&mlon=-61.802342#map=19/47.403504/-61.802342) |
| 540 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.403554&mlon=-61.798600#map=19/47.403554/-61.798600) |
| 569 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.555152&mlon=-61.537431#map=19/47.555152/-61.537431) |
| 685 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.234816&mlon=-61.858384#map=19/47.234816/-61.858384) |
| 701 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.407845&mlon=-61.786883#map=19/47.407845/-61.786883) |
| 705 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.234055&mlon=-61.856649#map=19/47.234055/-61.856649) |
| 718 Route 199 | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.233454&mlon=-61.855305#map=19/47.233454/-61.855305) |
| 747 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.551196&mlon=-61.550857#map=19/47.551196/-61.550857) |
| 760 Route 199 | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.551769&mlon=-61.551699#map=19/47.551769/-61.551699) |
| 770 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.233840&mlon=-61.851213#map=19/47.233840/-61.851213) |
| 787 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.411222&mlon=-61.781537#map=19/47.411222/-61.781537) |
| 841 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.413199&mlon=-61.778779#map=19/47.413199/-61.778779) |
| 907 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.556220&mlon=-61.560843#map=19/47.556220/-61.560843) |
| 1011 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.419978&mlon=-61.766068#map=19/47.419978/-61.766068) |
| 1151 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.425201&mlon=-61.757683#map=19/47.425201/-61.757683) |
| 1234 Route 199 | Bâtiment |  | [carte](https://www.openstreetmap.org/?mlat=47.428440&mlon=-61.754538#map=19/47.428440/-61.754538) |
| 1274 Route 199 | Incertaine |  | [carte](https://www.openstreetmap.org/?mlat=47.439909&mlon=-61.754107#map=19/47.439909/-61.754107) |
| 1320 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.455647&mlon=-61.748794#map=19/47.455647/-61.748794) |
| 1700 Route 199 | Centre lot |  | [carte](https://www.openstreetmap.org/?mlat=47.529065&mlon=-61.704645#map=19/47.529065/-61.704645) |
| 1714 Route 199 | Géocodée |  | [carte](https://www.openstreetmap.org/?mlat=47.529968&mlon=-61.703788#map=19/47.529968/-61.703788) |

## Absentes d'OSM, rue introuvable sous ce nom (52)

Aucune rue d'OSM de ce nom à moins de 300 m. La rue nommée la plus proche est indiquée, si elle existe.

| Adresse | Rue d'OSM la plus proche | Distance | Adresse déjà dans OSM | Position |
|---|---|---|---|---|
| 66 Allée Longuépée | Chemin F.-Longuépée | 18 m |  | [carte](https://www.openstreetmap.org/?mlat=47.409146&mlon=-61.897467#map=19/47.409146/-61.897467) |
| 3 Allée de la Petite-École | Chemin Alphonse | 52 m |  | [carte](https://www.openstreetmap.org/?mlat=47.412625&mlon=-61.777329#map=19/47.412625/-61.777329) |
| 5 Allée de la Petite-École | Chemin Alphonse | 83 m |  | [carte](https://www.openstreetmap.org/?mlat=47.412574&mlon=-61.776931#map=19/47.412574/-61.776931) |
| 12 Allée du Cap-de-l'Hôpital |  |  | [node/14374934124](https://www.openstreetmap.org/node/14374934124) | [carte](https://www.openstreetmap.org/?mlat=47.418769&mlon=-61.900173#map=19/47.418769/-61.900173) |
| 26 Allée du Cap-de-l'Hôpital |  |  | [node/14374934120](https://www.openstreetmap.org/node/14374934120) | [carte](https://www.openstreetmap.org/?mlat=47.418321&mlon=-61.900766#map=19/47.418321/-61.900766) |
| 32 Allée du Cap-de-l'Hôpital |  |  | [node/14374934122](https://www.openstreetmap.org/node/14374934122) | [carte](https://www.openstreetmap.org/?mlat=47.418012&mlon=-61.900135#map=19/47.418012/-61.900135) |
| 53 Allée du Cap-de-l'Hôpital |  |  | [node/14374934121](https://www.openstreetmap.org/node/14374934121) | [carte](https://www.openstreetmap.org/?mlat=47.417534&mlon=-61.903833#map=19/47.417534/-61.903833) |
| 106 Chemin Alva-Cyr |  |  | [node/14374933498](https://www.openstreetmap.org/node/14374933498) | [carte](https://www.openstreetmap.org/?mlat=47.398949&mlon=-61.856448#map=19/47.398949/-61.856448) |
| 173 Chemin Delaney |  |  |  | [carte](https://www.openstreetmap.org/?mlat=47.363909&mlon=-61.963651#map=19/47.363909/-61.963651) |
| 185 Chemin Delaney |  |  |  | [carte](https://www.openstreetmap.org/?mlat=47.363909&mlon=-61.963651#map=19/47.363909/-61.963651) |
| 550 Chemin Julien | Chemin Petitpas | 272 m | [node/14374960601](https://www.openstreetmap.org/node/14374960601) | [carte](https://www.openstreetmap.org/?mlat=47.381188&mlon=-61.876097#map=19/47.381188/-61.876097) |
| 45 Chemin Poirier |  |  |  | [carte](https://www.openstreetmap.org/?mlat=47.415610&mlon=-61.808869#map=19/47.415610/-61.808869) |
| 19 Chemin Renaud | Chemin du Mât | 192 m | [node/14374965282](https://www.openstreetmap.org/node/14374965282) | [carte](https://www.openstreetmap.org/?mlat=47.214984&mlon=-61.954577#map=19/47.214984/-61.954577) |
| 87 Chemin Renaud |  |  | [node/14374964457](https://www.openstreetmap.org/node/14374964457) | [carte](https://www.openstreetmap.org/?mlat=47.213316&mlon=-61.957642#map=19/47.213316/-61.957642) |
| 208 Chemin Wide |  |  | [node/14355484253](https://www.openstreetmap.org/node/14355484253) | [carte](https://www.openstreetmap.org/?mlat=47.613731&mlon=-61.522641#map=19/47.613731/-61.522641) |
| 1034 Chemin de La Vernière | Chemin de la Mine | 239 m | [node/14374961907](https://www.openstreetmap.org/node/14374961907) | [carte](https://www.openstreetmap.org/?mlat=47.374430&mlon=-61.885820#map=19/47.374430/-61.885820) |
| 1190 Chemin de La Vernière |  |  | [node/14374961909](https://www.openstreetmap.org/node/14374961909) | [carte](https://www.openstreetmap.org/?mlat=47.376147&mlon=-61.897761#map=19/47.376147/-61.897761) |
| 1331 Chemin de La Vernière | Allée Léger-Bourque | 280 m | [node/14397155472](https://www.openstreetmap.org/node/14397155472) | [carte](https://www.openstreetmap.org/?mlat=47.367504&mlon=-61.907751#map=19/47.367504/-61.907751) |
| 1355 Chemin de La Vernière | Chemin de La Martinique | 256 m | [node/14397155485](https://www.openstreetmap.org/node/14397155485) | [carte](https://www.openstreetmap.org/?mlat=47.368951&mlon=-61.911221#map=19/47.368951/-61.911221) |
| 1395 Chemin de La Vernière | Chemin de La Martinique | 93 m | [node/14397155443](https://www.openstreetmap.org/node/14397155443) | [carte](https://www.openstreetmap.org/?mlat=47.369572&mlon=-61.913266#map=19/47.369572/-61.913266) |
| 1606 Chemin de l'Étang-du-Nord |  |  | [node/14374961133](https://www.openstreetmap.org/node/14374961133) | [carte](https://www.openstreetmap.org/?mlat=47.377119&mlon=-61.928808#map=19/47.377119/-61.928808) |
| 1701 Chemin de l'Étang-du-Nord |  |  | [node/14374962476](https://www.openstreetmap.org/node/14374962476) | [carte](https://www.openstreetmap.org/?mlat=47.370091&mlon=-61.938340#map=19/47.370091/-61.938340) |
| 210 Chemin de la Baie |  |  | [node/14374965383](https://www.openstreetmap.org/node/14374965383) | [carte](https://www.openstreetmap.org/?mlat=47.232834&mlon=-61.879435#map=19/47.232834/-61.879435) |
| 228 Chemin de la Baie |  |  | [node/14374965350](https://www.openstreetmap.org/node/14374965350) | [carte](https://www.openstreetmap.org/?mlat=47.232867&mlon=-61.881392#map=19/47.232867/-61.881392) |
| 126 Chemin de la Belle-Anse |  |  | [node/14374976752](https://www.openstreetmap.org/node/14374976752) | [carte](https://www.openstreetmap.org/?mlat=47.399921&mlon=-61.931763#map=19/47.399921/-61.931763) |
| 148 Chemin de la Belle-Anse |  |  | [node/14374976721](https://www.openstreetmap.org/node/14374976721) | [carte](https://www.openstreetmap.org/?mlat=47.400198&mlon=-61.933451#map=19/47.400198/-61.933451) |
| 150 Chemin de la Belle-Anse |  |  | [node/14374976722](https://www.openstreetmap.org/node/14374976722) | [carte](https://www.openstreetmap.org/?mlat=47.400867&mlon=-61.935370#map=19/47.400867/-61.935370) |
| 156 Chemin de la Belle-Anse |  |  | [node/14374976739](https://www.openstreetmap.org/node/14374976739) | [carte](https://www.openstreetmap.org/?mlat=47.401455&mlon=-61.933203#map=19/47.401455/-61.933203) |
| 158 Chemin de la Belle-Anse |  |  | [node/14374976745](https://www.openstreetmap.org/node/14374976745) | [carte](https://www.openstreetmap.org/?mlat=47.401079&mlon=-61.932426#map=19/47.401079/-61.932426) |
| 162 Chemin de la Belle-Anse |  |  | [node/14397155460](https://www.openstreetmap.org/node/14397155460) | [carte](https://www.openstreetmap.org/?mlat=47.403033&mlon=-61.934571#map=19/47.403033/-61.934571) |
| 168 Chemin de la Belle-Anse |  |  | [node/14397155459](https://www.openstreetmap.org/node/14397155459) | [carte](https://www.openstreetmap.org/?mlat=47.402998&mlon=-61.930994#map=19/47.402998/-61.930994) |
| 172 Chemin de la Belle-Anse |  |  | [node/14381000192](https://www.openstreetmap.org/node/14381000192) | [carte](https://www.openstreetmap.org/?mlat=47.405236&mlon=-61.931143#map=19/47.405236/-61.931143) |
| 150 Chemin de la Dune-du-Sud | Allée des Collines | 157 m | [node/14374934755](https://www.openstreetmap.org/node/14374934755) | [carte](https://www.openstreetmap.org/?mlat=47.408865&mlon=-61.768427#map=19/47.408865/-61.768427) |
| 271 Chemin de la Pointe-Basse | Chemin des Turbide | 205 m | [node/14374935163](https://www.openstreetmap.org/node/14374935163) | [carte](https://www.openstreetmap.org/?mlat=47.396464&mlon=-61.793334#map=19/47.396464/-61.793334) |
| 46 Chemin des Arpenteurs |  |  | [node/14374964542](https://www.openstreetmap.org/node/14374964542) | [carte](https://www.openstreetmap.org/?mlat=47.234565&mlon=-62.010332#map=19/47.234565/-62.010332) |
| 845 Chemin des Caps | Allée des Puits | 141 m | [node/14374934343](https://www.openstreetmap.org/node/14374934343) | [carte](https://www.openstreetmap.org/?mlat=47.396911&mlon=-61.904022#map=19/47.396911/-61.904022) |
| 927 Chemin des Caps |  |  | [node/14374962416](https://www.openstreetmap.org/node/14374962416) | [carte](https://www.openstreetmap.org/?mlat=47.394061&mlon=-61.911684#map=19/47.394061/-61.911684) |
| 1388 Chemin des Caps |  |  | [node/14374962060](https://www.openstreetmap.org/node/14374962060) | [carte](https://www.openstreetmap.org/?mlat=47.388400&mlon=-61.949867#map=19/47.388400/-61.949867) |
| 1431 Chemin des Caps | Allée Michel-Vigneau | 234 m | [node/14374961157](https://www.openstreetmap.org/node/14374961157) | [carte](https://www.openstreetmap.org/?mlat=47.387279&mlon=-61.940163#map=19/47.387279/-61.940163) |
| 83 Chemin des Patton | Le Lac | 207 m | [node/14374934255](https://www.openstreetmap.org/node/14374934255) | [carte](https://www.openstreetmap.org/?mlat=47.383444&mlon=-61.884312#map=19/47.383444/-61.884312) |
| 41 Chemin des Pealey | Sentier Ile Boudreau | 151 m | [node/14374932122](https://www.openstreetmap.org/node/14374932122) | [carte](https://www.openstreetmap.org/?mlat=47.547532&mlon=-61.549769#map=19/47.547532/-61.549769) |
| 279 Chemin du Bassin |  |  | [node/14391904604](https://www.openstreetmap.org/node/14391904604) | [carte](https://www.openstreetmap.org/?mlat=47.232479&mlon=-61.908286#map=19/47.232479/-61.908286) |
| 231 Chemin du Cap-Rouge |  |  | [node/14374933598](https://www.openstreetmap.org/node/14374933598) | [carte](https://www.openstreetmap.org/?mlat=47.413469&mlon=-61.810167#map=19/47.413469/-61.810167) |
| 949 Chemin du Gros-Cap |  |  | [node/14391904577](https://www.openstreetmap.org/node/14391904577) | [carte](https://www.openstreetmap.org/?mlat=47.363500&mlon=-61.900050#map=19/47.363500/-61.900050) |
| 42 Chemin du Mât | Chemin du Moulin | 162 m | [node/14391904606](https://www.openstreetmap.org/node/14391904606) | [carte](https://www.openstreetmap.org/?mlat=47.214906&mlon=-61.951496#map=19/47.214906/-61.951496) |
| 25 Route 199 | Sentier Seacow | 16 m |  | [carte](https://www.openstreetmap.org/?mlat=47.566341&mlon=-61.495363#map=19/47.566341/-61.495363) |
| 215 Route 199 | Chemin du Cap-Rouge | 292 m | [node/14391780786](https://www.openstreetmap.org/node/14391780786) | [carte](https://www.openstreetmap.org/?mlat=47.402830&mlon=-61.823299#map=19/47.402830/-61.823299) |
| 219 Route 199 |  |  | [node/14374933654](https://www.openstreetmap.org/node/14374933654) | [carte](https://www.openstreetmap.org/?mlat=47.403338&mlon=-61.822979#map=19/47.403338/-61.822979) |
| 330 Route 199 | Allée du Bas-de-la-Baie | 41 m | [node/14374964644](https://www.openstreetmap.org/node/14374964644) | [carte](https://www.openstreetmap.org/?mlat=47.236162&mlon=-61.888667#map=19/47.236162/-61.888667) |
| 1155 Route 199 | Sentier du parc des Sillons | 121 m | [node/14397155487](https://www.openstreetmap.org/node/14397155487) | [carte](https://www.openstreetmap.org/?mlat=47.427219&mlon=-61.762777#map=19/47.427219/-61.762777) |
| 1310 Route 199 |  |  |  | [carte](https://www.openstreetmap.org/?mlat=47.457390&mlon=-61.755407#map=19/47.457390/-61.755407) |
| 1340 Route 199 |  |  |  | [carte](https://www.openstreetmap.org/?mlat=47.457390&mlon=-61.755407#map=19/47.457390/-61.755407) |

## Adresses d'OSM sans pendant au RQA (243)

Adresses d'OSM près du lieu qu'aucune adresse du RQA ne retrouve : ajoutées d'une autre source, ou au numéro ou à la rue écrits autrement.

| Objet | Numéro | Rue | addr:city |
|---|---|---|---|
| [node/14381318642](https://www.openstreetmap.org/node/14381318642) | 8B | Allée Conrad-Miousse | L'Étang-du-Nord |
| [node/14381191147](https://www.openstreetmap.org/node/14381191147) | 8 | Allée Cummings | Fatima |
| [node/14381191148](https://www.openstreetmap.org/node/14381191148) | 10 | Allée Cummings | Fatima |
| [node/14374933756](https://www.openstreetmap.org/node/14374933756) | 4 | Allée Joseph-Déraspe | Fatima |
| [node/14383671709](https://www.openstreetmap.org/node/14383671709) | 1B | Allée Longuépée | Fatima |
| [node/14391780800](https://www.openstreetmap.org/node/14391780800) | 12 | Allée Nelson-Renaud | Les Îles-de-la-Madeleine |
| [node/14391904502](https://www.openstreetmap.org/node/14391904502) | 26A;26B | Allée Robert-Vigneau | L'Étang-du-Nord |
| [node/14381318640](https://www.openstreetmap.org/node/14381318640) | 340A;340B | Chemin Arsenault | Cap-aux-Meules |
| [node/14374967416](https://www.openstreetmap.org/node/14374967416) | 124 | Chemin Big Hill | L'Île-d'Entrée |
| [node/14381318688](https://www.openstreetmap.org/node/14381318688) | 51B | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/14381318646](https://www.openstreetmap.org/node/14381318646) | 71A;71B | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/14381343504](https://www.openstreetmap.org/node/14381343504) | 147A | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/14381318638](https://www.openstreetmap.org/node/14381318638) | 224A | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/14381343502](https://www.openstreetmap.org/node/14381343502) | 415B | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/11114751396](https://www.openstreetmap.org/node/11114751396) | 499 | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/14392246723](https://www.openstreetmap.org/node/14392246723) | 499 | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/14392246724](https://www.openstreetmap.org/node/14392246724) | 510 | Chemin Boisville Ouest | L'Étang-du-Nord |
| [node/14384500755](https://www.openstreetmap.org/node/14384500755) | 260;260B | Chemin Boudreau | Cap-aux-Meules |
| [node/14381318674](https://www.openstreetmap.org/node/14381318674) | 57B | Chemin Bourgeois | Fatima |
| [node/9374924071](https://www.openstreetmap.org/node/9374924071) | 37 | Chemin Central | Havre-aux-Maisons |
| [node/14395203828](https://www.openstreetmap.org/node/14395203828) | 37 | Chemin Central | Havre-aux-Maisons |
| [node/14395203827](https://www.openstreetmap.org/node/14395203827) | 38 | Chemin Central | Havre-aux-Maisons |
| [node/14391780791](https://www.openstreetmap.org/node/14391780791) | 736A | Chemin Cormier | Cap-aux-Meules |
| [node/14391780792](https://www.openstreetmap.org/node/14391780792) | 736B | Chemin Cormier | Cap-aux-Meules |
| [node/6103879686](https://www.openstreetmap.org/node/6103879686) | 286 | Chemin Coulombe | L'Étang-du-Nord |
| [node/14391864580](https://www.openstreetmap.org/node/14391864580) | 286 | Chemin Coulombe | L'Étang-du-Nord |
| [node/14391780789](https://www.openstreetmap.org/node/14391780789) | 41A;41B | Chemin Edgar-Thorne | Fatima |
| [node/14393674146](https://www.openstreetmap.org/node/14393674146) | 4 | Chemin Ernest | Fatima |
| [way/1184851156](https://www.openstreetmap.org/way/1184851156) | 112 | Chemin F- Longuépée | Fatima |
| [node/14381318630](https://www.openstreetmap.org/node/14381318630) | 32B | Chemin Garneau | L'Étang-du-Nord |
| [node/10603916966](https://www.openstreetmap.org/node/10603916966) | 6 | Chemin Jerry | Grosse-Île |
| [node/14355480208](https://www.openstreetmap.org/node/14355480208) | 6 | Chemin Jerry | Grosse-Île |
| [node/14374934633](https://www.openstreetmap.org/node/14374934633) | 115 | Chemin John-Aucoin | Fatima |
| [node/14381318652](https://www.openstreetmap.org/node/14381318652) | 341B | Chemin Julien | Cap-aux-Meules |
| [node/14381343512](https://www.openstreetmap.org/node/14381343512) | 27B | Chemin Langford | Havre-aux-Maisons |
| [node/14381318624](https://www.openstreetmap.org/node/14381318624) | 280A | Chemin Lapierre | Fatima |
| [node/14381318662](https://www.openstreetmap.org/node/14381318662) | 31A;31B | Chemin Le Pré | L'Étang-du-Nord |
| [node/14381318644](https://www.openstreetmap.org/node/14381318644) | 103A | Chemin Le Pré | L'Étang-du-Nord |
| [node/14381000220](https://www.openstreetmap.org/node/14381000220) | 2 | Chemin Main | L'Île-d'Entrée |
| [node/14381343514](https://www.openstreetmap.org/node/14381343514) | 166B;166C | Chemin Martinet | Havre-Aubert |
| [node/14356684351](https://www.openstreetmap.org/node/14356684351) | 38 | Chemin Park | Grosse-Île |
| [node/14356684352](https://www.openstreetmap.org/node/14356684352) | 38 | Chemin Park | Grosse-Île |
| [node/14392823706](https://www.openstreetmap.org/node/14392823706) | 355 | Chemin Petitpas | Cap-aux-Meules |
| [node/14381343506](https://www.openstreetmap.org/node/14381343506) | 15A;15B | Chemin Philippe-Thorne | Fatima |
| [node/14392965200](https://www.openstreetmap.org/node/14392965200) | 40 | Chemin Principal | Cap-aux-Meules |
| [node/14381000291](https://www.openstreetmap.org/node/14381000291) | 40A | Chemin Principal | Cap-aux-Meules |
| [node/10603917255](https://www.openstreetmap.org/node/10603917255) | 50 | Chemin Principal | Grosse-Île |
| [node/14355383058](https://www.openstreetmap.org/node/14355383058) | 50 | Chemin Principal | Grosse-Île |
| [node/14356953612](https://www.openstreetmap.org/node/14356953612) | 56 | Chemin Principal | Grosse-Île |
| [node/14355484222](https://www.openstreetmap.org/node/14355484222) | 110 | Chemin Principal | Grosse-Île |
| [node/11015020717](https://www.openstreetmap.org/node/11015020717) | 166 | Chemin Principal | Grosse-Île |
| [node/14355484243](https://www.openstreetmap.org/node/14355484243) | 166 | Chemin Principal | Grosse-Île |
| [node/14374961658](https://www.openstreetmap.org/node/14374961658) | 169 | Chemin Principal | Cap-aux-Meules |
| [node/14374960596](https://www.openstreetmap.org/node/14374960596) | 181 | Chemin Principal | Cap-aux-Meules |
| [node/14392637053](https://www.openstreetmap.org/node/14392637053) | 185 | Chemin Principal | Cap-aux-Meules |
| [node/14381000147](https://www.openstreetmap.org/node/14381000147) | 185;185B | Chemin Principal | Cap-aux-Meules |
| [node/14384529512](https://www.openstreetmap.org/node/14384529512) | 198 | Chemin Principal | Cap-aux-Meules |
| [node/14374961653](https://www.openstreetmap.org/node/14374961653) | 205 | Chemin Principal | Cap-aux-Meules |
| [node/14391780793](https://www.openstreetmap.org/node/14391780793) | 206A;206B | Chemin Principal | Cap-aux-Meules |
| [node/14374961668](https://www.openstreetmap.org/node/14374961668) | 221 | Chemin Principal | Cap-aux-Meules |
| [node/14381318648](https://www.openstreetmap.org/node/14381318648) | 224B | Chemin Principal | Cap-aux-Meules |
| [node/14381000145](https://www.openstreetmap.org/node/14381000145) | 225;225A;225B;225C;225D;225E;225F | Chemin Principal | Cap-aux-Meules |
| [node/14374961619](https://www.openstreetmap.org/node/14374961619) | 236 | Chemin Principal | Cap-aux-Meules |
| [node/14374961618](https://www.openstreetmap.org/node/14374961618) | 248 | Chemin Principal | Cap-aux-Meules |
| [node/14392839610](https://www.openstreetmap.org/node/14392839610) | 260 | Chemin Principal | Cap-aux-Meules |
| [node/14374961638](https://www.openstreetmap.org/node/14374961638) | 280 | Chemin Principal | Cap-aux-Meules |
| [node/11191538621](https://www.openstreetmap.org/node/11191538621) | 325 | Chemin Principal | Cap-aux-Meules |
| [node/14384529511](https://www.openstreetmap.org/node/14384529511) | 351 | Chemin Principal | Cap-aux-Meules |
| [node/14384529510](https://www.openstreetmap.org/node/14384529510) | 368 | Chemin Principal | Cap-aux-Meules |
| [node/6452023087](https://www.openstreetmap.org/node/6452023087) | 380 | Chemin Principal | Cap-aux-Meules |
| [node/13056479200](https://www.openstreetmap.org/node/13056479200) | 380 | Chemin Principal | Cap-aux-Meules |
| [node/14392637052](https://www.openstreetmap.org/node/14392637052) | 380 | Chemin Principal | Cap-aux-Meules |
| [node/13056469258](https://www.openstreetmap.org/node/13056469258) | 397A | Chemin Principal | Cap-aux-Meules |
| [node/14374962270](https://www.openstreetmap.org/node/14374962270) | 405 | Chemin Principal | Cap-aux-Meules |
| [node/14381318660](https://www.openstreetmap.org/node/14381318660) | 410A;410B | Chemin Principal | Cap-aux-Meules |
| [node/14374961923](https://www.openstreetmap.org/node/14374961923) | 420 | Chemin Principal | Cap-aux-Meules |
| [node/14392797692](https://www.openstreetmap.org/node/14392797692) | 424 | Chemin Principal | Cap-aux-Meules |
| [node/14374961920](https://www.openstreetmap.org/node/14374961920) | 425 | Chemin Principal | Cap-aux-Meules |
| [node/14355330535](https://www.openstreetmap.org/node/14355330535) | 443 | Chemin Principal | Grosse-Île |
| [way/1239731222](https://www.openstreetmap.org/way/1239731222) | 443 | Chemin Principal | Grosse-Île |
| [node/14374961918](https://www.openstreetmap.org/node/14374961918) | 445 | Chemin Principal | Cap-aux-Meules |
| [node/14374961904](https://www.openstreetmap.org/node/14374961904) | 485 | Chemin Principal | Cap-aux-Meules |
| [node/14384529509](https://www.openstreetmap.org/node/14384529509) | 545 | Chemin Principal | Cap-aux-Meules |
| [node/14374961355](https://www.openstreetmap.org/node/14374961355) | 565 | Chemin Principal | Cap-aux-Meules |
| [node/14392476870](https://www.openstreetmap.org/node/14392476870) | 596 | Chemin Principal | Cap-aux-Meules |
| [node/14392611675](https://www.openstreetmap.org/node/14392611675) | 596 | Chemin Principal | Cap-aux-Meules |
| [node/14392611676](https://www.openstreetmap.org/node/14392611676) | 596 | Chemin Principal | Cap-aux-Meules |
| [node/13596727323](https://www.openstreetmap.org/node/13596727323) | 699 | Chemin Principal | Cap-aux-Meules |
| [node/14374960723](https://www.openstreetmap.org/node/14374960723) | 720 | Chemin Principal | Cap-aux-Meules |
| [node/14374961099](https://www.openstreetmap.org/node/14374961099) | 725 | Chemin Principal | Cap-aux-Meules |
| [node/14374961107](https://www.openstreetmap.org/node/14374961107) | 760 | Chemin Principal | Cap-aux-Meules |
| [node/14355311882](https://www.openstreetmap.org/node/14355311882) | 773 | Chemin Principal | Grosse-Île |
| [node/14355311884](https://www.openstreetmap.org/node/14355311884) | 787 | Chemin Principal | Grosse-Île |
| [node/14374960744](https://www.openstreetmap.org/node/14374960744) | 800 | Chemin Principal | Cap-aux-Meules |
| [node/14355311886](https://www.openstreetmap.org/node/14355311886) | 806 | Chemin Principal | Grosse-Île |
| [node/14391904504](https://www.openstreetmap.org/node/14391904504) | 60A;60B | Chemin Redger-Noël | Fatima |
| [node/14355563590](https://www.openstreetmap.org/node/14355563590) | 51 | Chemin Shore | Grosse-Île |
| [node/14381318654](https://www.openstreetmap.org/node/14381318654) | 110A | Chemin Turbide | L'Étang-du-Nord |
| [node/14381000153](https://www.openstreetmap.org/node/14381000153) | 110B | Chemin Turbide | L'Étang-du-Nord |
| [node/14381318632](https://www.openstreetmap.org/node/14381318632) | 47A;47B | Chemin Turjo | L'Étang-du-Nord |
| [node/14381000223](https://www.openstreetmap.org/node/14381000223) | 21 | Chemin Wharf | L'Île-d'Entrée |
| [node/14391904510](https://www.openstreetmap.org/node/14391904510) | 200 | Chemin d'en Haut | Les Îles-de-la-Madeleine |
| [node/14381318696](https://www.openstreetmap.org/node/14381318696) | 264A;264B | Chemin d'en Haut | Havre-Aubert |
| [node/11343980307](https://www.openstreetmap.org/node/11343980307) | 316 | Chemin d'en Haut | Havre-Aubert |
| [node/14374965076](https://www.openstreetmap.org/node/14374965076) | 404 | Chemin d'en Haut | Havre-Aubert |
| [node/11341589815](https://www.openstreetmap.org/node/11341589815) | 405 | Chemin d'en Haut | Havre-Aubert |
| [node/14381061986](https://www.openstreetmap.org/node/14381061986) | 408 | Chemin d'en Haut | Havre-Aubert |
| [node/14381318670](https://www.openstreetmap.org/node/14381318670) | 285A | Chemin de Gros-Cap | Cap-aux-Meules |
| [node/14381318672](https://www.openstreetmap.org/node/14381318672) | 315B | Chemin de Gros-Cap | Cap-aux-Meules |
| [node/14381318690](https://www.openstreetmap.org/node/14381318690) | 895A | Chemin de La Grave | Havre-Aubert |
| [node/14374965518](https://www.openstreetmap.org/node/14374965518) | 995 | Chemin de La Grave | Havre-Aubert |
| [node/13048903937](https://www.openstreetmap.org/node/13048903937) | 996 | Chemin de La Grave | Havre-Aubert |
| [node/14389111296](https://www.openstreetmap.org/node/14389111296) | 996 | Chemin de La Grave | Havre-Aubert |
| [node/14389111297](https://www.openstreetmap.org/node/14389111297) | 996 | Chemin de La Grave | Havre-Aubert |
| [node/14391555655](https://www.openstreetmap.org/node/14391555655) | 1023 | Chemin de La Grave | Havre-Aubert |
| [node/11132381275](https://www.openstreetmap.org/node/11132381275) | 30 | Chemin de La Martinique | L'Étang-du-Nord |
| [node/11132381278](https://www.openstreetmap.org/node/11132381278) | 30 | Chemin de La Martinique | L'Étang-du-Nord |
| [node/11132405062](https://www.openstreetmap.org/node/11132405062) | 30 | Chemin de La Martinique | L'Étang-du-Nord |
| [node/13449245395](https://www.openstreetmap.org/node/13449245395) | 50 | Chemin de La Martinique | L'Étang-du-Nord |
| [node/14392217786](https://www.openstreetmap.org/node/14392217786) | 60 | Chemin de La Martinique | L'Étang-du-Nord |
| [node/14381318628](https://www.openstreetmap.org/node/14381318628) | 179A | Chemin de La Martinique | L'Étang-du-Nord |
| [node/11198051764](https://www.openstreetmap.org/node/11198051764) | 1011 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14392420073](https://www.openstreetmap.org/node/14392420073) | 1011 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14392420074](https://www.openstreetmap.org/node/14392420074) | 1011 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14392420075](https://www.openstreetmap.org/node/14392420075) | 1011 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14392462098](https://www.openstreetmap.org/node/14392462098) | 1073 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14391904515](https://www.openstreetmap.org/node/14391904515) | 1090 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14374961540](https://www.openstreetmap.org/node/14374961540) | 1244 | Chemin de La Vernière | L'Étang-du-Nord |
| [way/1016434385](https://www.openstreetmap.org/way/1016434385) | 1316 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/10179126593](https://www.openstreetmap.org/node/10179126593) | 1401 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14392257428](https://www.openstreetmap.org/node/14392257428) | 1401 | Chemin de La Vernière | L'Étang-du-Nord |
| [node/14384988605](https://www.openstreetmap.org/node/14384988605) | 188 | Chemin de l'Aéroport | Havre-aux-maisons |
| [node/14374934748](https://www.openstreetmap.org/node/14374934748) | 205 | Chemin de l'Aéroport | Havre-aux-Maisons |
| [way/1214139887](https://www.openstreetmap.org/way/1214139887) | 147 | Chemin de l'Hôpital | Fatima |
| [node/14383784021](https://www.openstreetmap.org/node/14383784021) | 148 | Chemin de l'Hôpital | Fatima |
| [node/14374934123](https://www.openstreetmap.org/node/14374934123) | 152 | Chemin de l'Hôpital | Fatima |
| [node/11343828324](https://www.openstreetmap.org/node/11343828324) | 28 | Chemin de l'École | Havre-Aubert |
| [node/11343828347](https://www.openstreetmap.org/node/11343828347) | 32 | Chemin de l'École | Havre-Aubert |
| [way/1425970830](https://www.openstreetmap.org/way/1425970830) | 7 | Chemin de l'Église | Les Îles-de-la-Madeleine |
| [node/14381318626](https://www.openstreetmap.org/node/14381318626) | 50B;50C | Chemin de l'Église | L'Étang-du-Nord |
| [node/14381318636](https://www.openstreetmap.org/node/14381318636) | 1791A | Chemin de l'Étang-du-Nord | L'Étang-du-Nord |
| [node/14392246727](https://www.openstreetmap.org/node/14392246727) | 1912 | Chemin de l'Étang-du-Nord | L'Étang-du-Nord |
| [node/14381318656](https://www.openstreetmap.org/node/14381318656) | 58A;58B | Chemin de l'Éveil | Fatima |
| [way/698817268](https://www.openstreetmap.org/way/698817268) | 187 | Chemin de la Dune du Sud | Les Îles-de-la-Madeleine |
| [node/14374935199](https://www.openstreetmap.org/node/14374935199) | 430 | Chemin de la Dune-du-Sud | Havre-aux-Maisons |
| [node/14374935200](https://www.openstreetmap.org/node/14374935200) | 436 | Chemin de la Dune-du-Sud | Havre-aux-Maisons |
| [node/14374960719](https://www.openstreetmap.org/node/14374960719) | 225 | Chemin de la Grande-Allée | Cap-aux-Meules |
| [node/14381343516](https://www.openstreetmap.org/node/14381343516) | 442A;442B | Chemin de la Mine | Cap-aux-Meules |
| [node/14392217788](https://www.openstreetmap.org/node/14392217788) | 15 | Chemin de la Piscine | L'Étang-du-Nord |
| [node/14392234650](https://www.openstreetmap.org/node/14392234650) | 25 | Chemin de la Piscine | L'Étang-du-Nord |
| [node/14392234651](https://www.openstreetmap.org/node/14392234651) | 25 | Chemin de la Piscine | L'Étang-du-Nord |
| [node/14381318680](https://www.openstreetmap.org/node/14381318680) | 133B | Chemin de la Pointe-Basse | Havre-aux-Maisons |
| [node/14374935284](https://www.openstreetmap.org/node/14374935284) | 149 | Chemin de la Pointe-Basse | Havre-aux-Maisons |
| [node/14381343508](https://www.openstreetmap.org/node/14381343508) | 99B | Chemin des Buttes | Havre-aux-Maisons |
| [node/14397155411](https://www.openstreetmap.org/node/14397155411) | 321 | Chemin des Buttes | Havre-aux-Maisons |
| [node/14395889102](https://www.openstreetmap.org/node/14395889102) | 608 | Chemin des Caps | Fatima |
| [node/14395889101](https://www.openstreetmap.org/node/14395889101) | 615 | Chemin des Caps | Fatima |
| [node/14374933424](https://www.openstreetmap.org/node/14374933424) | 623 | Chemin des Caps | Fatima |
| [node/14374933418](https://www.openstreetmap.org/node/14374933418) | 634 | Chemin des Caps | Fatima |
| [node/14381318622](https://www.openstreetmap.org/node/14381318622) | 729A | Chemin des Caps | Fatima |
| [node/14381318684](https://www.openstreetmap.org/node/14381318684) | 795B | Chemin des Caps | Fatima |
| [node/14381318676](https://www.openstreetmap.org/node/14381318676) | 1062A | Chemin des Caps | Fatima |
| [node/14381318678](https://www.openstreetmap.org/node/14381318678) | 1184A;1184B;1184C | Chemin des Caps | Fatima |
| [node/14393309390](https://www.openstreetmap.org/node/14393309390) | 1300 | Chemin des Caps | Fatima |
| [node/14393309391](https://www.openstreetmap.org/node/14393309391) | 1300 | Chemin des Caps | Fatima |
| [node/14393309392](https://www.openstreetmap.org/node/14393309392) | 1300 | Chemin des Caps | Fatima |
| [node/14393309393](https://www.openstreetmap.org/node/14393309393) | 1300 | Chemin des Caps | Fatima |
| [node/14393309394](https://www.openstreetmap.org/node/14393309394) | 1300 | Chemin des Caps | Fatima |
| [node/14393309395](https://www.openstreetmap.org/node/14393309395) | 1300 | Chemin des Caps | Fatima |
| [node/14397155403](https://www.openstreetmap.org/node/14397155403) | 139 | Chemin des Patton | Fatima |
| [node/14381343510](https://www.openstreetmap.org/node/14381343510) | 19B | Chemin des Turbide | Havre-aux-Maisons |
| [node/14381318698](https://www.openstreetmap.org/node/14381318698) | 76A;76B;76C | Chemin du Bassin | Havre-Aubert |
| [node/14391056823](https://www.openstreetmap.org/node/14391056823) | 280 | Chemin du Bassin | Bassin |
| [node/14391056824](https://www.openstreetmap.org/node/14391056824) | 280 | Chemin du Bassin | Bassin |
| [way/1425970829](https://www.openstreetmap.org/way/1425970829) | 280 | Chemin du Bassin | Les Îles-de-la-Madeleine |
| [node/14391183523](https://www.openstreetmap.org/node/14391183523) | 445 | Chemin du Bassin | Bassin |
| [node/14391062914](https://www.openstreetmap.org/node/14391062914) | 489 | Chemin du Bassin | Bassin |
| [node/14381318692](https://www.openstreetmap.org/node/14381318692) | 493A;493B;493C | Chemin du Bassin | Bassin |
| [node/14389086227](https://www.openstreetmap.org/node/14389086227) | 574 | Chemin du Bassin | L'Île-du-Havre-Aubert |
| [node/14389086225](https://www.openstreetmap.org/node/14389086225) | 588 | Chemin du Bassin | Bassin |
| [node/14389336931](https://www.openstreetmap.org/node/14389336931) | 788 | Chemin du Bassin | Bassin |
| [node/14381318700](https://www.openstreetmap.org/node/14381318700) | 796A | Chemin du Bassin | Bassin |
| [node/14389336929](https://www.openstreetmap.org/node/14389336929) | 828 | Chemin du Bassin | Bassin |
| [node/14389336930](https://www.openstreetmap.org/node/14389336930) | 833 | Chemin du Bassin | Bassin |
| [node/14389336923](https://www.openstreetmap.org/node/14389336923) | 866 | Chemin du Bassin | Bassin |
| [node/14391904543](https://www.openstreetmap.org/node/14391904543) | 1191 | Chemin du Bassin | Les Îles-de-la-Madeleine |
| [node/14381318682](https://www.openstreetmap.org/node/14381318682) | 1254B | Chemin du Bassin | Bassin |
| [node/14391842380](https://www.openstreetmap.org/node/14391842380) | 74 | Chemin du Camping | L'Étang-du-Nord |
| [node/14391842381](https://www.openstreetmap.org/node/14391842381) | 74 | Chemin du Camping | L'Étang-du-Nord |
| [node/14391842382](https://www.openstreetmap.org/node/14391842382) | 74 | Chemin du Camping | L'Étang-du-Nord |
| [node/14391842383](https://www.openstreetmap.org/node/14391842383) | 74 | Chemin du Camping | L'Étang-du-Nord |
| [node/14391780775](https://www.openstreetmap.org/node/14391780775) | 226A;226B;226C;226D | Chemin du Cap-Rouge | Havre-aux-Maisons |
| [node/14396141587](https://www.openstreetmap.org/node/14396141587) | 475 | Chemin du Cap-Rouge | Havre-aux-Maisons |
| [node/14381000201](https://www.openstreetmap.org/node/14381000201) | 475B | Chemin du Cap-Rouge | Havre-aux-Maisons |
| [node/14392855059](https://www.openstreetmap.org/node/14392855059) | 70 | Chemin du Débarcadère | Cap-aux-Meules |
| [node/14397155401](https://www.openstreetmap.org/node/14397155401) | 946 | Chemin du Grand-Ruisseau | Les Îles-de-la-Madeleine |
| [node/14374933662](https://www.openstreetmap.org/node/14374933662) | 984 | Chemin du Grand-Ruisseau | Fatima |
| [node/14381318668](https://www.openstreetmap.org/node/14381318668) | 1039A | Chemin du Grand-Ruisseau | Fatima |
| [node/14381318634](https://www.openstreetmap.org/node/14381318634) | 1102A;1102B | Chemin du Grand-Ruisseau | Fatima |
| [way/1016434359](https://www.openstreetmap.org/way/1016434359) | 70 | Chemin du Gros Cap | Les Îles-de-la-Madeleine |
| [node/14391904501](https://www.openstreetmap.org/node/14391904501) | 390 | Chemin du Gros-Cap | L'Étang-du-Nord |
| [node/14374961583](https://www.openstreetmap.org/node/14374961583) | 547 | Chemin du Gros-Cap | L'Étang-du-Nord |
| [node/14381318664](https://www.openstreetmap.org/node/14381318664) | 800B | Chemin du Gros-Cap | L'Étang-du-Nord |
| [node/14381318666](https://www.openstreetmap.org/node/14381318666) | 806B | Chemin du Gros-Cap | L'Étang-du-Nord |
| [node/14374961536](https://www.openstreetmap.org/node/14374961536) | 1069 | Chemin du Gros-Cap | L'Étang-du-Nord |
| [node/14381318650](https://www.openstreetmap.org/node/14381318650) | 10A;10B | Chemin du Marché | Cap-aux-Meules |
| [node/14392709193](https://www.openstreetmap.org/node/14392709193) | 75 | Chemin du Parc | Cap-aux-Meules |
| [node/4356728171](https://www.openstreetmap.org/node/4356728171) | 127 | Chemin du Parc | Cap-aux-Meules |
| [node/14393284258](https://www.openstreetmap.org/node/14393284258) | 26 | Chemin du Quai | Havre-aux-Maisons |
| [node/14374934827](https://www.openstreetmap.org/node/14374934827) | 27 | Chemin du Quai | Havre-aux-Maisons |
| [node/14384529513](https://www.openstreetmap.org/node/14384529513) | 360 | Chemin du Quai | Cap-aux-Meules |
| [node/14383773839](https://www.openstreetmap.org/node/14383773839) | 61 | Chemin du Rivage | Fatima |
| [node/14383773838](https://www.openstreetmap.org/node/14383773838) | 63 | Chemin du Rivage | Fatima |
| [node/14383773837](https://www.openstreetmap.org/node/14383773837) | 65 | Chemin du Rivage | Fatima |
| [node/14383773819](https://www.openstreetmap.org/node/14383773819) | 67 | Chemin du Rivage | Fatima |
| [node/14383773820](https://www.openstreetmap.org/node/14383773820) | 67 | Chemin du Rivage | Fatima |
| [node/14383728941](https://www.openstreetmap.org/node/14383728941) | 87 | Chemin du Rivage | Fatima |
| [node/14381318658](https://www.openstreetmap.org/node/14381318658) | 239A | Chemin Éloquin | Fatima |
| [node/14374932241](https://www.openstreetmap.org/node/14374932241) | 25 | Route 199 | Grande-Entrée |
| [node/14381000127](https://www.openstreetmap.org/node/14381000127) | 86;86B | Route 199 | Havre-aux-Maisons |
| [node/14374933763](https://www.openstreetmap.org/node/14374933763) | 90 | Route 199 | Havre-aux-Maisons |
| [node/14397155405](https://www.openstreetmap.org/node/14397155405) | 106 | Route 199 | Les Îles-de-la-Madeleine |
| [node/14393348565](https://www.openstreetmap.org/node/14393348565) | 156 | Route 199 | Fatima |
| [node/14374932105](https://www.openstreetmap.org/node/14374932105) | 214 | Route 199 | Grande-Entrée |
| [node/11413591130](https://www.openstreetmap.org/node/11413591130) | 251 | Route 199 | Havre-aux-Maisons |
| [node/14381318685](https://www.openstreetmap.org/node/14381318685) | 251 | Route 199 | Havre-aux-Maisons |
| [node/14381318686](https://www.openstreetmap.org/node/14381318686) | 251A | Route 199 | Havre-aux-Maisons |
| [node/14381000185](https://www.openstreetmap.org/node/14381000185) | 255A;255B | Route 199 | Havre-Aubert |
| [node/14393356403](https://www.openstreetmap.org/node/14393356403) | 257 | Route 199 | Havre-aux-Maisons |
| [node/14393335475](https://www.openstreetmap.org/node/14393335475) | 319 | Route 199 | Havre-aux-Maisons |
| [node/11010347432](https://www.openstreetmap.org/node/11010347432) | 323 | Route 199 | Fatima |
| [node/14393301850](https://www.openstreetmap.org/node/14393301850) | 323 | Route 199 | Fatima |
| [node/14397004217](https://www.openstreetmap.org/node/14397004217) | 399 | Route 199 | Grande-Entrée |
| [node/14374935379](https://www.openstreetmap.org/node/14374935379) | 415 | Route 199 | Fatima |
| [node/14398214972](https://www.openstreetmap.org/node/14398214972) | 590 | Route 199 | Grande-Entrée |
| [node/14381318694](https://www.openstreetmap.org/node/14381318694) | 701A | Route 199 | Havre-Aubert |
| [node/14374932166](https://www.openstreetmap.org/node/14374932166) | 709 | Route 199 | Grande-Entrée |
| [node/14381343518](https://www.openstreetmap.org/node/14381343518) | 833A | Route 199 | Havre-Aubert |
| [node/14374932225](https://www.openstreetmap.org/node/14374932225) | 897 | Route 199 | Grande-Entrée |
| [node/14396811879](https://www.openstreetmap.org/node/14396811879) | 898 | Route 199 | Grande-Entrée |
| [node/14397155410](https://www.openstreetmap.org/node/14397155410) | 1234B | Route 199 | Havre-aux-Maisons |
| [node/14374935386](https://www.openstreetmap.org/node/14374935386) | 1340 | Route 199 | Havre-aux-Maisons |
| [node/14396797047](https://www.openstreetmap.org/node/14396797047) | 1757 | Route 199 | Pointe-aux-Loups |

## Non certifiées au RQA (3)

- 0 Chemin Big Hill : non certifiée
- 0 Chemin Head : non certifiée
- 0 Chemin Main : non certifiée
