# Règles de préparation d'un import d'adresses du RQA dans OSM.
#
# Le résultat est un « plan » : nœuds à créer, objets existants à
# corriger, lignes d'interpolation à supprimer, et un rapport ligne par
# ligne pour la révision. Les règles sont décrites dans le README.

import re
import unicodedata
from collections import defaultdict
from dataclasses import dataclass, field

from . import geo
from .rqa import developper

DOUBLON_M = 30          # adresse OSM existante au même numéro à moins de 30 m
SUFFIXE_DISTINCT_M = 5  # un suffixe plus loin que ça de son numéro de base est une adresse à part
RUE_PROCHE_M = 300      # distance maximale entre l'adresse et une rue du même nom dans OSM


def cle_nom(nom):
    """Forme de comparaison d'un nom de rue : sans accents, casse,
    tirets ni apostrophes (« Chemin du Gros Cap » = « Chemin du Gros-Cap »),
    abréviations développées (« Rue St. Andrew » = « Rue Saint-Andrew »)."""
    s = unicodedata.normalize("NFD", developper(nom or "")).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]", "", s.lower())


@dataclass
class Ligne:
    """Une ligne du rapport de révision."""
    municipalite: str
    rue: str
    numero: str
    code_postal: str
    lon: float
    lat: float
    qualite: str
    statut: str          # nouveau, existant, corrigé, exclu, à revoir
    detail: str = ""
    position: str = "RQA"  # source de la position retenue


@dataclass
class Plan:
    creer: list = field(default_factory=list)       # (tags, (lon, lat))
    modifier: dict = field(default_factory=dict)    # (type, id) -> {clé: valeur}
    raisons: dict = field(default_factory=dict)     # (type, id) -> [texte]
    supprimer_chemins: list = field(default_factory=list)
    supprimer_noeuds: list = field(default_factory=list)
    rapport: list = field(default_factory=list)
    douteux: list = field(default_factory=list)     # (logement, adresse de base)

    def corriger(self, genre, ident, tags, raison):
        self.modifier.setdefault((genre, ident), {}).update(tags)
        self.raisons.setdefault((genre, ident), []).append(raison)


def regrouper(adresses):
    """Une adresse par numéro de base et par rue. Les logements (2-1701,
    329 1) et les suffixes en lettre au même point que leur numéro de base
    y sont fusionnés; un suffixe en lettre placé ailleurs devient une
    adresse à part (120A). Renvoie {(municipalité, odonyme, numéro
    affiché): (Adresse, [autres])}."""
    groupes = defaultdict(list)
    for a in adresses:
        groupes[(a.municipalite, a.odonyme, a.numero)].append(a)
    res = {}
    for (mun, odo, num), lst in groupes.items():
        base = next((a for a in lst if a.principale), lst[0])
        autres = []
        for a in lst:
            if a is base:
                continue
            if a.suffixe and not a.logement and geo.distance(a.point, base.point) > SUFFIXE_DISTINCT_M:
                res[(mun, odo, num + a.suffixe)] = (a, [])
            else:
                autres.append(a)
        res[(mun, odo, num)] = (base, autres)
    return res


def _ordre(v):
    m = re.match(r"(\d*)(.*)", v)
    return (int(m.group(1) or 0), m.group(2))


def numeros(num, base, autres):
    """Étiquettes de numéro d'une adresse fusionnée : addr:housenumber
    avec les suffixes en lettre (« 120;120A;120B »), et addr:unit avec les
    logements (« 1;2;3 »), ou None s'il n'y en a pas."""
    groupe = [base] + list(autres)
    lettres = sorted({a.numero + a.suffixe for a in groupe if a.suffixe and not a.logement}, key=_ordre)
    logements = sorted({a.logement for a in groupe if a.logement}, key=_ordre)
    numero = ";".join([num] + [l for l in lettres if l != num])
    return numero, ";".join(logements) or None


def logement_douteux(base, a):
    """Logement que rien ne confirme : ni lot ni matricule, sur une
    adresse principale qui, selon le rôle d'évaluation (nombre_unite du
    RQA), n'a qu'un logement. Exemple : 9999-2225 chemin du Lac-Gagnon
    Ouest (Duhamel). Sans adresse principale ou sans nombre de
    logements connu, on ne juge pas."""
    return bool(a.logement and not a.lot and not a.matricule and base.principale
                and base.nombre_unite.isdigit() and int(base.nombre_unite) <= 1)


SUR_CONTOUR_M = 1       # une position à moins de 1 m du contour d'un bâtiment est une porte
ENTREES = {"RESI": "home", "VILL": "home", "COMM": "shop"}


def entree(categorie):
    """Valeur d'entrance=* selon la catégorie d'utilisation du rôle."""
    return ENTREES.get(categorie, "main")


