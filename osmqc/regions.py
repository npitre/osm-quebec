# Limites municipales : comparaison d'OSM avec les Découpages
# administratifs du MRNF (SDA, 1/20 000), qui font autorité, et
# préparation de leur remplacement dans OSM.
#
# Source : SDA.gpkg, couche munic_s. Licence CC BY 4.0, couverte par la
# permission du MRNF pour OSM.
#
# Règles du remplacement (rencontre du 16 octobre 2026) :
# - le tracé est celui du MRNF;
# - les limites ont leurs propres chemins et nœuds : jamais le littoral,
#   une route ou un cours d'eau, même quand le tracé les suit;
# - une limite commune à deux municipalités est un seul chemin, membre
#   des deux relations;
# - les chemins qui ne servent plus à aucune limite sont supprimés; le
#   littoral et les autres objets sont seulement retirés des relations.

import json
import sqlite3
from collections import Counter, defaultdict

from . import extrait, geo, osm

URL_SDA = ("https://diffusion.mern.gouv.qc.ca/diffusion/RGQ/Vectoriel/Theme/Local/"
           "SDA_20k/GPKG/SDA.gpkg.zip")
MAX_NOEUDS = 1900       # sous la limite de 2000 nœuds par chemin


def municipalites_mrc(chemin, mrc):
    """Codes et noms des municipalités d'une MRC selon le MRNF :
    {code: nom}."""
    db = sqlite3.connect("file:%s?mode=ro" % chemin, uri=True)
    return dict(db.execute("select MUS_CO_GEO, MUS_NM_MUN from munic_s where MUS_CO_MRC = ? "
                           "order by MUS_CO_GEO", (mrc,)))


def nom_mrc(chemin, mrc):
    db = sqlite3.connect("file:%s?mode=ro" % chemin, uri=True)
    r = db.execute("select MRS_NM_MRC from mrc_s where MRS_CO_MRC = ?", (mrc,)).fetchone()
    return r[0] if r else ""


def trouver_relation(code, nom, contexte):
    """Relation de limite d'OSM d'une municipalité, cherchée par
    Nominatim et confirmée par son étiquette ref:qc. None si absente."""
    import time
    import urllib.parse
    # Avec le nom de la MRC d'abord; sans, ensuite, au cas où OSM
    # rattache la municipalité à une autre MRC.
    for q in ("%s, %s, Québec" % (nom, contexte), "%s, Québec" % nom):
        params = urllib.parse.urlencode({"q": q, "format": "jsonv2", "extratags": 1,
                                         "limit": 10, "countrycodes": "ca"})
        time.sleep(1.1)     # règles d'usage de Nominatim : une requête par seconde
        rep = json.loads(osm.lire("https://nominatim.openstreetmap.org/search?" + params))
        for r in rep:
            if r.get("osm_type") == "relation" and (r.get("extratags") or {}).get("ref:qc") == code:
                return int(r["osm_id"])
    return None


def sda(chemin, codes):
    """Polygones officiels : {code: (nom, version, [polygones])}."""
    db = sqlite3.connect("file:%s?mode=ro" % chemin, uri=True)
    colonnes = [r[1] for r in db.execute("pragma table_info(munic_s)")]
    version = "MUS_CO_VER" if "MUS_CO_VER" in colonnes else "''"
    res = {}
    for code, nom, ver, g in db.execute(
            "select MUS_CO_GEO, MUS_NM_MUN, %s, geom from munic_s where MUS_CO_GEO in (%s)"
            % (version, ",".join("?" * len(codes))), list(codes)):
        res[code] = (nom, ver, geo.wkb_gpkg(g))
    return res


def genre_chemin(t):
    """Ce dont est fait un chemin de limite : littoral, route, etc."""
    for k in ("natural", "highway", "waterway", "railway"):
        if k in t:
            return k + "=" + t[k]
    if not t or set(t) <= {"boundary", "admin_level", "source", "name"}:
        return "limite seule"
    return "autre"


A_REPORTER = ("note", "fixme", "description")


def protege(t):
    """Étiquettes qui interdisent la suppression automatique d'un chemin
    de limite : une note, un fixme, une description, ou une limite
    contestée (disputed*, par exemple la frontière avec
    Terre-Neuve-et-Labrador). Renvoie ces étiquettes, ou {}."""
    return {k: v for k, v in t.items() if k in A_REPORTER or k.startswith("disputed")}


