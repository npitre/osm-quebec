# Québec : frontières et municipalités absentes d'OSM

Première étape de l'import : remplacer les limites municipales de tout
le Québec par celles du MRNF, par bouchées assez petites pour être
acceptées par OSM. Avant de commencer, deux vérifications : les
frontières du Québec avec ses voisins, et les municipalités du MRNF qui
n'ont pas de relation dans OSM. Rien n'a été envoyé à OSM.

Rapports générés par `outils/frontieres.py` :
[frontières](frontieres.md), avec leur carte
([frontieres.geojson](frontieres.geojson) : les points de la frontière
du MRNF à plus de 100 m du tracé d'OSM), et
[municipalités absentes](municipalites.md).

Données : Découpages administratifs du MRNF, version V2026-09, extrait
OSM de Geofabrik du 16 octobre 2026.

## 1. Frontières du Québec

En attendant d'en discuter, **les frontières extérieures existantes sont
gardées** : les municipalités qui les touchent reprendront les chemins
actuels de la relation du Québec, au lieu de tracer le MRNF par-dessus.

### Constat

Écart entre la frontière du MRNF et celle d'OSM (relation du Québec,
61549), en médiane et pour 90 % des points :

| Frontière | Médiane | 90 % à moins de |
|---|---|---|
| États-Unis | 0 m | 1 m |
| Nouveau-Brunswick | 11 m | 46 m |
| Ontario | 58 m | 193 m |
| Labrador, le long du 52e parallèle | 14 m | 80 m |
| Labrador, ligne de partage des eaux | 232 m | plus de 5 km |
| Nunavut | 189 m | 3,5 km |
| Golfe du Saint-Laurent | 44 m | 5,2 km |

- **États-Unis** : les deux tracés concordent. Aucun problème.
- **Nouveau-Brunswick** : bonne concordance, en rivière (Ristigouche,
  Patapédia) comme sur la ligne terrestre jusqu'au Maine, autour de
  10 m. Les deux tracés passent au milieu de la rivière, qui n'a que
  quelques dizaines de mètres de large. Les écarts de plus de 1 km sont
  dans l'estuaire, là où la rivière s'élargit vers la baie des Chaleurs.
- **Ontario** :
  - Dans la rivière des Outaouais, les deux tracés passent au milieu de
    l'eau, mais pas sur le même milieu : 60 m d'écart en médiane, plus
    de 200 m pour 10 % des points. Dans OSM, la frontière est sur un
    tiers de sa longueur l'axe même de la rivière (57 chemins
    `waterway=river`), ailleurs une ligne tracée à la main près de lui.
  - La ligne terrestre, du lac Témiscamingue à la baie James, n'est pas
    plus précise : dans OSM, c'est une ligne simplifiée, avec un nœud
    tous les 10 km environ entre les 49e et 51e parallèles, qui dérive
    jusqu'à 80 m vers l'est. L'écart n'est pas constant : ce n'est pas
    une différence de système de référence. Près de la baie James, les
    tracés s'écartent de 0,6 à 2 km.
- **Labrador** : le cas le plus délicat. Le long du 52e parallèle, la
  concordance est bonne (14 m en médiane), sauf par endroits (7 % des
  points à plus de 1 km). Le long de la ligne de partage des eaux, les
  tracés diffèrent souvent de plusieurs kilomètres. Une partie de cette
  frontière est toujours contestée par le Québec; aucun chemin d'OSM n'y
  porte d'étiquette `disputed*`, `note` ou `fixme`.
- **Nunavut et golfe du Saint-Laurent** : le Québec d'OSM s'arrête au
  littoral (820 de ses 1 358 chemins sont `natural=coastline`), alors
  que le MRNF suit une limite en mer. Ce sont deux conceptions
  différentes plutôt que des erreurs.

### Questions en suspens

1. **Ontario** : remplacer la frontière par le tracé du MRNF? À
   discuter avec les contributeurs ontariens, puisque la relation de
   l'Ontario partage ces chemins. Et, si la définition légale est le
   milieu de la rivière, faut-il que frontière et rivière partagent la
   même ligne? La règle 2 des régions (décidée à la rencontre du
   16 octobre) dit non : l'axe de la rivière est un tracé approximatif
   de l'écoulement, corrigé au fil des améliorations, alors que la
   frontière est une ligne officielle fixe; ici, les deux sont à 76 m
   l'une de l'autre en médiane. La question mérite toutefois d'être
   reposée.
2. **Nouveau-Brunswick** : même question, mais les écarts sont faibles;
   seul l'estuaire de la Ristigouche mérite un examen.
3. **Labrador** : garder le tracé actuel d'OSM; faut-il y ajouter une
   étiquette `disputed_by` ou une note là où le Québec conteste la
   frontière?
4. **Nunavut et golfe** : les municipalités côtières doivent-elles
   s'arrêter au littoral, comme aujourd'hui, ou suivre la limite en mer
   du MRNF, comme aux Îles-de-la-Madeleine?

## 2. Municipalités absentes d'OSM

Sur les 1 342 municipalités du MRNF, 1 243 ont une relation dans OSM
portant leur code (`ref:qc`). Les 99 autres :

- **52 TNO aquatiques** (les parties en eau de chaque MRC, comme dans la
  Petite-Nation).
- **29 réserves et établissements autochtones** (Kahnawake, Kanesatake,
  Kitigan Zibi, Manawan, Mashteuiatsh, etc.). Dans OSM, ces territoires
  sont généralement des `boundary=aboriginal_lands`, pas des limites
  administratives; à vérifier un par un.
- **8 territoires non organisés de la Jamésie** au nom « Toponyme à
  venir ».
- **Terres autochtones du Nord** : Killiniq et Kiggaluk (terres
  inuites), la terre réservée naskapie de Kawawachikamach, Oujé-Bougoumou
  (terre réservée crie).
- **Cas particuliers** :
  - La Pocatière : sa relation porte `ref:qc=14085`, le MRNF donne
    14082;
  - le village naskapi de Kawawachikamach : sa relation porte
    `ref:qc=99605`, le MRNF donne 99065 (deux chiffres inversés?);
  - La Romaine et Akwesasne : une relation existe, mais sans `ref:qc`;
  - Lac-Simon et Cacouna : les réserves de ce nom n'ont pas de relation,
    seulement les municipalités homonymes.

À l'inverse, trois relations d'OSM ont un code inconnu du MRNF :
Hébertville, Hébertville-Station et Saint-Bruno, au niveau 10, avec leur
ancien code. Elles ont fusionné dans la nouvelle municipalité
d'Hébertville (93022), qui a déjà sa relation : OSM garde ici les
anciennes municipalités au niveau 10, un précédent pour la question des
anciennes municipalités (Îles-de-la-Madeleine).

### Questions en suspens

5. **TNO aquatiques** : créer leur relation, ou laisser l'eau hors des
   municipalités comme aujourd'hui?
6. **Territoires autochtones** : les traiter comme des municipalités
   (relation `boundary=administrative`), ou garder
   `boundary=aboriginal_lands` et seulement vérifier leur tracé?
7. **TNO de la Jamésie** sans nom : attendre leur nom officiel?