def contours_batiments(index):
    """Grille des contours de bâtiments, pour reconnaître une porte."""
    return geo.Grille([index.ligne(w["id"]) for w in index.chemins.values()
                       if "building" in w.get("tags", {}) and len(w["nodes"]) > 3])


INTERPOLATION_M = 300   # une interpolation remplacée est près d'adresses de sa rue


def interpolations(index, noms, rapport, points=None, villes=None):
    """Lignes d'interpolation (CanVec) des rues importées : celles dont
    les deux extrémités portent addr:street d'une de ces rues et qui
    passent à moins de INTERPOLATION_M d'une adresse de cette rue (une
    rue du même nom ailleurs n'est pas touchée). Elles ne sont
    supprimées que si leurs nœuds ne servent à rien d'autre.
    points : {clé de nom: [points des adresses]}; villes : clés des noms
    des municipalités du lieu."""
    cles = {cle_nom(n) for n in noms}
    grilles = {k: geo.Grille([[p, p] for p in pts], pas=0.01) for k, pts in (points or {}).items()}
    usage = defaultdict(int)
    for w in index.chemins.values():
        for n in w["nodes"]:
            usage[n] += 1
    chemins, noeuds = [], set()
    for w in index.chemins.values():
        if "addr:interpolation" not in w.get("tags", {}):
            continue
        bouts = [index.noeuds.get(n, {}).get("tags", {}) for n in (w["nodes"][0], w["nodes"][-1])]
        if not all(cle_nom(t.get("addr:street")) in cles for t in bouts):
            continue
        cle = cle_nom(bouts[0].get("addr:street"))
        # Une ligne attribuée par CanVec à une autre municipalité reste.
        if villes and any(t.get("addr:city") and cle_nom(t["addr:city"]) not in villes for t in bouts):
            continue
        if points is not None:
            g = grilles.get(cle)
            ligne = index.ligne(w["id"])
            if not g or not any((g.distance(p, rayon_deg=0.004) or 1e9) < INTERPOLATION_M
                                for p in ligne[::max(1, len(ligne) // 10)] + ligne[-1:]):
                continue
        propres = all(usage[n] == 1 for n in w["nodes"]) and all(
            not index.noeuds.get(n, {}).get("tags")
            or index.noeuds[n]["tags"].get("source", "").startswith("NRCan-CanVec")
            for n in w["nodes"])
        if not propres or any(n not in index.noeuds for n in w["nodes"]):
            p = index.ligne(w["id"])[0]
            rapport.append(Ligne("", bouts[0].get("addr:street", ""), "", "", p[0], p[1], "",
                                 "à revoir", "interpolation %d gardée : nœuds partagés ou "
                                 "étiquettes inattendues" % w["id"]))
            continue
        chemins.append(w["id"])
        noeuds.update(w["nodes"])
    return chemins, noeuds


def existantes(index, ignorer):
    """Adresses déjà dans OSM, par numéro : (objet, point ou contour)."""
    res = defaultdict(list)
    for e in index.tous():
        t = e.get("tags", {})
        if "addr:housenumber" not in t or "addr:interpolation" in t:
            continue
        if e["type"] == "node":
            if e["id"] in ignorer:
                continue
            res[t["addr:housenumber"]].append((e, [(e["lon"], e["lat"])]))
        elif e["type"] == "way":
            contour = [index.point(n) for n in e["nodes"] if n in index.noeuds]
            if contour:
                res[t["addr:housenumber"]].append((e, contour))
    return res


def correspondance(existants, numero, point):
    """Objet OSM au même numéro : nœud à moins de DOUBLON_M, ou contour
    fermé (bâtiment, terrain) qui contient le point ou en est proche."""
    for e, pts in existants.get(numero, []):
        if len(pts) == 1:
            if geo.distance(pts[0], point) < DOUBLON_M:
                return e
        elif pts[0] == pts[-1] and len(pts) > 3:
            if geo.dedans(point, [pts]) or geo.distance_ligne(point, pts) < DOUBLON_M:
                return e
    return None


def rues_osm(index):
    """Lignes des rues d'OSM, par forme de comparaison du nom :
    {clé: [(nom exact, ligne)]}."""
    res = defaultdict(list)
    for w in index.chemins.values():
        t = w.get("tags", {})
        if "highway" in t and "name" in t:
            for k in ("name", "alt_name", "old_name"):
                if k in t:
                    res[cle_nom(t[k])].append((t[k], w["id"]))
    return res


def preparer(adresses, index, conf, positions=None):
    """Construit le plan d'import. conf : section [adresses] du lieu.
    positions : source de positions plus précises (positions.Positions),
    sinon le point du RQA."""
    plan = Plan()
    # Exclusions : municipalité, rue et numéro (la rue est obligatoire :
    # un même numéro existe sur bien des rues).
    exclus = {}
    for x in conf.get("exclure", []):
        if "rue" not in x:
            raise SystemExit("Exclusion sans rue : %s" % x)
        exclus[(x["municipalite"], cle_nom(x["rue"]), x["numero"])] = x.get("raison", "")
    gardees = []
    for a in adresses:
        if a.fin:
            continue
        cle = (a.municipalite, cle_nom(a.rue), a.numero)
        if cle in exclus:
            if a.principale:
                plan.rapport.append(Ligne(a.municipalite, a.rue, a.numero, a.code_postal, a.lon,
                                          a.lat, a.qualite, "exclu", exclus[cle]))
            continue
        gardees.append(a)
    groupes = regrouper(gardees)
    noms = {a.rue for a in gardees}

    if conf.get("supprimer_interpolations", True):
        pts = defaultdict(list)
        for a in gardees:
            pts[cle_nom(a.rue)].append(a.point)
        villes = {cle_nom(a.nom_municipalite) for a in gardees}
        plan.supprimer_chemins, ignorer = interpolations(index, noms, plan.rapport, pts, villes)
        plan.supprimer_noeuds = sorted(ignorer)
    else:
        ignorer = set()
    deja = existantes(index, ignorer)
    rues = rues_osm(index)
    batiments = contours_batiments(index) if positions else None
    if hasattr(positions, "associer"):
        positions.associer(gardees)
    corriger_rue = conf.get("corriger_rue_existante", True)

    for (mun, odo, num), (a, autres) in sorted(
            groupes.items(), key=lambda kv: (kv[0][0], kv[1][0].rue, int(re.match(r"\d*", kv[0][2]).group() or 0), kv[0][2])):
        point, source, remarque = positions.position(a) if positions else (a.point, "RQA", "")
        if conf.get("ecarter_logements_douteux", True):
            douteux = [x for x in autres if logement_douteux(a, x)]
            autres = [x for x in autres if x not in douteux]
            plan.douteux += [(x, a) for x in douteux]
        else:
            douteux = []
        # La rue doit exister dans OSM sous le même nom, tout près.
        proches = [(nom, wid) for nom, wid in rues.get(cle_nom(a.rue), [])
                   if geo.distance_ligne(a.point, index.ligne(wid)) < RUE_PROCHE_M]
        detail = []
        if not proches:
            detail.append("aucune rue « %s » dans OSM à moins de %d m" % (a.rue, RUE_PROCHE_M))
        elif all(nom != a.rue for nom, _ in proches):
            detail.append("rue écrite « %s » dans OSM" % proches[0][0])
        statut = "à revoir" if detail else None
        if remarque:
            detail.insert(0, remarque)

        e = correspondance(deja, num, point) or correspondance(deja, num, a.point)
        if e is not None:
            t = e.get("tags", {})
            maj = {}
            if corriger_rue and t.get("addr:street") != a.rue:
                maj["addr:street"] = a.rue
            if a.code_postal and not t.get("addr:postcode"):
                maj["addr:postcode"] = a.code_postal
            if maj:
                plan.corriger(e["type"], e["id"], maj, "adresse %s %s : %s" % (
                    num, a.rue, ", ".join("%s=%s" % kv for kv in maj.items())))
                detail.insert(0, "%s %d corrigé (%s)" % (e["type"], e["id"], ", ".join(maj)))
                statut = statut or "corrigé"
            else:
                detail.insert(0, "déjà dans OSM (%s %d)" % (e["type"], e["id"]))
                statut = statut or "existant"
        elif statut and not conf.get("creer_si_rue_absente", False):
            # Nom de rue absent ou différent dans OSM : rien n'est créé
            # tant que la rue n'est pas réglée (renommée ou ajoutée).
            pass
        else:
            numero, logements = numeros(num, a, autres)
            tags = {"addr:housenumber": numero, "addr:street": a.rue}
            if logements:
                tags["addr:unit"] = logements
            if a.code_postal:
                tags["addr:postcode"] = a.code_postal
            # Une position d'une autre source posée sur le contour d'un
            # bâtiment est une porte d'entrée.
            if source != "RQA":
                d = batiments.distance(point, rayon_deg=0.0002)
                if d is not None and d < SUR_CONTOUR_M:
                    tags["entrance"] = entree(a.categorie)
                    detail.append("entrance=%s" % tags["entrance"])
            plan.creer.append((tags, point))
            statut = statut or "nouveau"
        if not a.principale:
            detail.append("pas d'adresse principale au RQA, point d'un logement ou d'un suffixe")
        if autres:
            detail.append("%d logement(s) ou suffixe(s) fusionné(s)" % len(autres))
        if douteux:
            detail.append("logement(s) douteux écarté(s) : %s" % ", ".join(
                sorted({x.logement for x in douteux}, key=_ordre)))
        plan.rapport.append(Ligne(mun, a.rue, num, a.code_postal, point[0], point[1], a.qualite,
                                  statut, "; ".join(detail), source))
    return plan
