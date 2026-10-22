# Bouchées du Québec méridional

Découpage des municipalités du Québec méridional en bouchées pour l'import des limites, chacune assez petite pour un seul groupe de modifications d'OSM. Produit par `outils/bouchees.py`, d'après l'[inventaire](inventaire.md); détail dans [bouchees.csv](bouchees.csv).

Budget : 8 000 objets estimés par bouchée, au pire : tous les sommets distincts du MRNF de ses municipalités (la première bouchée qui touche une limite commune la crée en entier), plus leur part des nœuds d'OSM à supprimer. Le fichier d'envoi réel de la bouchée 1 compte 6,6 % de plus (routes coupées, raccords des voisines), sous la limite de 10 000 objets d'OSM; les bouchées suivantes coûtent moins, puisqu'elles reprennent les limites déjà conformes. Une MRC qui tient dans le budget forme une bouchée; deux MRC voisines de la même région qui tiennent ensemble sont réunies; une MRC trop grosse est coupée en groupes de municipalités voisines, en partant de l'ouest.

| Bouchées | Municipalités | Objets estimés, au pire | Moyenne par bouchée | Laissées de côté |
|---|---|---|---|---|
| 133 | 1129 | 832 362 | 6 258 | 211 |

## Bouchées

| N° | Région | MRC | Municipalités | Objets estimés | Lieu |
|---|---|---|---|---|---|
| 1 | 01 | La Matapédia | 25 | 7 796 | `lieux/quebec/Q001-La-Matapedia.toml` |
| 2 | 01 | La Matanie (1 de 2) | 11 | 6 679 | `lieux/quebec/Q002-La-Matanie.toml` |
| 3 | 01 | La Matanie (2 de 2) | 1 | 2 765 | `lieux/quebec/Q003-La-Matanie.toml` |
| 4 | 01 | La Mitis (1 de 2) | 16 | 7 881 | `lieux/quebec/Q004-La-Mitis.toml` |
| 5 | 01 | La Mitis (2 de 2) | 2 | 3 287 | `lieux/quebec/Q005-La-Mitis.toml` |
| 6 | 01 | Rimouski-Neigette | 10 | 5 541 | `lieux/quebec/Q006-Rimouski-Neigette.toml` |
| 7 | 01 | Les Basques (1 de 2), Rivière-du-Loup (2 de 3) | 8 | 7 937 | `lieux/quebec/Q007-Les-Basques.toml` |
| 8 | 01 | Les Basques (2 de 2) | 4 | 7 592 | `lieux/quebec/Q008-Les-Basques.toml` |
| 9 | 01 | Rivière-du-Loup (1 de 3) | 10 | 6 839 | `lieux/quebec/Q009-Riviere-du-Loup.toml` |
| 10 | 01 | Rivière-du-Loup (3 de 3) | 2 | 3 419 | `lieux/quebec/Q010-Riviere-du-Loup.toml` |
| 11 | 01 | Témiscouata (1 de 2) | 17 | 6 689 | `lieux/quebec/Q011-Temiscouata.toml` |
| 12 | 01 | Témiscouata (2 de 2) | 2 | 4 223 | `lieux/quebec/Q012-Temiscouata.toml` |
| 13 | 01 | Kamouraska | 16 | 6 353 | `lieux/quebec/Q013-Kamouraska.toml` |
| 14 | 02 | Le Domaine-du-Roy | 8 | 7 246 | `lieux/quebec/Q014-Le-Domaine-du-Roy.toml` |
| 15 | 02 | Maria-Chapdelaine (1 de 2) | 9 | 7 753 | `lieux/quebec/Q015-Maria-Chapdelaine.toml` |
| 16 | 02 | Maria-Chapdelaine (2 de 2), Lac-Saint-Jean-Est (1 de 5) | 5 | 4 043 | `lieux/quebec/Q016-Maria-Chapdelaine.toml` |
| 17 | 02 | Lac-Saint-Jean-Est (2 de 5) | 11 | 7 441 | `lieux/quebec/Q017-Lac-Saint-Jean-Est.toml` |
| 18 | 02 | Lac-Saint-Jean-Est (4 de 5) | 1 | 7 311 | `lieux/quebec/Q018-Lac-Saint-Jean-Est.toml` |
| 19 | 02 | Lac-Saint-Jean-Est (5 de 5), Lac-Saint-Jean-Est (3 de 5) | 3 | 6 708 | `lieux/quebec/Q019-Lac-Saint-Jean-Est.toml` |
| 20 | 02 | Saguenay, Le Fjord-du-Saguenay (1 de 3), Le Fjord-du-Saguenay (2 de 3) | 15 | 7 638 | `lieux/quebec/Q020-Saguenay.toml` |
| 21 | 02 | Le Fjord-du-Saguenay (3 de 3) | 1 | 6 279 | `lieux/quebec/Q021-Le-Fjord-du-Saguenay.toml` |
| 22 | 03 | Charlevoix-Est | 9 | 5 346 | `lieux/quebec/Q022-Charlevoix-Est.toml` |
| 23 | 03 | Charlevoix | 7 | 7 088 | `lieux/quebec/Q023-Charlevoix.toml` |
| 24 | 03 | L'Île-d'Orléans | 6 | 7 621 | `lieux/quebec/Q024-L-Ile-d-Orleans.toml` |
| 25 | 03 | La Côte-de-Beaupré | 11 | 5 701 | `lieux/quebec/Q025-La-Cote-de-Beaupre.toml` |
| 26 | 03 | La Jacques-Cartier | 10 | 7 555 | `lieux/quebec/Q026-La-Jacques-Cartier.toml` |
| 27 | 03 | Québec | 5 | 6 336 | `lieux/quebec/Q027-Quebec.toml` |
| 28 | 03 | Portneuf (1 de 2) | 10 | 7 823 | `lieux/quebec/Q028-Portneuf.toml` |
| 29 | 03 | Portneuf (2 de 2) | 11 | 5 227 | `lieux/quebec/Q029-Portneuf.toml` |
| 30 | 04 | Mékinac (1 de 3) | 2 | 4 716 | `lieux/quebec/Q030-Mekinac.toml` |
| 31 | 04 | Mékinac (2 de 3) | 7 | 7 684 | `lieux/quebec/Q031-Mekinac.toml` |
| 32 | 04 | Mékinac (3 de 3) | 5 | 3 577 | `lieux/quebec/Q032-Mekinac.toml` |
| 33 | 04 | Shawinigan | 1 | 4 565 | `lieux/quebec/Q033-Shawinigan.toml` |
| 34 | 04 | Trois-Rivières, Maskinongé (3 de 3), Les Chenaux | 14 | 6 862 | `lieux/quebec/Q034-Trois-Rivieres.toml` |
| 35 | 04 | Maskinongé (1 de 3) | 6 | 6 657 | `lieux/quebec/Q035-Maskinonge.toml` |
| 36 | 04 | Maskinongé (2 de 3) | 8 | 7 491 | `lieux/quebec/Q036-Maskinonge.toml` |
| 37 | 04 | La Tuque | 2 | 3 160 | `lieux/quebec/Q037-La-Tuque.toml` |
| 38 | 05 | Le Granit (1 de 3) | 7 | 7 776 | `lieux/quebec/Q038-Le-Granit.toml` |
| 39 | 05 | Le Granit (2 de 3) | 11 | 7 208 | `lieux/quebec/Q039-Le-Granit.toml` |
| 40 | 05 | Le Granit (3 de 3) | 1 | 6 008 | `lieux/quebec/Q040-Le-Granit.toml` |
| 41 | 05 | Les Sources, Le Haut-Saint-François | 21 | 7 903 | `lieux/quebec/Q041-Les-Sources.toml` |
| 42 | 05 | Le Val-Saint-François (1 de 2) | 15 | 7 459 | `lieux/quebec/Q042-Le-Val-Saint-Francois.toml` |
| 43 | 05 | Le Val-Saint-François (2 de 2) | 3 | 4 710 | `lieux/quebec/Q043-Le-Val-Saint-Francois.toml` |
| 44 | 05 | Sherbrooke, Coaticook | 13 | 6 358 | `lieux/quebec/Q044-Sherbrooke.toml` |
| 45 | 05 | Memphrémagog | 17 | 5 543 | `lieux/quebec/Q045-Memphremagog.toml` |
| 46 | 05 | Brome-Missisquoi (1 de 2) | 18 | 7 980 | `lieux/quebec/Q046-Brome-Missisquoi.toml` |
| 47 | 05 | Brome-Missisquoi (2 de 2), La Haute-Yamaska | 11 | 5 027 | `lieux/quebec/Q047-Brome-Missisquoi.toml` |
| 48 | 06, 16 | Montréal (4 de 5), Longueuil, Roussillon (2 de 2), Marguerite-D'Youville | 14 | 6 854 | `lieux/quebec/Q048-Montreal.toml` |
| 49 | 06 | Montréal (2 de 5), Montréal (1 de 5), Montréal (3 de 5) | 5 | 3 614 | `lieux/quebec/Q049-Montreal.toml` |
| 50 | 06 | Montréal (5 de 5) | 9 | 4 803 | `lieux/quebec/Q050-Montreal.toml` |
| 51 | 07 | Papineau (1 de 2) | 13 | 7 761 | `lieux/quebec/Q051-Papineau.toml` |
| 52 | 07 | Papineau (2 de 2) | 12 | 6 002 | `lieux/quebec/Q052-Papineau.toml` |
| 53 | 07 | Gatineau | 1 | 3 822 | `lieux/quebec/Q053-Gatineau.toml` |
| 54 | 07 | Les Collines-de-l'Outaouais | 6 | 6 625 | `lieux/quebec/Q054-Les-Collines-de-l-Outaouais.toml` |
| 55 | 07 | La Vallée-de-la-Gatineau (1 de 7) | 1 | 1 777 | `lieux/quebec/Q055-La-Vallee-de-la-Gatineau.toml` |
| 56 | 07 | La Vallée-de-la-Gatineau (2 de 7) | 3 | 6 490 | `lieux/quebec/Q056-La-Vallee-de-la-Gatineau.toml` |
| 57 | 07 | La Vallée-de-la-Gatineau (3 de 7) | 1 | 2 149 | `lieux/quebec/Q057-La-Vallee-de-la-Gatineau.toml` |
| 58 | 07 | La Vallée-de-la-Gatineau (4 de 7) | 4 | 6 185 | `lieux/quebec/Q058-La-Vallee-de-la-Gatineau.toml` |
| 59 | 07 | La Vallée-de-la-Gatineau (5 de 7) | 7 | 7 122 | `lieux/quebec/Q059-La-Vallee-de-la-Gatineau.toml` |
| 60 | 07 | La Vallée-de-la-Gatineau (6 de 7) | 2 | 7 418 | `lieux/quebec/Q060-La-Vallee-de-la-Gatineau.toml` |
| 61 | 07 | La Vallée-de-la-Gatineau (7 de 7) | 1 | 4 281 | `lieux/quebec/Q061-La-Vallee-de-la-Gatineau.toml` |
| 62 | 07 | Pontiac (1 de 4) | 1 | 7 838 | `lieux/quebec/Q062-Pontiac.toml` |
| 63 | 07 | Pontiac (2 de 4) | 4 | 6 886 | `lieux/quebec/Q063-Pontiac.toml` |
| 64 | 07 | Pontiac (3 de 4) | 9 | 7 422 | `lieux/quebec/Q064-Pontiac.toml` |
| 65 | 07 | Pontiac (4 de 4) | 4 | 6 871 | `lieux/quebec/Q065-Pontiac.toml` |
| 66 | 08 | Témiscamingue (1 de 3) | 10 | 7 963 | `lieux/quebec/Q066-Temiscamingue.toml` |
| 67 | 08 | Témiscamingue (2 de 3) | 1 | 2 307 | `lieux/quebec/Q067-Temiscamingue.toml` |
| 68 | 08 | Témiscamingue (3 de 3), Rouyn-Noranda | 10 | 5 211 | `lieux/quebec/Q068-Temiscamingue.toml` |
| 69 | 08 | Abitibi-Ouest | 23 | 4 728 | `lieux/quebec/Q069-Abitibi-Ouest.toml` |
| 70 | 08 | Abitibi (1 de 2) | 16 | 5 335 | `lieux/quebec/Q070-Abitibi.toml` |
| 71 | 08 | Abitibi (2 de 2) | 1 | 7 391 | `lieux/quebec/Q071-Abitibi.toml` |
| 72 | 08 | La Vallée-de-l'Or | 8 | 5 808 | `lieux/quebec/Q072-La-Vallee-de-l-Or.toml` |
| 73 | 11 | Communauté maritime des Îles-de-la-Madeleine | 2 | 5 767 | `lieux/quebec/Q073-Communaute-maritime-des-Iles-de-la-Madeleine.toml` |
| 74 | 11 | Le Rocher-Percé | 6 | 5 580 | `lieux/quebec/Q074-Le-Rocher-Perce.toml` |
| 75 | 11 | La Côte-de-Gaspé | 7 | 6 777 | `lieux/quebec/Q075-La-Cote-de-Gaspe.toml` |
| 76 | 11 | La Haute-Gaspésie (1 de 4) | 7 | 7 769 | `lieux/quebec/Q076-La-Haute-Gaspesie.toml` |
| 77 | 11 | La Haute-Gaspésie (2 de 4) | 1 | 3 709 | `lieux/quebec/Q077-La-Haute-Gaspesie.toml` |
| 78 | 11 | La Haute-Gaspésie (4 de 4), La Haute-Gaspésie (3 de 4) | 2 | 5 962 | `lieux/quebec/Q078-La-Haute-Gaspesie.toml` |
| 79 | 11 | Bonaventure | 14 | 6 971 | `lieux/quebec/Q079-Bonaventure.toml` |
| 80 | 11 | Avignon (1 de 3) | 4 | 7 620 | `lieux/quebec/Q080-Avignon.toml` |
| 81 | 11 | Avignon (2 de 3) | 3 | 7 824 | `lieux/quebec/Q081-Avignon.toml` |
| 82 | 11 | Avignon (3 de 3) | 6 | 6 406 | `lieux/quebec/Q082-Avignon.toml` |
| 83 | 12 | L'Islet | 14 | 4 923 | `lieux/quebec/Q083-L-Islet.toml` |
| 84 | 12 | Montmagny, Les Etchemins (2 de 2) | 14 | 6 046 | `lieux/quebec/Q084-Montmagny.toml` |
| 85 | 12 | Bellechasse (1 de 2) | 8 | 7 822 | `lieux/quebec/Q085-Bellechasse.toml` |
| 86 | 12 | Bellechasse (2 de 2) | 12 | 5 860 | `lieux/quebec/Q086-Bellechasse.toml` |
| 87 | 12 | Lévis, Lotbinière (2 de 2) | 12 | 6 828 | `lieux/quebec/Q087-Levis.toml` |
| 88 | 12 | La Nouvelle-Beauce | 11 | 6 759 | `lieux/quebec/Q088-La-Nouvelle-Beauce.toml` |
| 89 | 12 | Beauce-Centre | 10 | 4 286 | `lieux/quebec/Q089-Beauce-Centre.toml` |
| 90 | 12 | Les Etchemins (1 de 2) | 12 | 7 839 | `lieux/quebec/Q090-Les-Etchemins.toml` |
| 91 | 12 | Beauce-Sartigan | 16 | 7 332 | `lieux/quebec/Q091-Beauce-Sartigan.toml` |
| 92 | 12 | Les Appalaches | 19 | 7 719 | `lieux/quebec/Q092-Les-Appalaches.toml` |
| 93 | 12 | Lotbinière (1 de 2) | 7 | 7 917 | `lieux/quebec/Q093-Lotbiniere.toml` |
| 94 | 13, 15 | Laval, Deux-Montagnes (2 de 2), Thérèse-De Blainville | 10 | 6 667 | `lieux/quebec/Q094-Laval.toml` |
| 95 | 14 | D'Autray (1 de 2) | 12 | 7 328 | `lieux/quebec/Q095-D-Autray.toml` |
| 96 | 14 | D'Autray (2 de 2) | 3 | 3 926 | `lieux/quebec/Q096-D-Autray.toml` |
| 97 | 14 | L'Assomption, Les Moulins | 7 | 5 997 | `lieux/quebec/Q097-L-Assomption.toml` |
| 98 | 14 | Joliette (1 de 2) | 4 | 7 545 | `lieux/quebec/Q098-Joliette.toml` |
| 99 | 14 | Joliette (2 de 2) | 6 | 7 078 | `lieux/quebec/Q099-Joliette.toml` |
| 100 | 14 | Matawinie (1 de 4) | 4 | 7 965 | `lieux/quebec/Q100-Matawinie.toml` |
| 101 | 14 | Matawinie (2 de 4) | 16 | 7 685 | `lieux/quebec/Q101-Matawinie.toml` |
| 102 | 14 | Matawinie (3 de 4) | 5 | 7 861 | `lieux/quebec/Q102-Matawinie.toml` |
| 103 | 14, 15 | Matawinie (4 de 4), La Rivière-du-Nord | 7 | 6 908 | `lieux/quebec/Q103-Matawinie.toml` |
| 104 | 14 | Montcalm | 10 | 7 452 | `lieux/quebec/Q104-Montcalm.toml` |
| 105 | 15 | Deux-Montagnes (1 de 2) | 5 | 7 294 | `lieux/quebec/Q105-Deux-Montagnes.toml` |
| 106 | 15 | Mirabel | 1 | 4 556 | `lieux/quebec/Q106-Mirabel.toml` |
| 107 | 15 | Argenteuil (1 de 2) | 8 | 6 303 | `lieux/quebec/Q107-Argenteuil.toml` |
| 108 | 15 | Argenteuil (2 de 2) | 1 | 4 398 | `lieux/quebec/Q108-Argenteuil.toml` |
| 109 | 15 | Les Pays-d'en-Haut | 10 | 6 320 | `lieux/quebec/Q109-Les-Pays-d-en-Haut.toml` |
| 110 | 15 | Les Laurentides (1 de 2) | 12 | 7 675 | `lieux/quebec/Q110-Les-Laurentides.toml` |
| 111 | 15 | Les Laurentides (2 de 2) | 8 | 7 539 | `lieux/quebec/Q111-Les-Laurentides.toml` |
| 112 | 15 | Antoine-Labelle (1 de 7) | 8 | 7 947 | `lieux/quebec/Q112-Antoine-Labelle.toml` |
| 113 | 15 | Antoine-Labelle (2 de 7) | 1 | 7 256 | `lieux/quebec/Q113-Antoine-Labelle.toml` |
| 114 | 15 | Antoine-Labelle (3 de 7) | 3 | 6 395 | `lieux/quebec/Q114-Antoine-Labelle.toml` |
| 115 | 15 | Antoine-Labelle (4 de 7) | 8 | 7 890 | `lieux/quebec/Q115-Antoine-Labelle.toml` |
| 116 | 15 | Antoine-Labelle (5 de 7) | 5 | 5 820 | `lieux/quebec/Q116-Antoine-Labelle.toml` |
| 117 | 15 | Antoine-Labelle (6 de 7) | 1 | 5 715 | `lieux/quebec/Q117-Antoine-Labelle.toml` |
| 118 | 15 | Antoine-Labelle (7 de 7) | 1 | 3 732 | `lieux/quebec/Q118-Antoine-Labelle.toml` |
| 119 | 16 | Acton, Les Maskoutains | 25 | 6 173 | `lieux/quebec/Q119-Acton.toml` |
| 120 | 16 | Pierre-De Saurel | 12 | 4 252 | `lieux/quebec/Q120-Pierre-De-Saurel.toml` |
| 121 | 16 | Rouville, Le Haut-Richelieu | 22 | 7 353 | `lieux/quebec/Q121-Rouville.toml` |
| 122 | 16 | La Vallée-du-Richelieu | 13 | 7 263 | `lieux/quebec/Q122-La-Vallee-du-Richelieu.toml` |
| 123 | 16 | Roussillon (1 de 2) | 9 | 7 589 | `lieux/quebec/Q123-Roussillon.toml` |
| 124 | 16 | Les Jardins-de-Napierville, Le Haut-Saint-Laurent (2 de 2) | 17 | 6 617 | `lieux/quebec/Q124-Les-Jardins-de-Napierville.toml` |
| 125 | 16 | Le Haut-Saint-Laurent (1 de 2) | 6 | 7 659 | `lieux/quebec/Q125-Le-Haut-Saint-Laurent.toml` |
| 126 | 16 | Beauharnois-Salaberry | 7 | 5 041 | `lieux/quebec/Q126-Beauharnois-Salaberry.toml` |
| 127 | 16 | Vaudreuil-Soulanges (1 de 2) | 22 | 6 899 | `lieux/quebec/Q127-Vaudreuil-Soulanges.toml` |
| 128 | 16 | Vaudreuil-Soulanges (2 de 2) | 1 | 2 322 | `lieux/quebec/Q128-Vaudreuil-Soulanges.toml` |
| 129 | 17 | L'Érable | 10 | 4 960 | `lieux/quebec/Q129-L-Erable.toml` |
| 130 | 17 | Bécancour | 12 | 5 994 | `lieux/quebec/Q130-Becancour.toml` |
| 131 | 17 | Arthabaska | 22 | 6 830 | `lieux/quebec/Q131-Arthabaska.toml` |
| 132 | 17 | Drummond | 18 | 6 278 | `lieux/quebec/Q132-Drummond.toml` |
| 133 | 17 | Nicolet-Yamaska | 16 | 6 700 | `lieux/quebec/Q133-Nicolet-Yamaska.toml` |

