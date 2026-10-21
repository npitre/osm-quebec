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


def ligne_de_limite(t):
    """Chemin qui n'est qu'une limite : sans étiquette (la relation lui
    donne son sens) ou étiqueté boundary=administrative, mais jamais un
    littoral, une route, un cours d'eau ou une voie ferrée."""
    g = genre_chemin(t)
    return g == "limite seule" or (g == "autre" and t.get("boundary") == "administrative")


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
    neufs = [(wid, [points[n] for n in ids]) for wid, ids, _ in plan["chemins"]
             if wid not in plan.get("provisoires", ())]
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
            if not ligne_de_limite(e.get("tags", {})):
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


def preparer(officiel, relations, exterieur=None, index=None, voisines=None, rels_voisines=None,
             usages=None, chemins_des_noeuds=None):
    """Plan de remplacement des limites.
    officiel : {code: polygones du MRNF}; relations : {code: Relation};
    exterieur : Relation parente (MRC) dont on réutilise les chemins pour
    un contour extérieur fermé (le large, autour d'îles), au lieu de le
    tracer d'après le MRNF (None : tout d'après le MRNF).
    index : objets OSM des relations; un chemin de limite existant qui
    suit déjà exactement le tracé du MRNF est réutilisé tel quel, avec ses
    nœuds (envoi précédent, ou voisine déjà traitée).
    voisines : {code: polygones du MRNF} des municipalités hors du lot qui
    le touchent; rels_voisines : {code: Relation} de celles qui ont une
    relation dans OSM. L'arc commun avec une voisine devient membre de sa
    relation, modifiée en partie (voir osmqc/voisines.py). usages :
    fonction {chemin: {relations}} pour les chemins donnés (tout OSM);
    chemins_des_noeuds : fonction {nœud: {chemins}} (tout OSM). Un nœud
    existant pile au bout d'un arc du MRNF (un point triple déjà juste)
    est réutilisé s'il ne sert qu'à des chemins de limite.
    Renvoie un dict : nouveaux nœuds et chemins, chemins existants
    réutilisés et leurs nœuds, membres des relations, chemins retirés,
    modifications des voisines, rapport."""
    noeuds = {}           # point arrondi -> id négatif
    existants = {}        # id de nœud existant -> point
    par_point = {}        # point arrondi -> id de nœud existant
    reutilises = []       # (id, [ids de nœuds], {code: rôle})
    chemins = []          # (id négatif, [ids de nœuds], {code: rôle})
    membres = defaultdict(list)   # code -> [(type, id, rôle)]
    rapport = []
    voisines = voisines or {}
    rels_voisines = rels_voisines or {}
    compteur = [0]

    def nouveau_chemin():
        compteur[0] -= 1
        return compteur[0]

    def noeud(p):
        p = arrondi(p)
        if p in par_point:
            return par_point[p]
        if p not in noeuds:
            noeuds[p] = -(len(noeuds) + 1)
        return noeuds[p]

    # Deux sommets du MRNF à moins de 1e-7 degré l'un de l'autre seraient
    # le même point dans OSM : un seul nœud.
    # Les arcs sont calculés avec les voisines, pour savoir qui borde
    # chaque arc; on ne garde que ceux qui touchent le lot. Une voisine
    # sans relation dans OSM (un TNO aquatique, souvent) est ignorée : elle
    # ne découpe pas les arcs.
    voisines = {c: p for c, p in voisines.items() if c in rels_voisines}
    tous, reste = [], defaultdict(list)
    for pts, roles in arcs(dict(officiel, **voisines)):
        pts = [p for i, p in enumerate(pts) if i == 0 or arrondi(p) != arrondi(pts[i - 1])]
        if not set(roles) & set(officiel):
            for c in roles:
                reste[c].append(pts)
            continue
        tous.append((pts, {c: r for c, r in roles.items() if c in officiel or c in rels_voisines}))
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
    # Nœuds existants pile aux bouts des arcs (points triples déjà justes) :
    # réutilisés s'ils ne servent qu'à des lignes de limite, pour que la
    # voisine se raccorde sans chemin de longueur nulle.
    if index is not None and chemins_des_noeuds is not None:
        bouts = {arrondi(pts[k]) for pts, _ in tous for k in (0, -1)}
        ici = {}
        for rel in list(relations.values()) + list(rels_voisines.values()):
            for w in rel.chemins:
                for n in index.chemins.get(w, {}).get("nodes", []):
                    if n in index.noeuds and arrondi(index.point(n)) in bouts:
                        ici[n] = arrondi(index.point(n))
        if ici:
            usage = chemins_des_noeuds(sorted(ici))
            for n, p in ici.items():
                ws = usage.get(n, set())
                if not index.noeuds[n].get("tags") and ws and all(
                        w in index.chemins and ligne_de_limite(index.chemins[w].get("tags", {})) for w in ws):
                    par_point.setdefault(p, n)
                    existants[n] = index.point(n)
    # Chemins existants déjà conformes au MRNF : d'abord les reconnaître
    # tous, pour que les chemins neufs se raccordent à leurs nœuds.
    candidats = candidats_conformes(dict(relations, **rels_voisines), index) if index is not None else {}
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
                wid = nouveau_chemin()
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

    # Voisines : modification partielle de leur relation.
    positions = {nid: p for p, nid in noeuds.items()}
    positions.update(existants)

    def point(n):
        return positions[n] if n in positions else index.point(n)

    def noeud_neuf(p):
        n = noeud(p)
        positions.setdefault(n, arrondi(p))
        return n
    from . import voisines as vois
    modif_voisines = {"modifies": {}, "neufs": {}, "relations": {}, "liberes": set()}
    provisoires = set()
    lot = [r.id for r in relations.values()]
    # Usage de tous les chemins des voisines, en une seule lecture.
    tous_usages = (usages or (lambda ws: {}))(sorted({w for r in rels_voisines.values() for w in r.chemins}))
    for code, rel in sorted(rels_voisines.items()):
        if not membres[code]:
            continue
        lignes = {w: ids for w, ids, _ in chemins + reutilises}
        communs = [(i, lignes[i], r) for t, i, r in membres[code]]
        res, raison = vois.modifier(rel, index, communs, reste.get(code, []), point, noeud_neuf,
                                    nouveau_chemin, lambda ws: {w: tous_usages.get(w, set()) for w in ws}, lot)
        if res is None:
            rapport.append("voisine %s non modifiée : %s" % (rel.tags.get("name", code), raison))
            for _, _, roles in chemins + reutilises:
                roles.pop(code, None)
            continue
        deja = set(res["modifies"]) & set(modif_voisines["modifies"])
        if deja:
            rapport.append("voisine %s non modifiée : chemin %s déjà coupé pour une autre voisine"
                           % (rel.tags.get("name", code), ", ".join(map(str, sorted(deja)))))
            for _, _, roles in chemins + reutilises:
                roles.pop(code, None)
            continue
        nouvelles[code] = res["membres"]
        anciens.update(rel.chemins)
        for w, ids, role in res["chemins"]:
            chemins.append((w, ids, {code: role}))
            provisoires.add(w)
        modif_voisines["modifies"].update(res["modifies"])
        modif_voisines["neufs"].update(res["neufs"])
        for rid, coupes in res["relations"].items():
            modif_voisines["relations"].setdefault(rid, []).extend(coupes)
        modif_voisines["liberes"] |= res["liberes"]
        rapport += res["rapport"]
    # Un chemin coupé chez une voisine peut servir à une autre relation que
    # l'on modifie déjà (autre voisine, ou lot) : ses morceaux entrent
    # dans ses nouveaux membres, juste après lui, au lieu d'un second envoi
    # de la même relation.
    par_id = {r.id: c for c, r in dict(relations, **rels_voisines).items() if c in nouvelles}
    for rid in list(modif_voisines["relations"]):
        if rid not in par_id:
            continue
        code = par_id[rid]
        for w, morceaux in modif_voisines["relations"].pop(rid):
            res_m = []
            for m in nouvelles[code]:
                res_m.append(m)
                if m["type"] == "way" and m["ref"] == w:
                    res_m += [{"type": "way", "ref": n, "role": m["role"]} for n in morceaux]
            nouvelles[code] = res_m
    # Nœuds existants auxquels s'accrochent raccords et copies.
    for _, ids, _ in chemins:
        for n in ids:
            if n > 0 and n not in existants:
                existants[n] = index.point(n)
    gardes = {m["ref"] for lst in nouvelles.values() for m in lst if m["type"] == "way" and m["ref"] > 0}
    retires = sorted(anciens - gardes)
    toutes = dict(relations, **{c: r for c, r in rels_voisines.items() if c in nouvelles})
    modifiees = sorted(c for c, rel in toutes.items()
                       if cles_membres(rel.rel["members"]) != cles_membres(nouvelles[c]))
    return {"noeuds": noeuds, "existants": existants, "chemins": chemins, "reutilises": reutilises,
            "membres": nouvelles, "modifiees": modifiees, "retires": retires, "rapport": rapport,
            "lot": sorted(relations), "voisines": modif_voisines, "provisoires": provisoires}


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
        if code not in plan.get("lot", plan["membres"]):
            continue
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
    res = {"noeuds": {}, "chemins": {}, "modifies": {}, "relations": {}, "rapport": [], "coupes": []}
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
        res["coupes"].append(wid)
        res["rapport"].append("way %d (%s) coupé en %d morceaux" % (
            wid, w.get("tags", {}).get("name", ""), len(morceaux)))
    return res


