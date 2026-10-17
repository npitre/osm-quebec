# Noms de rue : cohérence entre OSM et les odonymes officiels du RQA
# (qui reprennent ceux de la Commission de toponymie).
#
# Étape entre les régions et les adresses : une adresse n'est créée que
# si sa rue existe dans OSM sous exactement le même nom.
#
# Règles :
# - une rue d'OSM dont le nom ne diffère du nom officiel que par la
#   casse, les accents, les tirets ou les espaces est renommée (tous ses
#   segments, y compris les trottoirs qui portent son nom);
# - les autres écarts (nom différent, rue sans nom) sont seulement
#   rapportés, avec les candidats, pour être réglés à la main.

from collections import Counter, defaultdict
from dataclasses import dataclass, field

from . import geo
from .adresses import cle_nom

PROCHE_M = 300      # segments de rue pris en compte autour des adresses
SANS_NOM_M = 60     # voie sans nom candidate : à moins de 60 m d'une adresse


@dataclass
class Rue:
    officiel: str
    municipalite: str
    adresses: int
    statut: str = ""                 # conforme, à renommer, autre nom, sans nom, absente
    noms_osm: Counter = field(default_factory=Counter)   # nom dans OSM -> segments
    renommer: list = field(default_factory=list)          # ids de chemins
    candidats: list = field(default_factory=list)         # (id, highway, adresses, nom OSM)


def segments_nommes(index):
    """Routes et chemins nommés : {clé du nom: [ids]}."""
    res = defaultdict(list)
    for w in index.chemins.values():
        t = w.get("tags", {})
        if "highway" in t and "name" in t:
            res[cle_nom(t["name"])].append(w["id"])
    return res


def etendre(index, ids, nom):
    """Tous les segments de même nom reliés aux segments donnés, pour
    renommer la rue d'un bout à l'autre."""
    par_noeud = defaultdict(list)
    for w in index.chemins.values():
        if w.get("tags", {}).get("name") == nom and "highway" in w["tags"]:
            for n in (w["nodes"][0], w["nodes"][-1]):
                par_noeud[n].append(w["id"])
    vus = set(ids)
    pile = list(ids)
    while pile:
        w = index.chemins[pile.pop()]
        for n in (w["nodes"][0], w["nodes"][-1]):
            for v in par_noeud[n]:
                if v not in vus:
                    vus.add(v)
                    pile.append(v)
    return sorted(vus)


def analyser(adresses, index):
    """Compare chaque rue du RQA avec OSM. Renvoie [Rue]."""
    par_rue = defaultdict(dict)     # une adresse par numéro de base
    for a in adresses:
        if not a.fin:
            par_rue[(a.municipalite, a.rue)].setdefault(a.numero, a.point)
    par_rue = {k: list(v.values()) for k, v in par_rue.items()}
    nommes = segments_nommes(index)
    lignes = {}

    def ligne(w):
        if w not in lignes:
            lignes[w] = index.ligne(w)
        return lignes[w]

    voies = [w for w in index.chemins.values()
             if w.get("tags", {}).get("highway") in ("residential", "service", "unclassified", "track",
                                                    "tertiary", "secondary", "primary", "trunk",
                                                    "living_street", "road")]
    grille = geo.Grille([ligne(w["id"]) for w in voies if len(ligne(w["id"])) > 1])
    proprio = {}
    for w in voies:
        l = ligne(w["id"])
        for a, b in zip(l, l[1:]):
            proprio[(a, b)] = w["id"]

    def plus_proche(p):
        meilleur = None
        for c in grille._cases(p[0] - 0.001, p[1] - 0.001, p[0] + 0.001, p[1] + 0.001):
            for sg in grille.cases.get(c, ()):
                d = geo.distance_segment(p, sg[0], sg[1])
                if d < SANS_NOM_M and (meilleur is None or d < meilleur[0]):
                    meilleur = (d, proprio.get(sg))
        return meilleur[1] if meilleur else None

    res = []
    for (mun, nom), pts in sorted(par_rue.items()):
        r = Rue(nom, mun, len(pts))
        proches = [w for w in nommes.get(cle_nom(nom), [])
                   if len(ligne(w)) > 1 and min(geo.distance_ligne(p, ligne(w)) for p in pts[:50]) < PROCHE_M]
        for w in proches:
            r.noms_osm[index.chemins[w]["tags"]["name"]] += 1
        if proches and set(r.noms_osm) == {nom}:
            r.statut = "conforme"
        elif proches:
            r.statut = "à renommer"
            for osm_nom in r.noms_osm:
                if osm_nom != nom:
                    r.renommer += etendre(index, [w for w in proches
                                                  if index.chemins[w]["tags"]["name"] == osm_nom], osm_nom)
            r.renommer = sorted(set(r.renommer))
        else:
            # La voie la plus proche de chaque adresse : sans nom, ou
            # portant un autre nom.
            compte = Counter(w for w in map(plus_proche, pts) if w)
            r.candidats = [(w, index.chemins[w]["tags"]["highway"], n,
                            index.chemins[w]["tags"].get("name", "")) for w, n in compte.most_common(5)]
            if not r.candidats:
                r.statut = "absente"
            elif r.candidats[0][3]:
                r.statut = "autre nom"
            else:
                r.statut = "sans nom"
        res.append(r)
    return res


def plan_renommage(rues):
    """{id de chemin: nom officiel}, en refusant les conflits (un même
    chemin réclamé par deux noms officiels différents)."""
    voulu = defaultdict(set)
    for r in rues:
        for w in r.renommer:
            voulu[w].add(r.officiel)
    conflits = {w: n for w, n in voulu.items() if len(n) > 1}
    return {w: n.pop() for w, n in voulu.items() if len(n) == 1}, conflits


def etiquettes_renommage(actuelles, nouveau, demandees=None):
    """Étiquettes à poser pour renommer une voie. Les noms existants ne se
    perdent pas : alt_name et old_name restent tels quels, et l'ancien
    nom passe dans old_name s'il diffère du nouveau autrement que par la
    casse ou les accents (inutile de garder « Chemin de la Martinique »
    pour « Chemin de La Martinique ») et n'est pas déjà conservé ailleurs.
    actuelles : étiquettes actuelles de la voie; demandees : étiquettes
    décidées à la main (section [[rues.modifier]])."""
    tags = dict(demandees or {})
    tags["name"] = nouveau
    ancien = actuelles.get("name")
    if not ancien or cle_nom(ancien) == cle_nom(nouveau):
        return tags
    gardes = set()
    for k in ("alt_name", "old_name"):
        for source in (actuelles, tags):
            gardes.update(v for v in (source.get(k) or "").split(";") if v)
    if ancien not in gardes:
        tags["old_name"] = ";".join([v for v in (tags.get("old_name") or actuelles.get("old_name") or "").split(";") if v] + [ancien])
    return tags


def appliquer(index, plan):
    """Applique en mémoire des renommages {chemin: nom}, pour préparer les
    adresses comme si les rues étaient déjà renommées."""
    for w, nom in plan.items():
        if w in index.chemins:
            index.chemins[w].setdefault("tags", {})["name"] = nom
