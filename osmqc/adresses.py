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
MEME_RUE_M = 300        # ou au même numéro et sur la même rue (une porte loin du point du RQA)
SUFFIXE_DISTINCT_M = 5  # un suffixe plus loin que ça de son numéro de base est une adresse à part
RUE_PROCHE_M = 300      # distance maximale entre l'adresse et une rue du même nom dans OSM
SEULE_OSM_M = 500       # une adresse d'OSM sans pendant au RQA n'est signalée que près du lieu


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
    seules_osm: list = field(default_factory=list)  # (type, id, numéro, rue, ville, point)

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


MAX_VALEUR = 255        # longueur maximale d'une valeur d'étiquette dans OSM
PLAGE_MIN = 3           # une suite d'au moins 3 numéros consécutifs s'écrit en plage


def plages(logements):
    """Les logements en plages : « 101;102;103;105 » devient
    « 101-103;105 ». Seuls les numéros entiers consécutifs (sans zéro en
    tête) sont regroupés; un trou coupe la plage, pour qu'on sache
    exactement quels logements existent."""
    res, suite = [], []

    def vider():
        if len(suite) >= PLAGE_MIN:
            res.append("%s-%s" % (suite[0], suite[-1]))
        else:
            res.extend(suite)
        suite.clear()
    for l in logements:
        if l.isdigit() and not l.startswith("0"):
            if suite and int(l) != int(suite[-1]) + 1:
                vider()
            suite.append(l)
        else:
            vider()
            res.append(l)
    vider()
    return res


def deplier(valeur):
    """Les logements d'une valeur addr:flats, plages dépliées : un
    ensemble, pour comparer deux écritures."""
    res = set()
    for x in (valeur or "").split(";"):
        x = x.strip()
        m = re.fullmatch(r"(\d+)-(\d+)", x)
        if m and int(m.group(1)) < int(m.group(2)) and int(m.group(2)) - int(m.group(1)) < 10000:
            res.update(str(i) for i in range(int(m.group(1)), int(m.group(2)) + 1))
        elif x:
            res.add(x)
    return res


def tranches(valeurs, tete=False):
    """Valeurs addr:flats d'au plus MAX_VALEUR caractères : une liste
    trop longue est répartie sur plusieurs nœuds. tete : la liste commence
    par un élément vide (l'adresse sans logement existe aussi)."""
    res, cur = [], [""] if tete else []
    for v in valeurs:
        if cur and cur != [""] and len(";".join(cur + [v])) > MAX_VALEUR:
            res.append(";".join(cur))
            cur = []
        cur.append(v)
    if cur:
        res.append(";".join(cur))
    return res


