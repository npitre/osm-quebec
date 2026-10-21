# osmqc : importer les données officielles du Québec dans OpenStreetMap

Outils pour préparer, faire réviser et envoyer dans OpenStreetMap des
données ouvertes du gouvernement du Québec : adresses du Référentiel
québécois des adresses (RQA) et limites municipales des Découpages
administratifs (SDA), toutes deux du ministère des Ressources naturelles
et des Forêts (MRNF).

Le but est que la communauté puisse vérifier les **règles** appliquées
plutôt que de relire des milliers d'adresses une à une. Chaque
préparation produit des rapports de révision, lisibles sur GitHub
(voir Résultats).

Discussions : [compte-rendu de la rencontre du 16 octobre 2026](https://community.openstreetmap.org/t/148901),
[import du chemin du Gros-Cap](https://community.openstreetmap.org/t/148723).

## Résultats

État au 17 octobre 2026 (extrait OSM du 16 octobre). Rien n'a encore
été envoyé à OSM : ces résultats sont soumis à la révision de la
communauté. Pour chaque lieu, `rapports/LIEU/` contient :

- `README.md`, un commentaire rédigé : statistiques, exceptions à
  valider, questions en suspens;
- `regions.md`, `rues.md` et `adresses.md`, les rapports générés, avec
  leurs tableaux;
- les GeoJSON correspondants, que GitHub affiche sur une carte. Chaque
  objet porte ses propriétés (`statut` pour les adresses et les rues,
  `source` pour les limites, `coupure` pour les routes) : ce sont elles
  qui font foi. Les couleurs suivent la convention simplestyle, que tous
  les afficheurs ne respectent pas.

| Lieu | Municipalités | Limites : adresses mal placées dans OSM | Rues à renommer | Adresses prêtes | Adresses à revoir |
|---|---|---|---|---|---|
| [Îles-de-la-Madeleine](rapports/Iles_de_la_Madeleine/) | 2 | 3 sur 7 394 (0 après correction) | 28 segments | 7 221 | 129 |
| [La Petite-Nation (MRC de Papineau)](rapports/Petite-Nation/) | 25 | 23 sur 20 659 (0 après correction) | 45 segments | 19 430 | 1 544 |

## Licences

- Le code : licence MIT (fichier `LICENSE`).
- Les données d'entrée et leurs licences : voir
  [donnees/README.md](donnees/README.md).

## Installation

Python 3.11 ou plus récent, avec pyosmium (paquet `python3-osmium` de
Fedora ou Debian, ou `pip install osmium`). Les données sources
(RQA, Découpages administratifs, extrait d'OSM) ne sont pas incluses
dans ce dépôt, seulement les rapports de révision qui en découlent
(`rapports/`). La provenance des données sources, leur téléchargement et
leur organisation sont décrits dans [donnees/README.md](donnees/README.md).

## Utilisation

Chaque lieu est décrit par un fichier `lieux/LIEU.toml` (exemple :
`lieux/Iles_de_la_Madeleine.toml`). Trois sections, dans cet ordre :
les régions (limites municipales), les rues, les adresses (voir
« Ordre des étapes »).

```
python3 -m osmqc adresses extraire lieux/Iles_de_la_Madeleine.toml   # adresses du lieu, tirées du RQA

python3 -m osmqc regions comparer lieux/Iles_de_la_Madeleine.toml    # limites OSM contre MRNF
python3 -m osmqc regions preparer lieux/Iles_de_la_Madeleine.toml    # remplacement des limites
python3 -m osmqc regions envoyer lieux/Iles_de_la_Madeleine.toml --test

python3 -m osmqc adresses osm lieux/Iles_de_la_Madeleine.toml        # données OSM autour des adresses

python3 -m osmqc rues preparer lieux/Iles_de_la_Madeleine.toml       # noms de rue contre noms officiels
python3 -m osmqc rues envoyer lieux/Iles_de_la_Madeleine.toml --test

python3 -m osmqc adresses preparer lieux/Iles_de_la_Madeleine.toml   # import des adresses
python3 -m osmqc adresses envoyer lieux/Iles_de_la_Madeleine.toml --test
```

`--test` envoie au serveur de test d'OSM; `--reel` à OpenStreetMap, ce
qui est refusé tant que la discussion publique n'est pas inscrite dans
la section `groupe` correspondante du lieu. Pour l'authentification,
voir l'en-tête de `osmqc/envoi.py`.

Les fichiers d'envoi (`.osc`) et un CSV de toutes les adresses vont
dans `sortie/LIEU/` (hors du dépôt); les rapports de révision, dans
`rapports/LIEU/` (voir Résultats).

## Règles appliquées

### Ordre des étapes

1. **Les limites municipales** d'abord : la municipalité d'une adresse
   se déduit alors de la limite qui la contient. Nominatim et Photon
   (construit sur la base de Nominatim) utilisent les limites, mais
   rattachent chaque adresse à sa rue, et chaque chemin de rue à une
   seule municipalité : d'où la coupure des rues aux limites (voir
   Régions, règle 7). Pelias n'utilise ni les limites d'OSM ni
   `addr:city` (il prend Who's On First). OsmAnd n'utilise une limite que
   si elle est liée à son nœud de lieu (voir Régions, règle 8). Voir la
   [discussion sur les géocodeurs](https://community.openstreetmap.org/t/148901).
2. **Les rues** ensuite : une adresse n'est créée que si sa rue existe
   dans OSM sous son nom officiel. Les anciens noms ou noms alternatifs
   sont conservés dans les tags `old_name` et `alt_name`.
3. **Les adresses** enfin.

### Régions

1. **Les limites du MRNF ont préséance** sur celles d'OSM (Découpages
   administratifs, 1/20 000). OSM ne garde que 7 décimales de degré
   (environ 1 cm) : deux sommets du MRNF confondus à cette précision
   deviennent un seul nœud.
2. **Des chemins propres.** Une limite ne partage jamais ses nœuds avec
   le littoral, une route ou un cours d'eau, même quand elle les suit :
   déplacer l'un déplacerait l'autre. Les chemins de limite créés ne
   portent que `boundary=administrative` et `admin_level`.
3. **Une limite commune est un seul chemin**, membre des relations des
   deux municipalités (rôles `outer` et `inner` selon le cas).
4. **Contour extérieur** : un contour qui ne borde aucune autre
   municipalité du lieu et forme à lui seul un anneau fermé (le large,
   autour d'îles) peut reprendre les chemins d'une relation parente au
   lieu d'être tracé d'après le MRNF (`exterieur =` dans le lieu). Aux
   Îles, ce sont des limites interprovinciales en mer, reprises de la
   Communauté maritime. Un contour ouvert est toujours tracé d'après le
   MRNF, pour se raccorder aux limites voisines par les mêmes nœuds.
5. **Ce qui sort des relations** : le littoral et les autres objets sont
   seulement retirés des relations, sans être modifiés. Une simple ligne
   de limite qui ne sert plus à aucune relation est supprimée, avec ses
   nœuds s'ils ne servent à rien d'autre dans OSM. **Exception** : un
   chemin qui porte `note`, `fixme`, `description` ou une étiquette
   `disputed*` n'est jamais supprimé automatiquement (par exemple la
   frontière avec Terre-Neuve-et-Labrador, que le gouvernement du Québec
   considère comme non définitive) : il est signalé dans le rapport et
   traité à la main, et sa note est reportée sur le chemin qui le
   remplace. Les étiquettes des relations ne sont jamais modifiées;
   seuls leurs membres changent. Les frontières provinciales et
   internationales (`admin_level` 4 et 2) peuvent être réutilisées, mais
   ne sont jamais modifiées.
6. **Vérification** : le rapport compare la municipalité de chaque
   adresse du RQA selon le MRNF, les limites actuelles d'OSM et les
   limites proposées.
7. **Routes qui traversent les limites** : une route nommée est coupée
   exactement là où elle traverse une limite, même si ses étiquettes
   sont identiques des deux côtés. Raison : Nominatim (et donc Photon)
   lie chaque chemin de rue à une seule municipalité, et chaque adresse
   hérite de la municipalité de sa rue. Un nœud est ajouté sur la route
   au point de croisement, sans en modifier la géométrie, et le chemin
   est coupé en deux à ce nœud. Ce nœud n'est pas partagé avec le chemin
   de limite (voir la règle 2). Le rapport classe chaque croisement :
   déjà coupé, coupure à ajouter, coupure à déplacer, ou coupure devenue
   inutile (sur l'ancienne limite, entre deux segments aux étiquettes
   identiques). Une coupure à ajouter ou à déplacer est faite, et le
   nouveau segment prend place à côté de l'ancien dans les relations de
   route qui le contiennent; l'ancienne coupure, devenue inutile, est
   seulement signalée.
8. **Lien avec le nœud de lieu** : chaque relation municipale doit avoir
   un membre `label` (ou `admin_centre`) qui pointe vers un nœud `place`
   portant exactement le même `name` que la relation. Sans ce lien,
   OsmAnd n'utilise pas la limite pour attribuer les adresses. Les
   membres existants sont conservés; le rapport signale les relations
   sans lien ou dont les noms diffèrent.
9. **Chemins déjà conformes** : un chemin de limite existant (une simple
   ligne de limite, jamais un littoral, une route ou un cours d'eau)
   qui suit exactement le tracé du MRNF, mêmes sommets au 1e-7 degré
   près (la précision d'OSM), est gardé tel quel avec ses nœuds; les
   chemins neufs s'y raccordent. Une relation dont les membres ne
   changent pas n'est pas envoyée. Ainsi, relancer la préparation après
   un envoi ne produit plus rien : on peut reprendre un envoi
   interrompu, et vérifier qu'un envoi est bien passé. Un nœud existant
   pile au bout d'un arc du MRNF (un point triple déjà juste) est
   réutilisé s'il ne sert qu'à des lignes de limite.
10. **Voisines hors du lot** : les limites sont envoyées par lots, et
    chaque envoi doit laisser OSM valide. Une municipalité hors du lot
    qui le touche (une voisine, trouvée dans le MRNF, et sa relation par
    `ref:qc` ou par `[regions] voisines` dans le fichier du lieu) est
    donc modifiée en partie :
    - l'arc commun du MRNF devient un seul chemin, membre des deux
      relations;
    - les anciens chemins de la voisine qui longent le lot en sont
      retirés (supprimés s'ils ne servent plus à rien, règle 5);
    - un ancien chemin de limite qui ne longe le lot qu'en partie est
      coupé au dernier sommet gardé : raccourci s'il ne sert qu'à la
      voisine, sinon coupé en deux pour que ses autres relations (une
      aire protégée, par exemple) ne changent pas;
    - un littoral, une route ou un cours d'eau n'est jamais coupé ni
      modifié : la partie gardée en est recopiée dans un chemin de
      limite distinct (règle 2), et il est retiré de la voisine;
    - l'arc commun s'arrête au point triple du MRNF, la partie gardée
      de la voisine à l'ancien point triple d'OSM : un court chemin de
      raccord, membre de la voisine seule, les relie.

    Raccords et copies sont provisoires : quand la voisine est traitée
    à son tour, ses arcs avec le lot précédent sont reconnus comme
    conformes (règle 9), et raccords et copies, devenus de simples
    lignes de limite inutilisées, sont supprimés. Si l'anneau d'une
    voisine ne se refermerait pas, elle n'est pas touchée et le cas est
    signalé dans le rapport.

### Rues

1. **Nom officiel** : l'odonyme recomposé du RQA (repris de la
   Commission de toponymie), dans l'ordre usuel (« 4e Rang Sud »), sans
   le discriminant des municipalités fusionnées (« Chemin du Gros-Cap »
   et non « Chemin du Gros-Cap (L'Étang-du-Nord) »). Le discriminant
   correspond en général à la localité postale (Postes Canada). Selon le
   wiki, c'est le rôle d'`addr:city` (la ville de l'adresse postale), et
   non de `contact:*`, qui sert à une adresse de contact différente de
   l'adresse physique. Son ajout est à décider (voir Adresses, règle 6).
   Les abréviations du RQA sont remplacées par la forme complète
   (« St- » devient « Saint- »), selon la règle d'OSM
   ([Abbreviations](https://wiki.openstreetmap.org/wiki/Abbreviations)).
2. **Renommage automatique** seulement quand le nom d'OSM ne diffère du
   nom officiel que par la casse, les accents, les tirets, les espaces
   ou une abréviation (« Chemin de la Martinique » devient « Chemin de
   La Martinique », « Rue St. Andrew » devient « Rue Saint-Andrew »).
   Tous les segments reliés qui portent ce nom sont renommés, trottoirs
   compris, même loin des adresses; une rue homonyme qui n'y est pas
   reliée n'est pas touchée. Un renommage garde `alt_name` et
   `old_name`; l'ancien nom s'ajoute à `old_name` s'il diffère
   autrement que de ces façons (donc seulement pour un renommage
   décidé à la main), et s'il n'est pas déjà gardé.
3. **Autres écarts, rapportés seulement** : une voie proche qui porte un
   autre nom, une voie sans nom le long des adresses (candidate pour
   recevoir le nom officiel), ou aucune voie. Ils se règlent à la main ou
   par une section `[[rues.modifier]]` du lieu.
4. La préparation des adresses tient compte des renommages prévus.

### Adresses

1. **Une adresse par numéro de base et par rue.** Le RQA répète le
   point pour chaque logement d'un immeuble (2-1701, 329 1) : seul le
   numéro de base est créé. Les numéros de logement (2-1701, 329 1)
   vont dans `addr:unit`, séparés par « ; », sauf les logements
   douteux (voir « Logements douteux du RQA »). Un suffixe en lettre
   (120A) au même point que son numéro de base est fusionné et ajouté
   à `addr:housenumber` (« 120;120A;120B »); placé à plus de 5 m, il
   devient une adresse distincte. Le numéro de base n'est ajouté que
   s'il existe au RQA : 120A et 120B sans 120 donnent « 120A;120B ».
   À valider : un suffixe en lettre que Postes Canada traite comme un
   logement devrait aller dans `addr:unit` plutôt que dans
   `addr:housenumber`.
2. **Adresses terminées** (`date_fin` remplie) : ignorées.
3. **Exclusions** : une liste explicite, avec la raison, dans le fichier
   du lieu (par exemple une adresse absente du rôle d'évaluation).
4. **La rue doit exister dans OSM** sous exactement son nom officiel
   (voir Rues), à moins de 300 m. Sinon, l'adresse n'est pas créée et
   passe « à revoir » : rue absente, sans nom ou écrite autrement dans
   OSM. Les rues se corrigent d'abord, les adresses suivent.
5. **Doublons** : une adresse OSM au même numéro, à moins de 30 m (ou
   un bâtiment ou terrain qui contient le point), n'est pas recréée.
   On y corrige `addr:street` s'il diffère du nom officiel et on y
   ajoute `addr:postcode` s'il manque. Rien d'autre n'est touché.
6. **Étiquettes créées** : `addr:housenumber`, `addr:street`,
   `addr:postcode`. `addr:city` : à décider par la communauté. Aucun
   géocodeur courant n'en a besoin pour trouver la municipalité, qui
   vient des limites. S'il est ajouté, ce sera la localité postale de
   Postes Canada (définition du wiki), pas la municipalité officielle;
   Nominatim l'ajoute alors aux termes de recherche de l'adresse. Pas
   d'identifiant du RQA dans OSM (sauf si la communauté décide de
   l'inclure).
7. **Interpolations CanVec** : une ligne `addr:interpolation` est
   supprimée avec ses nœuds, puisque les vraies adresses la remplacent,
   si ses deux extrémités portent le nom d'une rue importée, si elle passe
   à moins de 300 m d'une adresse de cette rue, si CanVec l'attribue à
   une municipalité du lieu, et si ses nœuds ne servent à rien d'autre et
   ne portent que des étiquettes CanVec.
8. **Position** : le point du RQA, sauf si une source plus précise est
   donnée, par exemple les portes d'entrée placées à la main par la
   Chaire Mobilité (voir « Le fichier d'un lieu »). Ce point est ignoré
   si la même unité d'évaluation porte plusieurs numéros (la porte ne dit
   pas lequel); les logements d'un même numéro partagent la porte. Un
   point d'un GeoJSON est aussi ignoré s'il est trop loin du point du RQA
   (150 m par défaut); une porte de la Chaire Mobilité, vérifiée à la
   main, est gardée même loin du RQA, dont les points sont parfois
   décalés d'un terrain, et signalée dans le rapport. Un point ignoré
   sera corrigé manuellement plus tard. Le rapport
   indique la source retenue pour chaque adresse. Une étiquette
   `entrance=*` n'est ajoutée que si le point de cette source est sur le
   contour d'un bâtiment (à moins de 1 m) : `home` pour une adresse
   résidentielle ou de villégiature du RQA, `shop` pour un commerce,
   `main` sinon.

### Logements douteux du RQA

Certains logements du RQA ne correspondent à rien sur le terrain : des
numéros d'unité bizarres (36A, 3511, 9999) sur des propriétés qui n'ont
qu'un seul logement. Par exemple, le logement 9999-2225 chemin du
Lac-Gagnon Ouest, à Duhamel. Ils ne sont pas mis dans `addr:unit`.

**Règle.** Un logement est douteux s'il n'a ni lot ni matricule, et que
son adresse principale n'a qu'un seul logement selon le rôle
d'évaluation (champ `nombre_unite` du RQA) : rien ne le confirme, et le
rôle le contredit. Il est gardé s'il a un lot ou un matricule, si
l'immeuble compte plusieurs logements, ou si son numéro n'a pas
d'adresse principale ou pas de nombre de logements connu.

**Origine.** La plupart ont été ajoutés au RQA d'un seul coup, le
11 décembre 2021 à 20 h 15, dans un chargement d'environ 890 000 unités
pour tout le Québec. La règle ne repose pas sur cette date : le même
chargement contient aussi des logements valables (dans des immeubles que
le rôle compte à 6, 30 ou 54 logements), et des cas semblables viennent
d'autres chargements. À Duhamel, elle retrouve 62 des 64 unités
signalées.

**Signalement au MRNF.** Le 13 octobre 2026, 64 de ces logements, à
Duhamel, ont été signalés au MRNF (Géoboutique), qui a transmis la
demande à l'équipe responsable du RQA. Les autres régions restent à
signaler : la section « Logements douteux » du rapport des adresses de
chaque lieu en donne la liste, avec l'identifiant du RQA. Une version
corrigée du RQA les fera disparaître de cette liste.

**Effet.** Aucune adresse n'est perdue : seul un faux `addr:unit` est
évité. La règle se désactive par `ecarter_logements_douteux = false`
dans la section `[adresses]` du lieu.

### Groupe de modifications

Chaque envoi porte `import=yes`, `source=` (la source et sa version),
le commentaire et le lien de la discussion publique. Un envoi est pour
l'instant un seul groupe (voir « À automatiser » pour le découpage).

## Traiter une nouvelle région

1. **Créer le fichier du lieu**, `lieux/NOM.toml`. Son nom (sans
   `.toml`) sert partout : `donnees/NOM/`, `sortie/NOM/`,
   `rapports/NOM/`. Choisir les municipalités, soit toutes celles d'une
   MRC (`mrc = "80"` dans `[regions]`), soit une liste de codes
   géographiques (`municipalites` dans `[rqa]`). Les codes viennent des
   Découpages administratifs du MRNF.
2. **Trouver les relations OSM** des municipalités :
   `python3 -m osmqc regions trouver lieux/NOM.toml` affiche la section
   `[regions.osm]` à copier dans le fichier. Une municipalité sans
   relation, ou rattachée ailleurs dans OSM, y est signalée.
3. **Lancer les étapes** dans l'ordre de la section Utilisation :
   extraction, régions, données OSM, rues, adresses.
4. **Lire les rapports** générés dans `rapports/NOM/` et ajouter au
   besoin des exclusions ou des renommages décidés à la main
   (`exclure`, `[[rues.modifier]]`), puis relancer.
5. **Rédiger le commentaire** `rapports/NOM/README.md` (statistiques,
   exceptions à valider, questions en suspens) et ajouter le lieu au
   tableau des Résultats.

### Le fichier d'un lieu

Toutes les sections possibles, d'après l'exemple des Îles (l'exclusion
vient de la Petite-Nation) :

```toml
nom = "Les Îles-de-la-Madeleine"

[rqa]
municipalites = ["01023", "01042"]   # codes géographiques
# odonymes = ["178477"]              # seqodo, pour se limiter à certaines rues

[regions]
# mrc = "80"                         # à la place de [rqa] municipalites : toute la MRC
osm = { "01023" = 8402197, "01042" = 8402196 }   # relations OSM à remplacer
exterieur = 8405826                  # facultatif : relation parente réutilisée

[regions.groupe]
comment = "Limites municipales d'après les Découpages administratifs du MRNF"
source = "Découpages administratifs (MRNF), version V2026-09"
discussion = "https://community.openstreetmap.org/t/..."

[adresses]
supprimer_interpolations = true
corriger_rue_existante = true
creer_si_rue_absente = false
ecarter_logements_douteux = true     # voir « Logements douteux du RQA »
exclure = [ { municipalite = "80135", rue = "Chemin du Tour-du-Lac", numero = "131", raison = "absent du rôle" } ]

[adresses.positions]                 # facultatif : positions plus précises
fichier = "donnees/Iles_de_la_Madeleine/portes.csv"   # CSV ou GeoJSON, voir plus bas
# propriete = "matricule"            # GeoJSON : propriété qui sert de clé
# cle_rqa = "id_provinc"             # ou matricule, lot, ident, adresse
ecart_max_m = 150                    # GeoJSON seulement
nom = "portes"

[[rues.modifier]]                    # renommages décidés à la main
type = "way"
id = 1221212557
tags = { name = "Chemin de Gros-Cap", alt_name = "Chemin du Gros-Cap" }
raison = "nom officiel du tronçon de Cap-aux-Meules"

[adresses.groupe]
comment = "Adresses des Îles-de-la-Madeleine d'après le Référentiel québécois des adresses"
source = "Référentiel québécois des adresses (MRNF), version AQ20261001"
discussion = "https://community.openstreetmap.org/t/..."
```

Le CSV est celui du rôle d'évaluation corrigé par la Chaire Mobilité
(outil address_integrator) : une ligne par unité d'évaluation, avec
`id_provinc` (code de municipalité et matricule), `geog` (point en WKT,
EWKT ou EWKB hexadécimal, comme l'écrit PostGIS),
`geog_changed_entrance_aligned`, `geog_approximate` et `is_ignored`.
Seuls les points placés sur la porte, ni approximatifs ni ignorés, sont
retenus. Un point approximatif est une porte que la Chaire Mobilité n'a
pu déterminer avec certitude; son erreur maximale
(`geog_approximate_max_error_distance_m`, pas encore disponible pour
toutes les régions) pourra servir plus tard à en accepter certains. Un
GeoJSON de points est relié au RQA par la propriété
`propriete`.

## Durées et usage des serveurs

Les données d'OSM sont lues dans un extrait local du Québec
(`.osm.pbf`, voir [donnees/README.md](donnees/README.md)), avec pyosmium,
plutôt que demandées à l'API d'OSM : les règles d'usage de l'API
découragent les téléchargements en masse. L'API ne sert plus qu'à de
petites lectures groupées : la version actuelle des objets à modifier,
juste avant d'écrire le fichier d'envoi. Sans extrait, l'outil se
rabat sur l'API pour une très petite zone seulement (au plus 20
tuiles) et refuse au-delà. Avec `OSMQC_HORS_LIGNE=1`, l'API n'est
jamais appelée : même les versions actuelles des objets sont lues dans
l'extrait (c'est le mode des tests de bout en bout).

Mesures du 17 octobre 2026, avec l'extrait :

| Étape | Îles (7 400 adresses) | Petite-Nation (21 000 adresses) |
|---|---|---|
| Téléchargement de l'extrait du Québec (1,2 Go, Geofabrik) | ~1 min | (le même) |
| Téléchargement du RQA et des découpages (MRNF) | de 30 min à quelques heures, une fois | (les mêmes) |
| `adresses extraire` | ~40 s | ~40 s |
| `adresses osm` | ~55 s | ~55 s |
| `regions trouver` | ~1 s | ~1 s |
| `regions preparer` | ~2 min | ~2 min |
| `rues preparer` | ~20 s | ~20 s |
| `adresses preparer` | ~5 s | ~10 s |

La lecture de l'extrait prend environ 4 Go de mémoire. Chaque étape
relit l'extrait en entier une ou plusieurs fois : la durée dépend peu de
la taille du lieu.

Avant de préparer un envoi, mettre l'extrait à jour sur place avec les
changements publiés par OSM (quelques minutes) :

```
pyosmium-up-to-date donnees/quebec-latest.osm.pbf
```

## À automatiser

Liste au 21 octobre 2026, par ordre de priorité.

### Avant tout envoi

1. **Découper les gros envois.** L'API d'OSM refuse un groupe de
   modifications de plus de 10 000 objets; celui des adresses de la
   Petite-Nation en compte environ 72 000 (créations et suppressions
   d'interpolations). Pour les limites : une région administrative comme
   lieu, envoyée par bouchées de municipalités voisines, chacune
   laissant OSM valide (règle 10 des régions). Même chose pour les
   adresses, avec la même discussion inscrite sur chaque groupe.
2. **Enchaîner les bouchées.** Après chaque envoi, appliquer à
   l'extrait local ce qui vient d'être envoyé, avec les identifiants et
   versions renvoyés par l'API (`extrait.appliquer` est prêt), puis
   préparer la bouchée suivante. Une relance ne prépare déjà que ce qui
   reste (règle 9), ce qui règle la reprise après un envoi interrompu.
3. **Fraîcheur de l'extrait.** Lancer `pyosmium-up-to-date`
   automatiquement, ou refuser de préparer un envoi à partir d'un extrait
   trop vieux.

### Régions

4. **Coupures devenues inutiles** : fusionner les deux segments d'une
   route coupée sur l'ancienne limite (aujourd'hui seulement signalées).
5. **Relation de la MRC** : la reconstruire à partir des limites
   extérieures de ses municipalités, pour éviter les tracés doubles le
   long du contour.
6. **Relations manquantes ou mal rattachées** : créer celles qui
   n'existent pas (TNO aquatique), vérifier que chaque municipalité est
   membre de la bonne MRC (Notre-Dame-de-la-Salette).
7. **Anciennes municipalités** (niveau 9 ou 10) : simple à coder, mais il
   manque une source autorisée pour les tracés.
8. **Route qui finit sur la limite** : classée « coupure à ajouter »
   alors qu'il n'y a rien à couper (chemin des Joyeux-Sportifs, dans la
   Petite-Nation).
9. **Durée** : la préparation des limites de la Petite-Nation lit
   l'extrait du Québec en entier plusieurs fois (voisines, usage des
   chemins et des nœuds) et prend environ 5 minutes; tout lire en un
   seul passage.

### Rues

10. **Nommer les voies sans nom** quand une seule voie dessert toutes les
    adresses d'une rue, si la communauté accepte la règle.
11. **`addr:place`** pour les adresses sans rue (Île du Canard-Blanc).

### Adresses

12. **Portes d'entrée** de la Chaire Mobilité : l'outil lit son CSV, il
    manque les données.
13. **Interpolations** : ne supprimer une ligne que si sa rue reçoit
    vraiment des adresses (aujourd'hui, une rue « à revoir » peut perdre
    son interpolation sans rien recevoir).
14. **Anomalies du RQA** : les logements douteux sont déjà listés (voir
    « Logements douteux du RQA »). Reste à lister, pour les
    signalements au MRNF, les adresses absentes du rôle d'évaluation
    (comme le 34 chemin de la Pointe-à-Baptiste, à Duhamel), à partir
    du rôle géoréférencé du ministère des Affaires municipales et de
    l'Habitation (MAMH), qui a lui aussi donné une [permission
    explicite pour OSM](https://wiki.openstreetmap.org/wiki/FR:Minist%C3%A8re_des_Affaires_municipales_et_de_l%27Habitation).

## Tests

```
python3 -m unittest discover tests
```

Aucun test n'a besoin de données téléchargées ni d'accès réseau. Il y
a au moins un test par règle de ce document, et un essai de bout en
bout sur Lac-Témoin, une région fictive : voir
[tests/README.md](tests/README.md).
