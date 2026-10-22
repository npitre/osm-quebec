# Inventaire des limites municipales du Québec

Chaque municipalité des Découpages administratifs du MRNF (table `munic_s`), sa relation d'OSM (`ref:qc`, niveau 8), le nombre de sommets de son tracé officiel et de nœuds de sa relation actuelle, et une estimation des objets à envoyer pour la remplacer. Produit par `outils/inventaire.py`; détail par municipalité dans [inventaire.csv](inventaire.csv).

Estimation : sommets du MRNF à créer, plus nœuds des simples lignes de limite d'OSM à supprimer; un sommet ou un nœud commun à deux municipalités compte pour moitié à chacune. Les routes à couper ne sont pas comptées (environ 5 % de plus dans la Petite-Nation). Un groupe de modifications d'OSM accepte au plus 10 000 objets.

| Municipalités du MRNF | Dans OSM | Sommets du MRNF | Nœuds dans OSM | Objets estimés | Envois de 9 000 objets, au moins |
|---|---|---|---|---|---|
| 1340 | 1239 | 2 207 343 | 709 624 | 1 351 829 | 151 |

## Par région

| Région | Municipalités | Dans OSM | MRC | Sommets du MRNF | Nœuds dans OSM | Objets estimés |
|---|---|---|---|---|---|---|
| 01 Bas-Saint-Laurent | 132 | 124 | 8 | 61 711 | 24 899 | 55 913 |
| 02 Saguenay–Lac-Saint-Jean | 62 | 58 | 5 | 75 712 | 17 357 | 67 550 |
| 03 Capitale-Nationale | 73 | 69 | 7 | 37 824 | 15 904 | 36 291 |
| 04 Mauricie | 53 | 46 | 6 | 33 665 | 17 238 | 37 283 |
| 05 Estrie | 119 | 117 | 9 | 41 812 | 15 776 | 47 977 |
| 06 Montréal | 18 | 16 | 1 | 10 204 | 3 376 | 10 424 |
| 07 Outaouais | 78 | 73 | 5 | 82 228 | 51 683 | 92 107 |
| 08 Abitibi-Témiscamingue | 80 | 72 | 5 | 63 964 | 26 855 | 76 855 |
| 09 Côte-Nord | 59 | 43 | 6 | 583 320 | 174 496 | 377 146 |
| 10 Nord-du-Québec | 63 | 50 | 3 | 894 430 | 218 888 | 242 746 |
| 11 Gaspésie–Îles-de-la-Madeleine | 59 | 52 | 6 | 60 743 | 32 817 | 39 379 |
| 12 Chaudière-Appalaches | 140 | 136 | 10 | 62 722 | 22 481 | 63 323 |
| 13 Laval | 1 | 1 | 1 | 717 | 274 | 727 |
| 14 Lanaudière | 74 | 69 | 6 | 42 990 | 16 163 | 43 486 |
| 15 Laurentides | 92 | 87 | 8 | 64 481 | 39 187 | 74 823 |
| 16 Montérégie | 156 | 148 | 13 | 69 967 | 22 080 | 60 721 |
| 17 Centre-du-Québec | 81 | 78 | 5 | 20 853 | 10 150 | 25 078 |

## Municipalités de plus de 9 000 objets

Elles ne tiennent pas dans un seul groupe de modifications : leurs chemins neufs devront être envoyés en plusieurs fois avant la modification de la relation.