def frontiere(t):
    """Frontière provinciale ou internationale : réutilisable, jamais
    modifiée ni supprimée."""
    return t.get("admin_level") in ("2", "4")


def lien_lieu(rel, index):
    """Lien entre une relation municipale et son nœud de lieu, dont
    OsmAnd a besoin : un membre label ou admin_centre qui est un nœud
    place portant exactement le même name. Renvoie (statut, détail)."""
    nom = rel.get("tags", {}).get("name", "")
    membres = [m for m in rel["members"] if m["type"] == "node" and m["role"] in ("label", "admin_centre")]
    if not membres:
        return "sans lien", "aucun membre label ni admin_centre"
    for m in membres:
        n = index.noeuds.get(m["ref"])
        if n is None:
            continue
        t = n.get("tags", {})
        if "place" in t and t.get("name") == nom:
            return "lié", "%s : node %d place=%s" % (m["role"], m["ref"], t["place"])
    n = index.noeuds.get(membres[0]["ref"], {})
    t = n.get("tags", {})
    if "place" not in t:
        return "lien sans place", "%s : node %d sans étiquette place" % (membres[0]["role"], membres[0]["ref"])
    return "noms différents", "%s : node %d « %s » contre « %s »" % (
        membres[0]["role"], membres[0]["ref"], t.get("name", ""), nom)