SENS = ("oneway", "forward", "backward", "incline", "direction", "turn")


def fusions_possibles(index, coupures_, anciennes):
    """Coupures d'une route sur une ancienne limite qui ne servent plus :
    celles « devenues inutiles », et l'ancienne coupure d'une « coupure à
    déplacer ». Une coupure entre deux segments aux étiquettes différentes
    (un pont, un changement de revêtement) sert à quelque chose : elle
    n'est pas retenue. Renvoie [(nœud, chemin, chemin)] : les deux chemins
    du même nom qui s'y rejoignent."""
    grille_a = geo.Grille([l for l in anciennes if len(l) > 1])
    par_noeud = defaultdict(list)
    for w in index.chemins.values():
        t = w.get("tags", {})
        if "highway" in t and "name" in t:
            for n in {w["nodes"][0], w["nodes"][-1]}:
                par_noeud[n].append(w["id"])
    res, vus = [], set()
    for action, nom, wid, p, _, _ in coupures_:
        if action not in ("coupure devenue inutile", "coupure à déplacer") or wid not in index.chemins:
            continue
        bouts = [n for n in (index.chemins[wid]["nodes"][0], index.chemins[wid]["nodes"][-1])
                 if n in index.noeuds and len([x for x in par_noeud[n]
                                               if index.chemins[x]["tags"].get("name") == nom]) == 2]
        if not bouts:
            continue
        n = min(bouts, key=lambda b: geo.distance(index.point(b), p))
        da = grille_a.distance(index.point(n))
        if n in vus or da is None or da >= COUPURE_M:
            continue
        vus.add(n)
        a, b = sorted(x for x in par_noeud[n] if index.chemins[x]["tags"].get("name") == nom)
        if index.chemins[a].get("tags") != index.chemins[b].get("tags"):
            continue
        res.append((n, a, b))
    return res