| Code | Municipalité | MRC | Relation | Sommets du MRNF | Nœuds dans OSM | Littoral | Objets estimés |
|---|---|---|---|---|---|---|---|
| 98015 | Côte-Nord-du-Golfe-du-Saint-Laurent | Le Golfe-du-Saint-Laurent | [7734578](https://www.openstreetmap.org/relation/7734578) | 209 824 | 39 087 | 277 | 210 032 |
| 99902 | Rivière-Koksoak | Administration régionale Kativik | [8792922](https://www.openstreetmap.org/relation/8792922) | 61 684 | 56 624 | 294 | 67 787 |
| 99804 | Mistissini | Nouveau toponyme à venir | [13267724](https://www.openstreetmap.org/relation/13267724) | 41 608 | 20 843 | 0 | 62 438 |
| 98904 | Lac-Jérôme | Minganie | [8146388](https://www.openstreetmap.org/relation/8146388) | 22 176 | 12 156 | 0 | 32 813 |
| 99904 | Baie-d'Hudson | Administration régionale Kativik | [8514211](https://www.openstreetmap.org/relation/8514211) | 29 266 | 76 896 | 204 | 30 289 |
| 85907 | Les Lacs-du-Témiscamingue | Témiscamingue | [8368091](https://www.openstreetmap.org/relation/8368091) | 17 010 | 5 426 | 0 | 20 516 |
| 89040 | Senneterre | La Vallée-de-l'Or | [7359770](https://www.openstreetmap.org/relation/7359770) | 13 735 | 9 763 | 0 | 18 622 |
| 96902 | Rivière-aux-Outardes | Manicouagan | [8281748](https://www.openstreetmap.org/relation/8281748) | 14 866 | 6 405 | 0 | 18 068 |
| 98912 | Petit-Mécatina | Le Golfe-du-Saint-Laurent | [8145537](https://www.openstreetmap.org/relation/8145537) | 15 513 | 1 292 | 0 | 15 642 |
| 97904 | Lac-Walker | Sept-Rivières | [8282725](https://www.openstreetmap.org/relation/8282725) | 12 099 | 6 742 | 0 | 15 206 |
| 99814 | Chisasibi | Nouveau toponyme à venir | [13266133](https://www.openstreetmap.org/relation/13266133) | 13 874 | 1 454 | 12 | 14 070 |
| 97908 | Caniapiscau | Caniapiscau | [8282723](https://www.openstreetmap.org/relation/8282723) | 8 159 | 1 819 | 0 | 9 969 |
| 99030 | Mistissini | Nouveau toponyme à venir | [13266598](https://www.openstreetmap.org/relation/13266598) | 4 652 | 5 033 | 0 | 9 672 |
| 84902 | Lac-Nilgaut | Pontiac | [8106705](https://www.openstreetmap.org/relation/8106705) | 9 116 | 1 999 | 0 | 9 671 |
| 97912 | Lac-Juillet | Caniapiscau | [8449502](https://www.openstreetmap.org/relation/8449502) | 7 905 | 1 465 | 0 | 9 369 |
| 89910 | Réservoir-Dozois | La Vallée-de-l'Or | [8161780](https://www.openstreetmap.org/relation/8161780) | 8 459 | 1 628 | 0 | 9 272 |

## Relations faites en partie de littoral

Chemins `natural=*` membres de la relation (littoral, surtout). La règle 2 les retire de la relation, et la limite devient un chemin distinct.

| Code | Municipalité | MRC | Relation | Chemins | Dont natural=* | Dont waterway=* |
|---|---|---|---|---|---|---|
| 01023 | Les Îles-de-la-Madeleine | Communauté maritime des Îles-de-la-Madeleine | [8402197](https://www.openstreetmap.org/relation/8402197) | 422 | 417 | 0 |
| 99902 | Rivière-Koksoak | Administration régionale Kativik | [8792922](https://www.openstreetmap.org/relation/8792922) | 481 | 294 | 2 |
| 98015 | Côte-Nord-du-Golfe-du-Saint-Laurent | Le Golfe-du-Saint-Laurent | [7734578](https://www.openstreetmap.org/relation/7734578) | 284 | 277 | 1 |
| 10043 | Rimouski | Rimouski-Neigette | [8138193](https://www.openstreetmap.org/relation/8138193) | 251 | 244 | 0 |
| 99904 | Baie-d'Hudson | Administration régionale Kativik | [8514211](https://www.openstreetmap.org/relation/8514211) | 236 | 204 | 0 |
| 98012 | Saint-Augustin | Le Golfe-du-Saint-Laurent | [7734575](https://www.openstreetmap.org/relation/7734575) | 175 | 171 | 0 |
| 98010 | Bonne-Espérance | Le Golfe-du-Saint-Laurent | [7734573](https://www.openstreetmap.org/relation/7734573) | 168 | 160 | 0 |
| 98040 | Havre-Saint-Pierre | Minganie | [7734513](https://www.openstreetmap.org/relation/7734513) | 144 | 138 | 0 |
| 97007 | Sept-Îles | Sept-Rivières | [7722332](https://www.openstreetmap.org/relation/7722332) | 148 | 135 | 2 |
| 98055 | Rivière-au-Tonnerre | Minganie | [7734517](https://www.openstreetmap.org/relation/7734517) | 125 | 119 | 0 |
| 98005 | Blanc-Sablon | Le Golfe-du-Saint-Laurent | [7734572](https://www.openstreetmap.org/relation/7734572) | 110 | 106 | 0 |
| 03005 | Gaspé | La Côte-de-Gaspé | [8237761](https://www.openstreetmap.org/relation/8237761) | 110 | 104 | 1 |
| 97022 | Port-Cartier | Sept-Rivières | [7722335](https://www.openstreetmap.org/relation/7722335) | 83 | 80 | 0 |
| 01042 | Grosse-Île | Communauté maritime des Îles-de-la-Madeleine | [8402196](https://www.openstreetmap.org/relation/8402196) | 67 | 65 | 0 |
| 02005 | Percé | Le Rocher-Percé | [8237764](https://www.openstreetmap.org/relation/8237764) | 58 | 54 | 0 |
| 98014 | Gros-Mécatina | Le Golfe-du-Saint-Laurent | [7734577](https://www.openstreetmap.org/relation/7734577) | 50 | 47 | 0 |
| 96005 | Baie-Trinité | Manicouagan | [7719053](https://www.openstreetmap.org/relation/7719053) | 44 | 41 | 0 |
| 99889 | Quaqtaq | Administration régionale Kativik | [9388808](https://www.openstreetmap.org/relation/9388808) | 43 | 39 | 0 |
| 15058 | Saint-Siméon | Charlevoix-Est | [7717111](https://www.openstreetmap.org/relation/7717111) | 40 | 37 | 0 |
| 99890 | Kangirsuk | Administration régionale Kativik | [8495612](https://www.openstreetmap.org/relation/8495612) | 39 | 36 | 0 |
| 99879 | Inukjuak | Administration régionale Kativik | [8492856](https://www.openstreetmap.org/relation/8492856) | 37 | 33 | 0 |
| 10070 | Saint-Fabien | Rimouski-Neigette | [8138192](https://www.openstreetmap.org/relation/8138192) | 37 | 31 | 1 |
| 98035 | Baie-Johan-Beetz | Minganie | [7734512](https://www.openstreetmap.org/relation/7734512) | 35 | 31 | 0 |
| 99894 | Kangiqsualujjuaq | Administration régionale Kativik | [8495494](https://www.openstreetmap.org/relation/8495494) | 54 | 31 | 0 |
| 02047 | Port-Daniel–Gascons | Le Rocher-Percé | [8271756](https://www.openstreetmap.org/relation/8271756) | 38 | 31 | 0 |
| 99885 | Ivujivik | Administration régionale Kativik | [8492877](https://www.openstreetmap.org/relation/8492877) | 33 | 30 | 0 |
| 02028 | Chandler | Le Rocher-Percé | [8271776](https://www.openstreetmap.org/relation/8271776) | 38 | 30 | 0 |
| 98030 | Aguanish | Minganie | [7734511](https://www.openstreetmap.org/relation/7734511) | 34 | 28 | 2 |
| 98025 | Natashquan | Minganie | [7734510](https://www.openstreetmap.org/relation/7734510) | 45 | 26 | 3 |
| 12045 | Notre-Dame-des-Sept-Douleurs | Rivière-du-Loup | [8228147](https://www.openstreetmap.org/relation/8228147) | 25 | 25 | 0 |
| 99888 | Kangiqsujuaq | Administration régionale Kativik | [9388839](https://www.openstreetmap.org/relation/9388839) | 32 | 25 | 0 |
| 96020 | Baie-Comeau | Manicouagan | [7719056](https://www.openstreetmap.org/relation/7719056) | 29 | 24 | 0 |
| 98050 | Rivière-Saint-Jean | Minganie | [7734516](https://www.openstreetmap.org/relation/7734516) | 27 | 24 | 0 |
| 16023 | L'Isle-aux-Coudres | Charlevoix | [7717121](https://www.openstreetmap.org/relation/7717121) | 23 | 23 | 0 |
| 98045 | Longue-Pointe-de-Mingan | Minganie | [7734515](https://www.openstreetmap.org/relation/7734515) | 27 | 23 | 0 |
| 95025 | Les Escoumins | La Haute-Côte-Nord | [7719067](https://www.openstreetmap.org/relation/7719067) | 26 | 22 | 0 |
| 96015 | Franquelin | Manicouagan | [7719055](https://www.openstreetmap.org/relation/7719055) | 25 | 21 | 0 |
| 99891 | Aupaluk | Administration régionale Kativik | [9388600](https://www.openstreetmap.org/relation/9388600) | 30 | 18 | 2 |
| 99812 | Wemindji | Nouveau toponyme à venir | [12893851](https://www.openstreetmap.org/relation/12893851) | 26 | 17 | 0 |
| 04005 | Sainte-Madeleine-de-la-Rivière-Madeleine | La Haute-Gaspésie | [8237926](https://www.openstreetmap.org/relation/8237926) | 22 | 17 | 0 |
| 15013 | La Malbaie | Charlevoix-Est | [7717114](https://www.openstreetmap.org/relation/7717114) | 31 | 16 | 6 |
| 95050 | Colombier | La Haute-Côte-Nord | [7719063](https://www.openstreetmap.org/relation/7719063) | 29 | 16 | 2 |
| 04010 | Saint-Maxime-du-Mont-Louis | La Haute-Gaspésie | [8240795](https://www.openstreetmap.org/relation/8240795) | 20 | 16 | 0 |
| 16005 | Petite-Rivière-Saint-François | Charlevoix | [7717123](https://www.openstreetmap.org/relation/7717123) | 18 | 15 | 0 |
| 21902 | Sault-au-Cochon | La Côte-de-Beaupré | [8146885](https://www.openstreetmap.org/relation/8146885) | 19 | 15 | 0 |
| 17070 | Saint-Jean-Port-Joli | L'Islet | [8188530](https://www.openstreetmap.org/relation/8188530) | 19 | 15 | 0 |
| 99892 | Tasiujaq | Administration régionale Kativik | [9388430](https://www.openstreetmap.org/relation/9388430) | 19 | 14 | 0 |
| 12057 | Cacouna | Rivière-du-Loup | [8227654](https://www.openstreetmap.org/relation/8227654) | 19 | 13 | 0 |
| 95018 | Les Bergeronnes | La Haute-Côte-Nord | [7719068](https://www.openstreetmap.org/relation/7719068) | 17 | 13 | 0 |
| 99140 | Ivujivik | Administration régionale Kativik | [9389089](https://www.openstreetmap.org/relation/9389089) | 14 | 13 | 0 |
| 03020 | Grande-Vallée | La Côte-de-Gaspé | [8237873](https://www.openstreetmap.org/relation/8237873) | 19 | 13 | 0 |
| 95045 | Forestville | La Haute-Côte-Nord | [7719064](https://www.openstreetmap.org/relation/7719064) | 24 | 12 | 0 |
| 99887 | Salluit | Administration régionale Kativik | [8516272](https://www.openstreetmap.org/relation/8516272) | 16 | 12 | 0 |
| 99814 | Chisasibi | Nouveau toponyme à venir | [13266133](https://www.openstreetmap.org/relation/13266133) | 22 | 12 | 1 |
| 03010 | Cloridorme | La Côte-de-Gaspé | [8237875](https://www.openstreetmap.org/relation/8237875) | 15 | 12 | 0 |
| 15065 | Baie-Sainte-Catherine | Charlevoix-Est | [7717110](https://www.openstreetmap.org/relation/7717110) | 17 | 11 | 2 |
| 04037 | Sainte-Anne-des-Monts | La Haute-Gaspésie | [8240889](https://www.openstreetmap.org/relation/8240889) | 14 | 11 | 0 |
| 08053 | Matane | La Matanie | [7998297](https://www.openstreetmap.org/relation/7998297) | 24 | 10 | 0 |
| 96030 | Pointe-aux-Outardes | Manicouagan | [7719058](https://www.openstreetmap.org/relation/7719058) | 14 | 10 | 0 |
| 11045 | Notre-Dame-des-Neiges | Les Basques | [8228422](https://www.openstreetmap.org/relation/8228422) | 18 | 9 | 2 |
| 95005 | Tadoussac | La Haute-Côte-Nord | [7719070](https://www.openstreetmap.org/relation/7719070) | 15 | 9 | 0 |
| 99085 | Inukjuak | Administration régionale Kativik | [9390720](https://www.openstreetmap.org/relation/9390720) | 10 | 9 | 0 |
| 99100 | Tasiujaq | Administration régionale Kativik | [9388431](https://www.openstreetmap.org/relation/9388431) | 11 | 9 | 0 |
| 99115 | Quaqtaq | Administration régionale Kativik | [9388684](https://www.openstreetmap.org/relation/9388684) | 11 | 9 | 0 |
| 04020 | Rivière-à-Claude | La Haute-Gaspésie | [8240793](https://www.openstreetmap.org/relation/8240793) | 13 | 9 | 0 |
| 08005 | Les Méchins | La Matanie | [7998291](https://www.openstreetmap.org/relation/7998291) | 19 | 8 | 0 |
| 09048 | Métis-sur-Mer | La Mitis | [8232989](https://www.openstreetmap.org/relation/8232989) | 13 | 8 | 0 |
| 96010 | Godbout | Manicouagan | [7719054](https://www.openstreetmap.org/relation/7719054) | 11 | 8 | 0 |
| 99120 | Puvirnituq | Administration régionale Kativik | [9390593](https://www.openstreetmap.org/relation/9390593) | 9 | 8 | 0 |
| 99125 | Akulivik | Administration régionale Kativik | [8490188](https://www.openstreetmap.org/relation/8490188) | 9 | 8 | 0 |
| 99883 | Akulivik | Administration régionale Kativik | [9390576](https://www.openstreetmap.org/relation/9390576) | 13 | 8 | 0 |
| 04047 | Cap-Chat | La Haute-Gaspésie | [8154704](https://www.openstreetmap.org/relation/8154704) | 12 | 8 | 0 |
| 12072 | Rivière-du-Loup | Rivière-du-Loup | [8189523](https://www.openstreetmap.org/relation/8189523) | 12 | 7 | 0 |
| 12080 | Notre-Dame-du-Portage | Rivière-du-Loup | [8166514](https://www.openstreetmap.org/relation/8166514) | 11 | 7 | 0 |
| 05010 | Shigawake | Bonaventure | [8276148](https://www.openstreetmap.org/relation/8276148) | 14 | 7 | 0 |
| 06013 | Carleton-sur-Mer | Avignon | [8271765](https://www.openstreetmap.org/relation/8271765) | 11 | 7 | 0 |
| 18050 | Montmagny | Montmagny | [8188525](https://www.openstreetmap.org/relation/8188525) | 13 | 7 | 0 |
| 99090 | Kangiqsualujjuaq | Administration régionale Kativik | [9388091](https://www.openstreetmap.org/relation/9388091) | 9 | 6 | 0 |
| 99893 | Kuujjuaq | Administration régionale Kativik | [8495694](https://www.openstreetmap.org/relation/8495694) | 11 | 6 | 0 |
| 99055 | Chisasibi | Nouveau toponyme à venir | [13266134](https://www.openstreetmap.org/relation/13266134) | 17 | 6 | 1 |
| 99806 | Waskaganish | Nouveau toponyme à venir | [13266168](https://www.openstreetmap.org/relation/13266168) | 10 | 6 | 0 |
| 17078 | L'Islet | L'Islet | [8188527](https://www.openstreetmap.org/relation/8188527) | 10 | 6 | 0 |
| 69075 | Dundee | Le Haut-Saint-Laurent | [7743232](https://www.openstreetmap.org/relation/7743232) | 47 | 6 | 0 |
| 08015 | Grosses-Roches | La Matanie | [7998289](https://www.openstreetmap.org/relation/7998289) | 8 | 5 | 0 |
| 11055 | Saint-Simon-de-Rimouski | Les Basques | [8228995](https://www.openstreetmap.org/relation/8228995) | 11 | 5 | 2 |
| 14065 | Rivière-Ouelle | Kamouraska | [8120206](https://www.openstreetmap.org/relation/8120206) | 10 | 5 | 0 |
| 95032 | Longue-Rive | La Haute-Côte-Nord | [7719066](https://www.openstreetmap.org/relation/7719066) | 8 | 5 | 0 |
| 99877 | Kuujjuarapik | Administration régionale Kativik | [9391150](https://www.openstreetmap.org/relation/9391150) | 12 | 5 | 0 |
| 02015 | Grande-Rivière | Le Rocher-Percé | [8244714](https://www.openstreetmap.org/relation/8244714) | 11 | 5 | 0 |
| 18045 | Cap-Saint-Ignace | Montmagny | [8188526](https://www.openstreetmap.org/relation/8188526) | 12 | 5 | 0 |
| 09060 | Grand-Métis | La Mitis | [8232990](https://www.openstreetmap.org/relation/8232990) | 8 | 4 | 1 |
| 09092 | Sainte-Luce | La Mitis | [8226226](https://www.openstreetmap.org/relation/8226226) | 9 | 4 | 0 |
| 12043 | L'Isle-Verte | Rivière-du-Loup | [8228146](https://www.openstreetmap.org/relation/8228146) | 12 | 4 | 0 |
| 14040 | Saint-André-de-Kamouraska | Kamouraska | [8120202](https://www.openstreetmap.org/relation/8120202) | 9 | 4 | 0 |
| 14055 | Saint-Denis-De La Bouteillerie | Kamouraska | [8120205](https://www.openstreetmap.org/relation/8120205) | 7 | 4 | 0 |
| 99110 | Kangirsuk | Administration régionale Kativik | [9388634](https://www.openstreetmap.org/relation/9388634) | 5 | 4 | 0 |
| 99050 | Wemindji | Nouveau toponyme à venir | [12893850](https://www.openstreetmap.org/relation/12893850) | 10 | 4 | 3 |
| 02010 | Sainte-Thérèse-de-Gaspé | Le Rocher-Percé | [8244715](https://www.openstreetmap.org/relation/8244715) | 6 | 4 | 0 |
| 03015 | Petite-Vallée | La Côte-de-Gaspé | [8237874](https://www.openstreetmap.org/relation/8237874) | 6 | 4 | 0 |
| 03902 | Rivière-Saint-Jean | La Côte-de-Gaspé | [8237876](https://www.openstreetmap.org/relation/8237876) | 13 | 4 | 1 |
| 04025 | Marsoui | La Haute-Gaspésie | [8240891](https://www.openstreetmap.org/relation/8240891) | 8 | 4 | 0 |
| 06020 | Nouvelle | Avignon | [8271764](https://www.openstreetmap.org/relation/8271764) | 8 | 4 | 0 |
| 08073 | Saint-Ulric | La Matanie | [7998298](https://www.openstreetmap.org/relation/7998298) | 8 | 3 | 0 |
| 08080 | Baie-des-Sables | La Matanie | [7998299](https://www.openstreetmap.org/relation/7998299) | 6 | 3 | 0 |
| 09085 | Sainte-Flavie | La Mitis | [8232992](https://www.openstreetmap.org/relation/8232992) | 10 | 3 | 2 |
| 15005 | Saint-Irénée | Charlevoix-Est | [7717112](https://www.openstreetmap.org/relation/7717112) | 15 | 3 | 6 |
| 95040 | Portneuf-sur-Mer | La Haute-Côte-Nord | [7719065](https://www.openstreetmap.org/relation/7719065) | 7 | 3 | 0 |
| 04015 | Mont-Saint-Pierre | La Haute-Gaspésie | [8240794](https://www.openstreetmap.org/relation/8240794) | 5 | 3 | 0 |
| 04030 | La Martre | La Haute-Gaspésie | [8240890](https://www.openstreetmap.org/relation/8240890) | 7 | 3 | 0 |
| 06005 | Maria | Avignon | [8271767](https://www.openstreetmap.org/relation/8271767) | 10 | 3 | 0 |
| 06025 | Escuminac | Avignon | [8271763](https://www.openstreetmap.org/relation/8271763) | 6 | 3 | 0 |
| 08023 | Sainte-Félicité | La Matanie | [7998292](https://www.openstreetmap.org/relation/7998292) | 6 | 2 | 0 |
| 14045 | Saint-Germain-de-Kamouraska | Kamouraska | [8120203](https://www.openstreetmap.org/relation/8120203) | 6 | 2 | 0 |
| 14050 | Kamouraska | Kamouraska | [8120204](https://www.openstreetmap.org/relation/8120204) | 6 | 2 | 0 |
| 99075 | Kuujjuarapik | Administration régionale Kativik | [9391149](https://www.openstreetmap.org/relation/9391149) | 6 | 2 | 1 |
| 99878 | Umiujaq | Administration régionale Kativik | [9391174](https://www.openstreetmap.org/relation/9391174) | 11 | 2 | 0 |
| 99070 | Whapmagoostui | Nouveau toponyme à venir | [8490438](https://www.openstreetmap.org/relation/8490438) | 12 | 2 | 4 |
| 05032 | Paspébiac | Bonaventure | [8271757](https://www.openstreetmap.org/relation/8271757) | 9 | 2 | 0 |
| 05040 | New Carlisle | Bonaventure | [8271758](https://www.openstreetmap.org/relation/8271758) | 8 | 2 | 0 |
| 05045 | Bonaventure | Bonaventure | [8271759](https://www.openstreetmap.org/relation/8271759) | 8 | 2 | 0 |
| 05060 | Caplan | Bonaventure | [8271761](https://www.openstreetmap.org/relation/8271761) | 5 | 2 | 0 |
| 05070 | New Richmond | Bonaventure | [8271762](https://www.openstreetmap.org/relation/8271762) | 8 | 2 | 0 |
| 17065 | Saint-Roch-des-Aulnaies | L'Islet | [8188529](https://www.openstreetmap.org/relation/8188529) | 5 | 2 | 0 |
| 11040 | Trois-Pistoles | Les Basques | [8228426](https://www.openstreetmap.org/relation/8228426) | 2 | 1 | 0 |
| 96025 | Pointe-Lebel | Manicouagan | [7719057](https://www.openstreetmap.org/relation/7719057) | 3 | 1 | 0 |
| 96040 | Ragueneau | Manicouagan | [7719060](https://www.openstreetmap.org/relation/7719060) | 13 | 1 | 5 |
| 99080 | Umiujaq | Administration régionale Kativik | [9391175](https://www.openstreetmap.org/relation/9391175) | 2 | 1 | 0 |
| 99130 | Kangiqsujuaq | Administration régionale Kativik | [8495564](https://www.openstreetmap.org/relation/8495564) | 2 | 1 | 0 |
| 99135 | Salluit | Administration régionale Kativik | [9389056](https://www.openstreetmap.org/relation/9389056) | 2 | 1 | 0 |
| 05015 | Saint-Godefroi | Bonaventure | [8276147](https://www.openstreetmap.org/relation/8276147) | 9 | 1 | 0 |
| 05020 | Hope Town | Bonaventure | [8276146](https://www.openstreetmap.org/relation/8276146) | 10 | 1 | 0 |
| 05025 | Hope | Bonaventure | [8276145](https://www.openstreetmap.org/relation/8276145) | 12 | 1 | 0 |
| 05055 | Saint-Siméon | Bonaventure | [8271760](https://www.openstreetmap.org/relation/8271760) | 5 | 1 | 0 |
| 06030 | Pointe-à-la-Croix | Avignon | [8274884](https://www.openstreetmap.org/relation/8274884) | 24 | 1 | 6 |

## Autres cas à noter

Absentes (voir aussi [municipalites.md](municipalites.md)), `ref:qc` en double, anneau ouvert dans OSM, membres hors de l'extrait.

| Code | Municipalité | MRC | Relation | Notes |
|---|---|---|---|---|
| 08990 | TNO aquatique de la MRC de La Matanie | La Matanie |  | absente |
| 09990 | TNO aquatique de la MRC de La Mitis | La Mitis |  | absente |
| 10990 | TNO aquatique de la MRC de Rimouski-Neigette | Rimouski-Neigette |  | absente |
| 11990 | TNO aquatique de la MRC des Basques | Les Basques |  | absente |
| 12802 | Kataskomiq | Rivière-du-Loup |  | absente |
| 12804 | Cacouna | Rivière-du-Loup |  | absente |
| 14082 | La Pocatière | Kamouraska |  | absente |
| 14990 | TNO aquatique de la MRC de Kamouraska | Kamouraska |  | absente |
| 91802 | Mashteuiatsh | Le Domaine-du-Roy |  | absente |
| 91990 | TNO aquatique de la MRC du Domaine-du-Roy | Le Domaine-du-Roy |  | absente |
| 93990 | TNO aquatique de la MRC de Lac-Saint-Jean-Est | Lac-Saint-Jean-Est |  | absente |
| 94990 | TNO aquatique de la MRC du Fjord-du-Saguenay | Le Fjord-du-Saguenay |  | absente |
| 16990 | TNO aquatique de la MRC de Charlevoix | Charlevoix |  | absente |
| 20990 | TNO aquatique de la MRC de L'Île-d'Orléans | L'Île-d'Orléans |  | absente |
| 21990 | TNO aquatique de la MRC de La Côte-de-Beaupré | La Côte-de-Beaupré |  | absente |
| 34990 | TNO aquatique de la MRC de Portneuf | Portneuf |  | absente |
| 35990 | TNO aquatique de la MRC de Mékinac | Mékinac |  | absente |
| 36990 | TNO aquatique de la MRC géographique de Shawinigan | Shawinigan |  | absente |
| 37990 | TNO aquatique de la MRC des Chenaux | Les Chenaux |  | absente |
| 51990 | TNO aquatique de la MRC de Maskinongé | Maskinongé |  | absente |
| 90801 | Coucoucache | La Tuque |  | absente |
| 90802 | Wemotaci | La Tuque |  | absente |
| 90804 | Obedjiwan | La Tuque |  | absente |
| 42990 | TNO aquatique de la MRC du Val-Saint-François | Le Val-Saint-François |  | absente |
| 46990 | TNO aquatique de la MRC de Brome-Missisquoi | Brome-Missisquoi |  | absente |
| 66940 | TNO terrestre de la MRC géographique de Montréal | Montréal |  | absente |
| 66990 | TNO aquatique de la MRC géographique de Montréal | Montréal |  | absente |
| 80990 | TNO aquatique de la MRC de Papineau | Papineau |  | absente |
| 83802 | Kitigan Zibi | La Vallée-de-la-Gatineau |  | absente |
| 83804 | Lac-Rapide | La Vallée-de-la-Gatineau |  | absente |
| 83990 | TNO aquatique de la MRC de La Vallée-de-la-Gatineau | La Vallée-de-la-Gatineau |  | absente |
| 84990 | TNO aquatique de la MRC de Pontiac | Pontiac |  | absente |
| 85802 | Kebaowek | Témiscamingue |  | absente |
| 85803 | Hunter's Point | Témiscamingue |  | absente |
| 85804 | Winneway | Témiscamingue |  | absente |
| 85806 | Timiskaming | Témiscamingue |  | absente |
| 87990 | TNO aquatique de la MRC d'Abitibi-Ouest | Abitibi-Ouest |  | absente |
| 88802 | Pikogan | Abitibi |  | absente |
| 89802 | Kitcisakik | La Vallée-de-l'Or |  | absente |
| 89804 | Lac-Simon | La Vallée-de-l'Or |  | absente |
| 95802 | Essipit | La Haute-Côte-Nord |  | absente |
| 95990 | TNO aquatique de la MRC de La Haute-Côte-Nord | La Haute-Côte-Nord |  | absente |
| 96802 | Pessamit | Manicouagan |  | absente |
| 96990 | TNO aquatique de la MRC de Manicouagan | Manicouagan |  | absente |
| 97802 | Uashat | Sept-Rivières |  | absente |
| 97804 | Maliotenam | Sept-Rivières |  | absente |
| 97990 | TNO aquatique de la MRC de Sept-Rivières | Sept-Rivières |  | absente |
| 97806 | Kawawachikamach | Caniapiscau |  | absente |
| 97808 | Matimekosh | Caniapiscau |  | absente |
| 97810 | Lac-John | Caniapiscau |  | absente |
| 98806 | Nutashkuan | Minganie |  | absente |
| 98808 | Mingan | Minganie |  | absente |
| 98990 | TNO aquatique de la MRC de Minganie | Minganie |  | absente |
| 98802 | Pakuashipi | Le Golfe-du-Saint-Laurent |  | absente (niveau 10) |
| 98804 | La Romaine | Le Golfe-du-Saint-Laurent |  | absente |
| 98992 | TNO aquatique de la MRC Le Golfe-du-Saint-Laurent | Le Golfe-du-Saint-Laurent |  | absente |
| 99060 | Eeyou Istchee Baie-James | Jamésie |  | absente (niveau 7) |
| 99875 | Kiggaluk | Jamésie |  | absente |
| 99908 | Toponyme à venir | Jamésie |  | absente |
| 99910 | Toponyme à venir | Jamésie |  | absente |
| 99914 | Toponyme à venir | Jamésie |  | absente |
| 99916 | Toponyme à venir | Jamésie |  | absente |
| 99918 | Toponyme à venir | Jamésie |  | absente |
| 99920 | Toponyme à venir | Jamésie |  | absente |
| 99922 | Toponyme à venir | Jamésie |  | absente |
| 99924 | Toponyme à venir | Jamésie |  | absente |
| 99065 | Kawawachikamach | Administration régionale Kativik |  | absente |
| 99896 | Killiniq | Administration régionale Kativik |  | absente |
| 99818 | Oujé-Bougoumou | Nouveau toponyme à venir |  | absente |
| 02990 | TNO aquatique de la MRC du Rocher-Percé | Le Rocher-Percé |  | absente |
| 03990 | TNO aquatique de la MRC de La Côte-de-Gaspé | La Côte-de-Gaspé |  | absente |
| 04990 | TNO aquatique de la MRC de La Haute-Gaspésie | La Haute-Gaspésie |  | absente |
| 05990 | TNO aquatique de la MRC de Bonaventure | Bonaventure |  | absente |
| 06802 | Gesgapegiag | Avignon |  | absente |
| 06804 | Listuguj | Avignon |  | absente |
| 06990 | TNO aquatique de la MRC d'Avignon | Avignon |  | absente |
| 18990 | TNO aquatique de la MRC de Montmagny | Montmagny |  | absente |
| 19990 | TNO aquatique de la MRC de Bellechasse | Bellechasse |  | absente |
| 26990 | TNO aquatique de la MRC de La Nouvelle-Beauce | La Nouvelle-Beauce |  | absente |
| 33990 | TNO aquatique de la MRC de Lotbinière | Lotbinière |  | absente |
| 52990 | TNO aquatique de la MRC de D'Autray | D'Autray |  | absente |
| 60990 | TNO aquatique de la MRC de L'Assomption | L'Assomption |  | absente |
| 61990 | TNO aquatique de la MRC de Joliette | Joliette |  | absente |
| 62802 | Manawan | Matawinie |  | absente |
| 62990 | TNO aquatique de la MRC de Matawinie | Matawinie |  | absente |
| 72802 | Kanesatake | Deux-Montagnes |  | absente |
| 75990 | TNO aquatique de la MRC de La Rivière-du-Nord | La Rivière-du-Nord |  | absente |
| 76990 | TNO aquatique de la MRC d'Argenteuil | Argenteuil |  | absente |
| 78802 | Doncaster | Les Laurentides |  | absente |
| 79992 | TNO aquatique de la MRC d'Antoine-Labelle | Antoine-Labelle |  | absente |
| 53990 | TNO aquatique de la MRC Pierre-De Saurel | Pierre-De Saurel |  | absente |
| 67802 | Kahnawake | Roussillon |  | absente |
| 67940 | TNO terrestre de la MRC de Roussillon | Roussillon |  | absente |
| 67990 | TNO aquatique de la MRC de Roussillon | Roussillon |  | absente |
| 69802 | Akwesasne | Le Haut-Saint-Laurent |  | absente |
| 69990 | TNO aquatique de la MRC du Haut-Saint-Laurent | Le Haut-Saint-Laurent |  | absente |
| 70990 | TNO aquatique de la MRC de Beauharnois-Salaberry | Beauharnois-Salaberry |  | absente |
| 71990 | TNO aquatique de la MRC de Vaudreuil-Soulanges | Vaudreuil-Soulanges |  | absente |
| 38802 | Wôlinak | Bécancour |  | absente |
| 49990 | TNO aquatique de la MRC de Drummond | Drummond |  | absente |
| 50802 | Odanak | Nicolet-Yamaska |  | absente |

## Par MRC

| Région | MRC | Municipalités | Dans OSM | Sommets du MRNF | Nœuds dans OSM | Objets estimés | Plus grosse municipalité |
|---|---|---|---|---|---|---|---|
| 01 | 07 La Matapédia | 25 | 25 | 5 401 | 1 388 | 5 929 | Ruisseau-des-Mineurs (1 247) |
| 01 | 08 La Matanie | 13 | 12 | 7 284 | 2 535 | 5 842 | Rivière-Bonjour (1 436) |
| 01 | 09 La Mitis | 19 | 18 | 8 588 | 2 844 | 7 886 | Sainte-Flavie (1 488) |
| 01 | 10 Rimouski-Neigette | 11 | 10 | 4 497 | 5 336 | 3 796 | Rimouski (1 242) |
| 01 | 11 Les Basques | 12 | 11 | 11 994 | 2 729 | 8 572 | Notre-Dame-des-Neiges (2 843) |
| 01 | 12 Rivière-du-Loup | 15 | 13 | 10 098 | 4 929 | 8 848 | Saint-Paul-de-la-Croix (1 782) |
| 01 | 13 Témiscouata | 19 | 19 | 8 411 | 2 360 | 9 671 | Lejeune (2 060) |
| 01 | 14 Kamouraska | 18 | 16 | 5 438 | 2 778 | 5 369 | Rivière-Ouelle (960) |
| 02 | 91 Le Domaine-du-Roy | 12 | 10 | 19 292 | 4 170 | 15 977 | Lac-Ashuapmushuan (5 745) |
| 02 | 92 Maria-Chapdelaine | 15 | 15 | 22 713 | 5 919 | 24 500 | Passes-Dangereuses (8 208) |
| 02 | 93 Lac-Saint-Jean-Est | 17 | 16 | 16 992 | 4 719 | 13 370 | Sainte-Monique (3 714) |
| 02 | 941 Saguenay | 1 | 1 | 965 | 287 | 1 107 | Saguenay (1 107) |
| 02 | 942 Le Fjord-du-Saguenay | 17 | 16 | 15 750 | 2 262 | 12 596 | Mont-Valin (4 675) |
| 03 | 15 Charlevoix-Est | 9 | 9 | 3 705 | 4 619 | 4 500 | Saint-Aimé-des-Lacs (857) |
| 03 | 16 Charlevoix | 8 | 7 | 5 487 | 2 257 | 4 150 | L'Isle-aux-Coudres (1 180) |
| 03 | 20 L'Île-d'Orléans | 7 | 6 | 7 586 | 327 | 4 233 | Saint-Laurent-de-l'Île-d'Orléans (1 193) |
| 03 | 21 La Côte-de-Beaupré | 12 | 11 | 4 534 | 1 956 | 4 298 | Saint-Joachim (791) |
| 03 | 22 La Jacques-Cartier | 10 | 10 | 4 176 | 1 349 | 4 840 | Lac-Croche (1 382) |
| 03 | 23 Québec | 5 | 5 | 4 178 | 1 243 | 4 797 | Québec (3 091) |
| 03 | 34 Portneuf | 22 | 21 | 8 158 | 4 153 | 9 473 | Saint-Basile (1 038) |
| 04 | 35 Mékinac | 15 | 14 | 8 786 | 4 323 | 9 943 | Lac-Normand (3 548) |
| 04 | 36 Shawinigan | 2 | 1 | 3 485 | 496 | 2 403 | Shawinigan (2 403) |
| 04 | 371 Trois-Rivières | 1 | 1 | 345 | 210 | 448 | Trois-Rivières (448) |
| 04 | 372 Les Chenaux | 11 | 10 | 2 762 | 886 | 3 000 | Sainte-Anne-de-la-Pérade (605) |
| 04 | 51 Maskinongé | 18 | 17 | 11 723 | 4 728 | 12 322 | Saint-Alexis-des-Monts (1 409) |
| 04 | 90 La Tuque | 6 | 3 | 6 564 | 6 595 | 9 167 | La Tuque (7 111) |
| 05 | 30 Le Granit | 19 | 19 | 10 842 | 5 010 | 14 325 | Saint-Romain (3 136) |
| 05 | 40 Les Sources | 7 | 7 | 2 203 | 1 120 | 2 755 | Danville (988) |
| 05 | 41 Le Haut-Saint-François | 14 | 14 | 3 200 | 1 543 | 4 201 | Chartierville (1 011) |
| 05 | 42 Le Val-Saint-François | 19 | 18 | 9 950 | 1 954 | 7 792 | Saint-François-Xavier-de-Brompton (1 107) |
| 05 | 43 Sherbrooke | 1 | 1 | 1 200 | 296 | 1 331 | Sherbrooke (1 331) |
| 05 | 44 Coaticook | 12 | 12 | 2 355 | 1 712 | 3 669 | Saint-Malo (892) |
| 05 | 45 Memphrémagog | 17 | 17 | 3 659 | 1 840 | 4 620 | Hatley (647) |
| 05 | 46 Brome-Missisquoi | 22 | 21 | 6 286 | 1 696 | 6 872 | Bromont (1 181) |
| 05 | 47 La Haute-Yamaska | 8 | 8 | 2 117 | 605 | 2 412 | Shefford (1 275) |
| 06 | 66 Montréal | 18 | 16 | 10 204 | 3 376 | 10 424 | Montréal (4 542) |
| 07 | 80 Papineau | 26 | 25 | 7 524 | 9 389 | 11 717 | Saint-André-Avellin (1 846) |
| 07 | 81 Gatineau | 1 | 1 | 1 936 | 3 936 | 2 728 | Gatineau (2 728) |
| 07 | 82 Les Collines-de-l'Outaouais | 6 | 6 | 3 191 | 4 589 | 5 083 | Pontiac (1 295) |
| 07 | 83 La Vallée-de-la-Gatineau | 25 | 22 | 38 474 | 22 841 | 42 453 | Lac-Moselle (8 152) |
| 07 | 84 Pontiac | 20 | 19 | 31 103 | 10 928 | 30 126 | Lac-Nilgaut (9 671) |
| 08 | 85 Témiscamingue | 25 | 21 | 26 711 | 7 892 | 31 809 | Les Lacs-du-Témiscamingue (20 516) |
| 08 | 86 Rouyn-Noranda | 1 | 1 | 787 | 423 | 1 016 | Rouyn-Noranda (1 016) |
| 08 | 87 Abitibi-Ouest | 24 | 23 | 3 280 | 2 305 | 4 192 | Palmarolle (698) |
| 08 | 88 Abitibi | 18 | 17 | 7 394 | 3 073 | 8 132 | Lac-Despinassy (3 869) |
| 08 | 89 La Vallée-de-l'Or | 12 | 10 | 25 792 | 13 162 | 31 706 | Senneterre (18 622) |
| 09 | 95 La Haute-Côte-Nord | 11 | 9 | 16 495 | 6 183 | 9 722 | Colombier (2 318) |
| 09 | 96 Manicouagan | 11 | 9 | 25 165 | 12 882 | 21 518 | Rivière-aux-Outardes (18 068) |
| 09 | 971 Sept-Rivières | 7 | 4 | 19 376 | 19 385 | 21 536 | Lac-Walker (15 206) |
| 09 | 972 Caniapiscau | 9 | 6 | 25 968 | 5 950 | 30 999 | Caniapiscau (9 969) |
| 09 | 981 Minganie | 12 | 9 | 50 680 | 44 236 | 51 924 | Lac-Jérôme (32 813) |
| 09 | 982 Le Golfe-du-Saint-Laurent | 9 | 6 | 445 636 | 85 860 | 241 447 | Côte-Nord-du-Golfe-du-Saint-Laurent (210 032) |
| 10 | 991 Jamésie | 14 | 4 | 683 519 | 364 | 1 191 | Lebel-sur-Quévillon (719) |
| 10 | 992 Administration régionale Kativik | 31 | 29 | 122 560 | 182 622 | 126 048 | Rivière-Koksoak (67 787) |
| 10 | 993 Nouveau toponyme à venir | 18 | 17 | 88 351 | 35 902 | 115 507 | Mistissini (62 438) |
| 11 | 01 Communauté maritime des Îles-de-la-Madeleine | 2 | 2 | 5 744 | 12 833 | 5 756 | Les Îles-de-la-Madeleine (2 896) |
| 11 | 02 Le Rocher-Percé | 7 | 6 | 5 218 | 4 004 | 3 122 | Chandler (1 480) |
| 11 | 03 La Côte-de-Gaspé | 8 | 7 | 6 482 | 5 963 | 3 738 | Cloridorme (1 404) |
| 11 | 04 La Haute-Gaspésie | 11 | 10 | 16 509 | 3 292 | 9 010 | Saint-Maxime-du-Mont-Louis (2 320) |
| 11 | 05 Bonaventure | 15 | 14 | 6 452 | 2 273 | 4 830 | Rivière-Bonaventure (893) |
| 11 | 06 Avignon | 16 | 13 | 20 338 | 4 452 | 12 923 | Escuminac (2 363) |
| 12 | 17 L'Islet | 14 | 14 | 4 310 | 1 989 | 4 757 | Sainte-Louise (1 014) |
| 12 | 18 Montmagny | 15 | 14 | 16 634 | 858 | 9 627 | Saint-Antoine-de-l'Isle-aux-Grues (5 967) |
| 12 | 19 Bellechasse | 21 | 20 | 9 085 | 3 636 | 10 001 | Beaumont (1 246) |
| 12 | 251 Lévis | 1 | 1 | 941 | 186 | 1 032 | Lévis (1 032) |
| 12 | 26 La Nouvelle-Beauce | 12 | 11 | 4 923 | 1 213 | 4 801 | Saint-Isidore (955) |
| 12 | 27 Beauce-Centre | 10 | 10 | 2 741 | 1 414 | 3 437 | Beauceville (703) |
| 12 | 28 Les Etchemins | 13 | 13 | 5 270 | 3 695 | 7 156 | Saint-Zacharie (1 931) |
| 12 | 29 Beauce-Sartigan | 16 | 16 | 4 401 | 2 473 | 6 036 | Saint-Théophile (2 366) |
| 12 | 31 Les Appalaches | 19 | 19 | 5 471 | 2 395 | 6 653 | Disraeli (863) |
| 12 | 33 Lotbinière | 19 | 18 | 8 946 | 4 622 | 9 823 | Sainte-Croix (1 701) |
| 13 | 65 Laval | 1 | 1 | 717 | 274 | 727 | Laval (727) |
| 14 | 52 D'Autray | 16 | 15 | 6 697 | 4 329 | 8 775 | Saint-Gabriel-de-Brandon (1 172) |
| 14 | 60 L'Assomption | 6 | 5 | 2 792 | 1 304 | 2 846 | L'Épiphanie (1 326) |
| 14 | 61 Joliette | 11 | 10 | 11 301 | 3 341 | 9 367 | Sainte-Mélanie (3 193) |
| 14 | 62 Matawinie | 29 | 27 | 16 370 | 4 307 | 15 282 | Saint-Félix-de-Valois (2 619) |
| 14 | 63 Montcalm | 10 | 10 | 4 758 | 2 420 | 5 959 | Sainte-Marie-Salomé (956) |
| 14 | 64 Les Moulins | 2 | 2 | 1 072 | 462 | 1 257 | Terrebonne (901) |
| 15 | 72 Deux-Montagnes | 8 | 7 | 7 880 | 1 207 | 5 770 | Oka (3 546) |
| 15 | 73 Thérèse-De Blainville | 7 | 7 | 2 302 | 1 017 | 2 777 | Blainville (812) |
| 15 | 74 Mirabel | 1 | 1 | 2 031 | 983 | 2 520 | Mirabel (2 520) |
| 15 | 75 La Rivière-du-Nord | 6 | 5 | 4 646 | 1 297 | 3 671 | Saint-Colomban (1 100) |
| 15 | 76 Argenteuil | 10 | 9 | 8 489 | 2 038 | 6 677 | Saint-André-d'Argenteuil (2 282) |
| 15 | 77 Les Pays-d'en-Haut | 10 | 10 | 4 499 | 1 598 | 5 288 | Sainte-Marguerite-du-Lac-Masson (1 334) |
| 15 | 78 Les Laurentides | 21 | 20 | 7 885 | 5 163 | 10 363 | Arundel (1 947) |
| 15 | 79 Antoine-Labelle | 29 | 28 | 26 749 | 25 884 | 37 757 | Lac-Douaire (7 641) |
| 16 | 48 Acton | 8 | 8 | 958 | 377 | 1 140 | Acton Vale (216) |
| 16 | 53 Pierre-De Saurel | 13 | 12 | 2 705 | 1 494 | 3 288 | Sorel-Tracy (471) |
| 16 | 54 Les Maskoutains | 17 | 17 | 3 191 | 1 686 | 3 998 | Saint-Hyacinthe (431) |
| 16 | 55 Rouville | 8 | 8 | 2 139 | 1 166 | 2 712 | Saint-Césaire (555) |
| 16 | 56 Le Haut-Richelieu | 14 | 14 | 2 905 | 1 402 | 3 525 | Saint-Jean-sur-Richelieu (684) |
| 16 | 57 La Vallée-du-Richelieu | 13 | 13 | 4 796 | 1 958 | 5 745 | Saint-Mathieu-de-Beloeil (950) |
| 16 | 58 Longueuil | 5 | 5 | 1 362 | 785 | 1 733 | Longueuil (484) |
| 16 | 59 Marguerite-D'Youville | 6 | 6 | 1 324 | 1 174 | 1 798 | Contrecoeur (568) |
| 16 | 67 Roussillon | 14 | 11 | 10 984 | 1 962 | 6 761 | Saint-Constant (1 189) |
| 16 | 68 Les Jardins-de-Napierville | 11 | 11 | 3 075 | 1 639 | 3 925 | Saint-Cyprien-de-Napierville (621) |
| 16 | 69 Le Haut-Saint-Laurent | 15 | 13 | 24 792 | 5 248 | 15 739 | Dundee (8 790) |
| 16 | 70 Beauharnois-Salaberry | 8 | 7 | 4 383 | 728 | 3 104 | Salaberry-de-Valleyfield (919) |
| 16 | 71 Vaudreuil-Soulanges | 24 | 23 | 7 353 | 2 461 | 7 253 | L'Île-Perrot (1 173) |
| 17 | 32 L'Érable | 10 | 10 | 3 379 | 1 261 | 3 999 | Inverness (891) |
| 17 | 38 Bécancour | 13 | 12 | 4 016 | 2 354 | 5 035 | Bécancour (1 021) |
| 17 | 39 Arthabaska | 22 | 22 | 4 543 | 2 379 | 5 712 | Tingwick (472) |
| 17 | 49 Drummond | 19 | 18 | 4 292 | 1 805 | 5 176 | Drummondville (741) |
| 17 | 50 Nicolet-Yamaska | 17 | 16 | 4 623 | 2 351 | 5 156 | Pierreville (890) |