def reporter_notes(proteges, index, plan):
    """Reporte note, fixme et description des chemins protégés retirés sur
    le chemin neuf le plus proche. Renvoie [(chemin protégé, chemin neuf,
    étiquettes)] et met à jour plan["etiquettes"]."""
    points = points_du_plan(plan)
    neufs = [(wid, [points[n] for n in ids]) for wid, ids, _ in plan["chemins"]]
    plan.setdefault("etiquettes", {})
    res = []
    for w in proteges:
        tags = {k: v for k, v in index.chemins[w].get("tags", {}).items() if k in A_REPORTER}
        if not tags or not neufs:
            res.append((w, None, tags))
            continue
        ligne = index.ligne(w)
        echantillon = ligne[::max(1, len(ligne) // 10)]
        wid = min(neufs, key=lambda nl: sum(geo.distance_ligne(p, nl[1]) for p in echantillon))[0]
        plan["etiquettes"].setdefault(wid, {}).update(tags)
        res.append((w, wid, tags))
    return res


class Relation:
    """Relation de limite d'OSM, avec tous ses membres."""

    def __init__(self, ident, pbf=None, elements=None):
        """elements : objets déjà lus (plusieurs relations à la fois);
        sinon lus dans l'extrait local pbf, ou demandés à l'API."""
        self.id = ident
        if elements is None:
            elements = extrait.relations(pbf, [ident]) if pbf else osm.complet("relation", ident)
        self.index = elements if isinstance(elements, osm.Index) else osm.Index(elements)
        self.rel = self.index.relations[ident]
        self.tags = self.rel.get("tags", {})
        self.chemins = [m["ref"] for m in self.rel["members"] if m["type"] == "way"]
        anneaux, self.ouverts = geo.assembler([self.index.chemins[w]["nodes"] for w in self.chemins])
        self.anneaux = [[self.index.point(n) for n in a] for a in anneaux]
        self.composition = Counter(genre_chemin(self.index.chemins[w].get("tags", {}))
                                   for w in self.chemins)


def comparer(adresses, officiel, osm_rel):
    """Municipalité de chaque adresse selon le RQA, la limite du MRNF et
    celle d'OSM. officiel : {code: polygones}; osm_rel : {code: anneaux}.
    Renvoie (compteur, écarts)."""
    compte = Counter()
    ecarts = []
    off = [(c, p, geo.boite([pt for a in p for pt in a])) for c, polys in officiel.items() for p in polys]
    rel = [(c, anneaux, geo.boite([pt for a in anneaux for pt in a])) for c, anneaux in osm_rel.items()]
    for a in adresses:
        if a.fin or not a.principale:
            continue
        m = next((c for c, p, b in off if geo.dans_boite(a.point, b) and geo.dedans(a.point, p)), None)
        o = next((c for c, an, b in rel if geo.dans_boite(a.point, b) and geo.dedans(a.point, an)), None)
        compte[("MRNF", m == a.municipalite)] += 1
        compte[("OSM", o == a.municipalite)] += 1
        if m != a.municipalite or o != a.municipalite:
            ecarts.append((a, m, o))
    return compte, ecarts


def arcs(officiel):
    """Découpe les anneaux officiels en arcs : portions de tracé bordant
    le même ensemble de municipalités (deux voisines, ou une seule si
    l'autre côté est hors du lieu traité). Un arc commun n'est produit
    qu'une fois. officiel : {code: polygones}.
    Renvoie [(points, {code: rôle})], rôle « outer » ou « inner »."""
    cotes = defaultdict(set)    # segment (non orienté) -> municipalités
    for code, polys in officiel.items():
        for poly in polys:
            for anneau in poly:
                for a, b in zip(anneau, anneau[1:]):
                    cotes[frozenset((a, b))].add(code)
    vus = {}
    res = []
    for code, polys in officiel.items():
        for poly in polys:
            for i, anneau in enumerate(poly):
                role = "outer" if i == 0 else "inner"
                segs = list(zip(anneau, anneau[1:]))
                proprio = [frozenset(cotes[frozenset(s)]) for s in segs]
                n = len(segs)
                # Commencer à un changement de voisinage, s'il y en a un.
                debut = next((k for k in range(n) if proprio[k] != proprio[k - 1]), 0)
                ordre = list(range(debut, n)) + list(range(0, debut))
                courant = [segs[ordre[0]][0]]
                for j, k in enumerate(ordre):
                    courant.append(segs[k][1])
                    fin = j == n - 1 or proprio[ordre[j + 1]] != proprio[k]
                    if fin:
                        _ajouter_arc(courant, code, role, vus, res)
                        courant = [segs[k][1]]
    return res


def _ajouter_arc(pts, code, role, vus, res):
    cle = frozenset(frozenset(s) for s in zip(pts, pts[1:]))
    if cle in vus:
        res[vus[cle]][1][code] = role
        return
    vus[cle] = len(res)
    res.append((list(pts), {code: role}))


PRECISION = 7           # OSM garde 7 décimales de degré (environ 1 cm)


def arrondi(p):
    return (round(p[0], PRECISION), round(p[1], PRECISION))


def candidats_conformes(relations, index):
    """Chemins de limite existants qui pourraient déjà suivre le tracé du
    MRNF : les simples lignes de limite des relations du lieu (jamais un
    littoral, une route ou un cours d'eau). {chemin: [points arrondis]}."""
    res = {}
    for rel in relations.values():
        for w in rel.chemins:
            e = index.chemins.get(w)
            if e is None or w in res:
                continue
            t = e.get("tags", {})
            if t.get("boundary") != "administrative" or genre_chemin(t) not in ("limite seule", "autre"):
                continue
            if any(n not in index.noeuds for n in e["nodes"]):
                continue
            res[w] = [arrondi(index.point(n)) for n in e["nodes"]]
    return res


def reconnaitre(pts, candidats, pris):
    """Chemins existants qui suivent exactement une portion de l'arc (mêmes
    sommets, dans un sens ou dans l'autre). Renvoie [(début, fin, chemin)]
    triés et sans chevauchement, en indices de sommets de l'arc."""
    R = [arrondi(p) for p in pts]
    ou = defaultdict(list)
    for i, p in enumerate(R):
        ou[p].append(i)
    trouves = []
    for w, S in candidats.items():
        if w in pris or len(S) < 2:
            continue
        for i in ou.get(S[0], []):
            if R[i:i + len(S)] == S:
                trouves.append((i, i + len(S) - 1, w))
                break
            if i - len(S) + 1 >= 0 and R[i - len(S) + 1:i + 1] == S[::-1]:
                trouves.append((i - len(S) + 1, i, w))
                break
    res, fin = [], 0
    for i, j, w in sorted(trouves):
        if i >= fin:
            res.append((i, j, w))
            fin = j
    return res


def preparer(officiel, relations, exterieur=None, index=None):
    """Plan de remplacement des limites.
    officiel : {code: polygones du MRNF}; relations : {code: Relation};
    exterieur : Relation parente (MRC) dont on réutilise les chemins pour
    un contour extérieur fermé (le large, autour d'îles), au lieu de le
    tracer d'après le MRNF (None : tout d'après le MRNF).
    index : objets OSM des relations; un chemin de limite existant qui
    suit déjà exactement le tracé du MRNF est réutilisé tel quel, avec ses
    nœuds (envoi précédent, ou voisine déjà traitée).
    Renvoie un dict : nouveaux nœuds et chemins, chemins existants
    réutilisés et leurs nœuds, membres des relations, chemins retirés,
    rapport."""
    noeuds = {}           # point arrondi -> id négatif
    existants = {}        # id de nœud existant -> point
    par_point = {}        # point arrondi -> id de nœud existant
    reutilises = []       # (id, [ids de nœuds], {code: rôle})
    chemins = []          # (id négatif, [ids de nœuds], {code: rôle})
    membres = defaultdict(list)   # code -> [(type, id, rôle)]
    rapport = []

    def noeud(p):
        p = arrondi(p)
        if p in par_point:
            return par_point[p]
        if p not in noeuds:
            noeuds[p] = -(len(noeuds) + 1)
        return noeuds[p]

    tous = arcs(officiel)
    # Un arc extérieur qui fait à lui seul un anneau fermé (une île, par
    # exemple) peut reprendre les chemins de la relation parente. Un arc
    # ouvert, lui, doit se raccorder à ses voisins par les mêmes nœuds :
    # il est toujours tracé d'après le MRNF.
    reprendre = {}
    fermes = [k for k, (pts, roles) in enumerate(tous) if len(roles) == 1 and pts[0] == pts[-1]]
    if exterieur is not None and fermes:
        for w in exterieur.chemins:
            ligne = exterieur.index.ligne(w)
            milieu = ligne[len(ligne) // 2]
            k = min(fermes, key=lambda k: geo.distance_ligne(milieu, tous[k][0]))
            reprendre.setdefault(k, []).append(w)
    # Chemins existants déjà conformes au MRNF : d'abord les reconnaître
    # tous, pour que les chemins neufs se raccordent à leurs nœuds.
    candidats = candidats_conformes(relations, index) if index is not None else {}
    pris = set()
    conformes = {}
    for k, (pts, roles) in enumerate(tous):
        if k in reprendre or not candidats:
            continue
        if pts[0] == pts[-1]:
            # Anneau fermé : le faire commencer au bout d'un chemin existant.
            R = [arrondi(p) for p in pts]
            debut = next((R.index(S[0]) for w, S in candidats.items() if w not in pris and S[0] in R), 0)
            pts = pts[debut:-1] + pts[:debut + 1]
            tous[k] = (pts, roles)
        conformes[k] = reconnaitre(pts, candidats, pris)
        for _, _, w in conformes[k]:
            pris.add(w)
            for n in index.chemins[w]["nodes"]:
                existants[n] = index.point(n)
                par_point[arrondi(existants[n])] = n
    for k, (pts, roles) in enumerate(tous):
        if k in reprendre:
            (code, role), = roles.items()
            for w in reprendre[k]:
                membres[code].append(("way", w, role))
            rapport.append("anneau extérieur de %d sommets (%s) : %d chemins de la relation %d réutilisés"
                           % (len(pts), code, len(reprendre[k]), exterieur.id))
            continue
        ids = [noeud(p) for p in pts]
        # Portions : chemins existants conformes, et trous à tracer.
        portions, i = [], 0
        for a, b, w in conformes.get(k, []):
            if a > i:
                portions.append((i, a, None))
            portions.append((a, b, w))
            i = b
        if i < len(ids) - 1:
            portions.append((i, len(ids) - 1, None))
        nb = nb_existants = 0
        for a, b, w in portions:
            if w is not None:
                reutilises.append((w, index.chemins[w]["nodes"], dict(roles)))
                nb_existants += 1
                for code, role in roles.items():
                    membres[code].append(("way", w, role))
                continue
            for i in range(a, b, MAX_NOEUDS - 1):
                morceau = ids[i:min(i + MAX_NOEUDS, b + 1)]
                wid = -(len(chemins) + 1)
                chemins.append((wid, morceau, dict(roles)))
                nb += 1
                for code, role in roles.items():
                    membres[code].append(("way", wid, role))
        rapport.append("arc de %d sommets (%s) : %s" % (
            len(pts), ", ".join("%s %s" % kv for kv in sorted(roles.items())),
            ", ".join(x for x in ("%d chemin(s) neuf(s)" % nb if nb else "",
                                  "%d chemin(s) existant(s) déjà conforme(s)" % nb_existants
                                  if nb_existants else "") if x)))

    # Membres des relations : les chemins sont remplacés, les autres
    # membres (label, admin_centre) sont gardés.
    nouvelles = {}
    anciens = set()
    for code, rel in relations.items():
        autres = [m for m in rel.rel["members"] if m["type"] != "way"]
        anciens.update(rel.chemins)
        nouvelles[code] = autres + [{"type": t, "ref": i, "role": r} for t, i, r in membres[code]]
    gardes = {i for lst in membres.values() for t, i, r in lst if i > 0}
    retires = sorted(anciens - gardes)
    modifiees = sorted(c for c, rel in relations.items()
                       if cles_membres(rel.rel["members"]) != cles_membres(nouvelles[c]))
    return {"noeuds": noeuds, "existants": existants, "chemins": chemins, "reutilises": reutilises,
            "membres": nouvelles, "modifiees": modifiees, "retires": retires, "rapport": rapport}


def cles_membres(membres):
    """Membres d'une relation, sans tenir compte de leur ordre."""
    return sorted((m["type"], m["ref"], m["role"]) for m in membres)


def points_du_plan(plan):
    """Position de chaque nœud des chemins du plan : neufs et existants."""
    points = {nid: p for p, nid in plan["noeuds"].items()}
    points.update(plan.get("existants", {}))
    return points


def relations_du_chemin(wid):
    """Relations dont un chemin est membre (version actuelle d'OSM)."""
    url = "%s/way/%d/relations.json" % (osm.API, wid)
    return [r["id"] for r in json.loads(osm.lire(url))["elements"]]


def supprimables(retires, index, relations_traitees, pbf=None):
    """Parmi les chemins retirés, ceux qu'on supprime : une simple ligne
    de limite, membre d'aucune autre relation que celles qu'on traite,
    avec ses nœuds qui ne servent à rien d'autre. Le littoral, les routes
    et le reste sont seulement retirés. L'usage dans tout OSM est lu dans
    l'extrait local (pbf), sinon demandé à l'API.
    Un chemin protégé (note, fixme, description, disputed*) ou une
    frontière provinciale ou internationale n'est jamais supprimé.
    Renvoie (chemins, nœuds) à supprimer."""
    candidats = [w for w in retires
                 if genre_chemin(index.chemins[w].get("tags", {})) == "limite seule"
                 and not protege(index.chemins[w].get("tags", {}))
                 and not frontiere(index.chemins[w].get("tags", {}))]
    noeuds = sorted({n for w in candidats for n in index.chemins[w]["nodes"]
                     if not index.noeuds[n].get("tags")})
    traitees = set(relations_traitees)
    if pbf:
        par_noeud, membres, par_chemin = extrait.usages(pbf, noeuds, candidats)
    else:
        par_chemin = {w: set(relations_du_chemin(w)) for w in candidats}
        par_noeud, membres = _usages_api(noeuds)
    chemins = [w for w in candidats if not (par_chemin.get(w, set()) - traitees)]
    supprimes = set(chemins)
    garder = {n for n in noeuds if (par_noeud.get(n, set()) - supprimes) or n in membres}
    return chemins, [n for n in noeuds if n not in garder
                     and any(n in index.chemins[w]["nodes"] for w in chemins)]


def _usages_api(nids):
    """Repli sans extrait : un appel à l'API par nœud."""
    par_noeud, membres = {}, set()
    for n in nids:
        par_noeud[n] = {c["id"] for c in json.loads(osm.lire("%s/node/%d/ways.json" % (osm.API, n)))["elements"]}
        if json.loads(osm.lire("%s/node/%d/relations.json" % (osm.API, n)))["elements"]:
            membres.add(n)
    return par_noeud, membres


def geojson(officiel, osm_rel, ecarts, noms, coupures=None):
    """Les deux tracés et les adresses en écart, pour la révision."""
    f = []
    for code, polys in officiel.items():
        f.append({"type": "Feature",
                  "geometry": {"type": "MultiPolygon",
                               "coordinates": [[[list(p) for p in a] for a in poly] for poly in polys]},
                  "properties": {"source": "MRNF", "code": code, "nom": noms.get(code, ""),
                                 "stroke": "#1f77b4", "fill-opacity": 0.05}})
    for code, anneaux in osm_rel.items():
        f.append({"type": "Feature",
                  "geometry": {"type": "MultiLineString",
                               "coordinates": [[list(p) for p in a] for a in anneaux]},
                  "properties": {"source": "OSM", "code": code, "nom": noms.get(code, ""),
                                 "stroke": "#d62728"}})
    for a, m, o in ecarts:
        f.append({"type": "Feature",
                  "geometry": {"type": "Point", "coordinates": [a.lon, a.lat]},
                  "properties": {"adresse": "%s %s" % (a.numero, a.rue),
                                 "municipalite_rqa": a.municipalite,
                                 "selon_mrnf": m or "aucune", "selon_osm": o or "aucune"}})
    couleurs = {"déjà coupée": "#2ca02c", "coupure à déplacer": "#ff7f0e",
                "coupure à ajouter": "#d62728", "coupure devenue inutile": "#9467bd"}
    for action, nom, wid, p, d, _ in coupures or []:
        f.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": list(p)},
                  "properties": {"coupure": action, "rue": nom, "objet": "way/%d" % wid,
                                 "distance_m": round(d) if d is not None else None,
                                 "marker-color": couleurs[action], "marker-size": "small"}})
    return {"type": "FeatureCollection", "features": f}


def anneaux_proposes(plan, exterieur):
    """Anneaux des relations après le remplacement, pour vérifier que
    chaque adresse tombe dans la bonne municipalité. {code: anneaux}."""
    points = points_du_plan(plan)
    chemins = {wid: ids for wid, ids, _ in plan["chemins"] + plan.get("reutilises", [])}
    if exterieur is not None:
        for w in exterieur.chemins:
            chemins[w] = exterieur.index.chemins[w]["nodes"]
        points.update({n: exterieur.index.point(n) for n in exterieur.index.noeuds})
    res = {}
    for code, membres in plan["membres"].items():
        segs = [chemins[m["ref"]] for m in membres if m["type"] == "way"]
        anneaux, _ = geo.assembler(segs)
        res[code] = [[points[n] for n in a] for a in anneaux]
    return res


COUPURE_M = 25          # une route coupée à moins de 25 m d'une limite y est coupée


def lignes_limites(plan, exterieur=None):
    """Polylignes des limites proposées (chemins neufs et réutilisés)."""
    points = points_du_plan(plan)
    lignes = [[points[n] for n in ids] for _, ids, _ in plan["chemins"] + plan.get("reutilises", [])]
    if exterieur is not None:
        reutilises = {m["ref"] for lst in plan["membres"].values() for m in lst
                      if m["type"] == "way" and m["ref"] > 0}
        lignes += [exterieur.index.ligne(w) for w in exterieur.chemins if w in reutilises]
    return lignes


def coupures(index, nouvelles, anciennes):
    """Routes nommées qui traversent les limites, et leurs coupures.
    index : objets OSM (routes); nouvelles, anciennes : polylignes des
    limites proposées et actuelles. Renvoie des lignes de rapport :
    (action, nom, chemin, point, distance, chemin qui croise la limite)."""
    grille_n = geo.Grille([l for l in nouvelles if len(l) > 1])
    grille_a = geo.Grille([l for l in anciennes if len(l) > 1])
    routes = [w for w in index.chemins.values()
              if "highway" in w.get("tags", {}) and "name" in w.get("tags", {})
              and w["tags"]["highway"] not in ("footway", "path", "cycleway", "steps", "track")
              and all(n in index.noeuds for n in w["nodes"])]
    # Une coupure est un nœud où se rejoignent deux chemins du même nom
    # (un cul-de-sac ou un quai au bord de l'eau n'en est pas une).
    par_bout = defaultdict(list)    # (nom, nœud) -> chemins
    for w in routes:
        for n in (w["nodes"][0], w["nodes"][-1]):
            par_bout[(w["tags"]["name"], n)].append(w["id"])
    bouts = defaultdict(list)       # nom -> [(point, chemin)]
    identiques = set()              # coupures entre chemins aux étiquettes identiques
    for (nom, n), ws in par_bout.items():
        if len(ws) >= 2:
            bouts[nom].append((index.point(n), ws[0]))
            if all(index.chemins[w].get("tags") == index.chemins[ws[0]].get("tags") for w in ws):
                identiques.add((nom, ws[0], index.point(n)))
    res = []
    vus = set()
    # Croisements avec les limites proposées : il faut une coupure tout près.
    for w in routes:
        nom = w["tags"]["name"]
        for p in grille_n.croisements(index.ligne(w["id"])):
            cle = (nom, round(p[0], 4), round(p[1], 4))
            if cle in vus:
                continue
            vus.add(cle)
            proches = sorted((geo.distance(p, b), wid) for b, wid in bouts[nom] if geo.distance(p, b) < 500)
            if proches and proches[0][0] < COUPURE_M:
                res.append(("déjà coupée", nom, proches[0][1], p, proches[0][0], w["id"]))
            elif proches:
                res.append(("coupure à déplacer", nom, proches[0][1], p, proches[0][0], w["id"]))
            else:
                res.append(("coupure à ajouter", nom, w["id"], p, None, w["id"]))
    # Coupures au droit d'une limite actuelle qui ne correspondent plus à
    # aucune limite proposée. Seulement si les deux chemins ont les mêmes
    # étiquettes : sinon la coupure sert à autre chose (pont, revêtement).
    for nom, wid, b in sorted(identiques):
        da = grille_a.distance(b)
        dn = grille_n.distance(b, rayon_deg=0.004)
        if da is not None and da < COUPURE_M and (dn is None or dn > 200):
            res.append(("coupure devenue inutile", nom, wid, b, da, None))
    return res


def decouper(index, coupures_, relations_routes, prochain_noeud, prochain_chemin):
    """Coupe les routes là où elles traversent une limite proposée (cas
    « coupure à ajouter » et « coupure à déplacer ») : un nœud est ajouté
    sur la route au point de croisement, sans changer sa géométrie, et le
    chemin est coupé à ce nœud. Le nœud n'appartient pas au chemin de
    limite. Le morceau neuf garde les étiquettes de la route et rejoint,
    juste après elle, chaque relation dont elle est membre (lignes
    d'autobus, routes numérotées).
    index : routes (versions actuelles); relations_routes : {id: relation};
    prochain_noeud, prochain_chemin : premiers identifiants négatifs libres.
    Renvoie {"noeuds": {id: (lon, lat)}, "chemins": {id: (nœuds, étiquettes)},
    "modifies": {id: nœuds}, "relations": {id: membres}, "rapport": [...]}."""
    a_couper = defaultdict(list)
    for action, nom, _, p, _, wid in coupures_:
        if action in ("coupure à ajouter", "coupure à déplacer") and wid in index.chemins:
            a_couper[wid].append(p)
    res = {"noeuds": {}, "chemins": {}, "modifies": {}, "relations": {}, "rapport": []}
    nid, wnid = prochain_noeud, prochain_chemin
    for wid, points in sorted(a_couper.items()):
        w = index.chemins[wid]
        noeuds = list(w["nodes"])
        coupes = []         # positions (indices) des nœuds de coupure
        for p in points:
            pts = [index.point(n) for n in noeuds]
            i = min(range(len(pts) - 1), key=lambda k: geo.distance_segment(p, pts[k], pts[k + 1]))
            # Un nœud existant tout près du croisement sert de coupure.
            proche = min((i, i + 1), key=lambda k: geo.distance(p, pts[k]))
            if geo.distance(p, pts[proche]) < 1:
                k = proche
            else:
                res["noeuds"][nid] = p
                noeuds.insert(i + 1, nid)
                index.noeuds[nid] = {"type": "node", "id": nid, "lon": p[0], "lat": p[1], "tags": {}}
                nid -= 1
                k = i + 1
                coupes = [c + 1 if c >= k else c for c in coupes]
            if 0 < k < len(noeuds) - 1:
                coupes.append(k)
        coupes = sorted(set(coupes))
        if not coupes:
            continue
        bornes = [0] + coupes + [len(noeuds) - 1]
        morceaux = [noeuds[a:b + 1] for a, b in zip(bornes, bornes[1:])]
        res["modifies"][wid] = morceaux[0]
        neufs = []
        for m in morceaux[1:]:
            res["chemins"][wnid] = (m, dict(w.get("tags", {})))
            neufs.append(wnid)
            wnid -= 1
        for rid, rel in relations_routes.items():
            membres = res["relations"].get(rid, rel["members"])
            nouveaux = []
            for m in membres:
                nouveaux.append(m)
                if m["type"] == "way" and m["ref"] == wid:
                    nouveaux += [{"type": "way", "ref": n, "role": m["role"]} for n in neufs]
            if nouveaux != membres:
                res["relations"][rid] = nouveaux
        res["rapport"].append("way %d (%s) coupé en %d morceaux" % (
            wid, w.get("tags", {}).get("name", ""), len(morceaux)))
    return res