def fusionner(index, candidats, decoupe, rels_par_chemin, rels_actuelles):
    """Fusionne les deux chemins de chaque coupure inutile, après les
    coupures neuves (decoupe, modifié sur place). Le chemin le plus ancien
    est gardé, l'autre supprimé et retiré de ses relations. Refusé si les
    étiquettes ou les relations diffèrent (une ligne d'autobus qui ne
    couvre qu'un côté, par exemple), ou s'il faudrait retourner un chemin
    à sens unique."""
    decoupe.setdefault("supprimes", [])
    decoupe.setdefault("fusions", [])
    for n, a, b in candidats:
        if a in decoupe["supprimes"] or b in decoupe["supprimes"]:
            continue
        nom = index.chemins[a]["tags"].get("name", "")
        na = decoupe["modifies"].get(a, index.chemins[a]["nodes"])
        nb = decoupe["modifies"].get(b, index.chemins[b]["nodes"])
        ta, tb = index.chemins[a].get("tags", {}), index.chemins[b].get("tags", {})
        raison = None
        if ta != tb:
            raison = "étiquettes différentes"
        elif rels_par_chemin.get(a, set()) != rels_par_chemin.get(b, set()):
            raison = "relations différentes"
        elif any(sorted(m["role"] for m in rels_actuelles[r]["members"] if m["type"] == "way" and m["ref"] == a) !=
                 sorted(m["role"] for m in rels_actuelles[r]["members"] if m["type"] == "way" and m["ref"] == b)
                 for r in rels_par_chemin.get(a, set())):
            raison = "rôles différents"
        if raison is None:
            if na[-1] == n and nb[0] == n:
                noeuds = na + nb[1:]
            elif na[0] == n and nb[-1] == n:
                noeuds = nb + na[1:]
            elif any(s in k for k in ta for s in SENS):
                raison = "sens opposés sur un chemin à sens unique"
            elif na[-1] == n and nb[-1] == n:
                noeuds = na + nb[::-1][1:]
            else:
                noeuds = nb[::-1] + na[1:]
        if raison is None and (noeuds[0] == noeuds[-1] or len(set(noeuds)) != len(noeuds)):
            raison = "le chemin fusionné ferait une boucle"
        if raison:
            decoupe["fusions"].append("way %d et way %d (%s) : fusion refusée, %s" % (a, b, nom, raison))
            continue
        decoupe["modifies"][a] = noeuds
        decoupe["modifies"].pop(b, None)
        decoupe["supprimes"].append(b)
        for r in rels_par_chemin.get(b, set()):
            membres = decoupe["relations"].get(r, rels_actuelles[r]["members"])
            decoupe["relations"][r] = [m for m in membres if not (m["type"] == "way" and m["ref"] == b)]
        decoupe["fusions"].append("way %d et way %d (%s) fusionnés : way %d supprimé" % (a, b, nom, b))