## Laissées de côté

| Raison | Municipalités | Objets estimés |
|---|---|---|
| absente d'OSM | 72 | 0 |
| plus de 8 000 objets | 17 | 261 714 |
| région 09 Côte-Nord | 59 | 377 146 |
| région 10 Nord-du-Québec | 63 | 242 746 |

### Plus de 8 000 objets, hors des régions 09 et 10

| Code | Municipalité | MRC | Région | Objets estimés |
|---|---|---|---|---|
| 85907 | Les Lacs-du-Témiscamingue | Témiscamingue | Abitibi-Témiscamingue | 37 163 |
| 89040 | Senneterre | La Vallée-de-l'Or | Abitibi-Témiscamingue | 32 362 |
| 84902 | Lac-Nilgaut | Pontiac | Outaouais | 18 790 |
| 89910 | Réservoir-Dozois | La Vallée-de-l'Or | Abitibi-Témiscamingue | 17 735 |
| 69075 | Dundee | Le Haut-Saint-Laurent | Montérégie | 16 299 |
| 92902 | Passes-Dangereuses | Maria-Chapdelaine | Saguenay–Lac-Saint-Jean | 16 043 |
| 92904 | Rivière-Mistassini | Maria-Chapdelaine | Saguenay–Lac-Saint-Jean | 14 290 |
| 83906 | Lac-Lenôtre | La Vallée-de-la-Gatineau | Outaouais | 13 821 |
| 83908 | Lac-Moselle | La Vallée-de-la-Gatineau | Outaouais | 12 699 |
| 79922 | Lac-Douaire | Antoine-Labelle | Laurentides | 12 344 |
| 18070 | Saint-Antoine-de-l'Isle-aux-Grues | Montmagny | Chaudière-Appalaches | 11 906 |
| 90012 | La Tuque | La Tuque | Mauricie | 11 713 |
| 91902 | Lac-Ashuapmushuan | Le Domaine-du-Roy | Saguenay–Lac-Saint-Jean | 10 784 |
| 91025 | Roberval | Le Domaine-du-Roy | Saguenay–Lac-Saint-Jean | 9 811 |
| 94930 | Mont-Valin | Le Fjord-du-Saguenay | Saguenay–Lac-Saint-Jean | 9 107 |
| 66023 | Montréal | Montréal | Montréal | 8 592 |
| 83065 | Maniwaki | La Vallée-de-la-Gatineau | Outaouais | 8 255 |