def numeros(num, base, autres):
    """Étiquettes de numéro d'une adresse fusionnée : addr:housenumber
    avec les suffixes en lettre (« 120;120A;120B »), et les valeurs
    addr:flats des logements (une par nœud, en général une seule), ou []
    s'il n'y en a pas. La liste des logements commence par un élément vide
    quand l'adresse sans logement existe aussi au RQA (« ;1;2 »), et les
    suites s'écrivent en plages (« 101-109;201-209 »). Le numéro de base
    n'est dans addr:housenumber que s'il existe au RQA, ou s'il n'y a pas
    de suffixe : 120A et 120B sans 120 donnent « 120A;120B »."""
    groupe = [base] + list(autres)
    lettres = sorted({a.numero + a.suffixe for a in groupe if a.suffixe and not a.logement}, key=_ordre)
    logements = sorted({a.logement for a in groupe if a.logement}, key=_ordre)
    lettres = [l for l in lettres if l != num]
    principale = any(a.principale for a in groupe)
    tete = [num] if principale or not lettres else []
    numero = ";".join(tete + lettres)
    return numero, tranches(plages(logements), principale) if logements else []


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
            if not g or not any(g.ecart(p, rayon_deg=0.004) < INTERPOLATION_M
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
    """Adresses déjà dans OSM, par numéro : (objet, point ou contour). Un
    objet qui porte plusieurs numéros (« 47;49 », « 120;120A ») est rangé
    sous chacun."""
    res = defaultdict(list)
    for e in index.tous():
        t = e.get("tags", {})
        if "addr:housenumber" not in t or "addr:interpolation" in t:
            continue
        if e["type"] == "node":
            if e["id"] in ignorer:
                continue
            pts = [(e["lon"], e["lat"])]
        elif e["type"] == "way":
            pts = [index.point(n) for n in e["nodes"] if n in index.noeuds]
            if not pts:
                continue
        else:
            continue
        for num in {x.strip() for x in t["addr:housenumber"].split(";") if x.strip()}:
            res[num].append((e, pts))
    return res


def correspondance(existants, numero, point, rue=None):
    """Objet OSM au même numéro : nœud à moins de DOUBLON_M, ou contour
    fermé (bâtiment, terrain) qui contient le point ou en est proche.
    Sinon, avec rue : le plus proche au même numéro sur la même rue, à
    moins de MEME_RUE_M (une porte placée loin du point du RQA, au fond
    d'un grand terrain)."""
    if rue is not None:
        cle = cle_nom(rue)
        proches = [(min(geo.distance(q, point) for q in pts), e) for e, pts in existants.get(numero, [])
                   if cle_nom(e.get("tags", {}).get("addr:street")) == cle]
        proches = [x for x in proches if x[0] < MEME_RUE_M]
        return min(proches, key=lambda x: x[0])[1] if proches else None
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
        if a.retiree:
            # Une adresse détruite est simplement ignorée; une adresse pas
            # encore certifiée ou sans clé de jumelage est signalée.
            if a.retiree != "terminée" and a.principale:
                plan.rapport.append(Ligne(a.municipalite, a.rue, a.numero, a.code_postal, a.lon,
                                          a.lat, a.qualite, "exclu", a.retiree))
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
    vus = set()             # adresses d'OSM qui correspondent à une adresse du RQA

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

        e = correspondance(deja, num, point) or correspondance(deja, num, a.point) \
            or correspondance(deja, num, a.point, a.rue)
        if e is not None:
            vus.add((e["type"], e["id"]))
            t = e.get("tags", {})
            maj = {}
            if corriger_rue and t.get("addr:street") != a.rue:
                maj["addr:street"] = a.rue
            # Une localité déjà inscrite est gardée.
            if not t.get("addr:city") and a.ville:
                maj["addr:city"] = a.ville
            # Les logements : seulement signalés s'ils diffèrent (une source
            # plus complète, le rôle d'évaluation, a pu servir).
            _, flats = numeros(num, a, autres)
            attendus = set().union(*(deplier(f) for f in flats)) if flats else set()
            dans_osm = deplier(t.get("addr:flats") or t.get("addr:unit"))
            if attendus != dans_osm:
                detail.append("logements : %s" % ", ".join(x for x in (
                    "%d de plus au RQA" % len(attendus - dans_osm) if attendus - dans_osm else "",
                    "%d de plus dans OSM" % len(dans_osm - attendus) if dans_osm - attendus else "") if x))
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
            numero, flats = numeros(num, a, autres)
            tags = {"addr:housenumber": numero, "addr:street": a.rue}
            if a.ville:
                tags["addr:city"] = a.ville
            # Une position d'une autre source posée sur le contour d'un
            # bâtiment est une porte d'entrée.
            if source != "RQA":
                d = batiments.distance(point, rayon_deg=0.0002)
                if d is not None and d < SUR_CONTOUR_M:
                    tags["entrance"] = entree(a.categorie)
                    detail.append("entrance=%s" % tags["entrance"])
            # Une liste de logements trop longue pour une valeur : un nœud
            # par tranche, au même point.
            for f in flats or [None]:
                plan.creer.append((dict(tags, **({"addr:flats": f} if f else {})), point))
            if len(flats) > 1:
                detail.append("logements répartis sur %d nœuds" % len(flats))
            statut = statut or "nouveau"
        if not a.principale and num == a.numero:
            detail.append("pas d'adresse principale au RQA, point d'un logement ou d'un suffixe")
        if autres:
            detail.append("%d logement(s) ou suffixe(s) fusionné(s)" % len(autres))
        if douteux:
            detail.append("logement(s) douteux écarté(s) : %s" % ", ".join(
                sorted({x.logement for x in douteux}, key=_ordre)))
        plan.rapport.append(Ligne(mun, a.rue, num, a.code_postal, point[0], point[1], a.qualite,
                                  statut, "; ".join(detail), source))
    # Adresses d'OSM qu'aucune adresse du RQA n'a retrouvées, près des
    # adresses du lieu (ajoutées à la main, venues d'une autre source, ou
    # écrites autrement).
    # Les extrémités d'une ligne d'interpolation n'en sont pas.
    grille = geo.Grille([[a.point, a.point] for a in gardees], pas=0.01)
    interp = {n for w in index.chemins.values() if "addr:interpolation" in w.get("tags", {}) for n in w["nodes"]}
    for num, lst in deja.items():
        for e, pts in lst:
            if (e["type"], e["id"]) in vus or e.get("tags", {}).get("addr:street") is None \
                    or (e["type"] == "node" and e["id"] in interp):
                continue
            if grille.ecart(pts[0], rayon_deg=0.01) > SEULE_OSM_M:
                continue
            vus.add((e["type"], e["id"]))
            t = e["tags"]
            plan.seules_osm.append((e["type"], e["id"], t["addr:housenumber"], t["addr:street"],
                                    t.get("addr:city", ""), pts[0]))
    plan.seules_osm.sort(key=lambda x: (x[3], _ordre(x[2])))
    return plan
