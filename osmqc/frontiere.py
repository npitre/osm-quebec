# Raccord des limites municipales à la frontière du Québec, gardée telle
# qu'elle est dans OSM (frontières avec l'Ontario, le Nouveau-Brunswick,
# les États-Unis, Terre-Neuve-et-Labrador, le Nunavut et en mer : à
# discuter, voir rapports/Quebec/).
#
# Un arc du MRNF qui suit la frontière du Québec selon le MRNF (table
# regio_l) n'est pas tracé : la municipalité garde les chemins de la
# frontière d'OSM. Un arc qui aboutit à la frontière (point triple du
# MRNF) est prolongé ou raccourci jusqu'à la frontière d'OSM; le chemin
# de la frontière y est coupé en deux, sans être déplacé (un nœud ajouté
# au besoin), et toutes les relations qui le contenaient (Québec,
# provinces et pays voisins, municipalités) reçoivent le morceau neuf
# juste après lui. Chaque arc de frontière du MRNF va d'un point triple
# à un autre : la municipalité reçoit les morceaux de la frontière d'OSM
# entre les deux points de raccord correspondants. Si la
# frontière d'OSM est introuvable près d'un point triple, la municipalité
# est tracée d'après le MRNF, comme ailleurs, et le cas est signalé.

import copy
from collections import defaultdict

from . import geo

SUR_M = 1.0             # un arc à moins de 1 m de la frontière du MRNF la suit
CHERCHE_M = 3000        # frontière d'OSM cherchée à moins de 3 km du point triple
NOEUD_M = 1.0           # un nœud existant à moins de 1 m sert de point de coupe


def suit(grille, pts):
    """Vrai si tous les sommets sont sur la frontière du MRNF."""
    return all(grille.ecart(p, rayon_deg=0.001) < SUR_M for p in pts)


class Segments:
    """Segments des chemins de la frontière d'OSM, par cases, pour trouver
    croisements et points les plus proches."""

    def __init__(self, index, chemins, pas=0.02):
        self.pas = pas
        self.cases = defaultdict(list)
        for w in chemins:
            ns = index.chemins[w]["nodes"]
            for i, (a, b) in enumerate(zip(ns, ns[1:])):
                pa, pb = index.point(a), index.point(b)
                for c in self._cases(min(pa[0], pb[0]), min(pa[1], pb[1]), max(pa[0], pb[0]), max(pa[1], pb[1])):
                    self.cases[c].append((w, i, pa, pb))

    def _cases(self, o, s, e, n):
        for i in range(int(o // self.pas), int(e // self.pas) + 1):
            for j in range(int(s // self.pas), int(n // self.pas) + 1):
                yield (i, j)

    def autour(self, p, rayon_deg=0.03):
        vus = set()
        for c in self._cases(p[0] - rayon_deg, p[1] - rayon_deg, p[0] + rayon_deg, p[1] + rayon_deg):
            for s in self.cases.get(c, ()):
                if (s[0], s[1]) not in vus:
                    vus.add((s[0], s[1]))
                    yield s


def projete(p, a, b):
    """Point du segment [a, b] le plus proche de p, et sa position t."""
    kx = geo.math.cos(geo.math.radians(p[1]))
    dx, dy = (b[0] - a[0]) * kx, b[1] - a[1]
    t = ((p[0] - a[0]) * kx * dx + (p[1] - a[1]) * dy) / ((dx * dx + dy * dy) or 1)
    t = max(0.0, min(1.0, t))
    return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])), t


def raccord(pts, depuis_fin, segments):
    """Point où l'arc rejoint la frontière d'OSM, en partant de son bout sur
    la frontière du MRNF : le croisement le plus proche de ce bout (à moins
    de CHERCHE_M), sinon le point de la frontière le plus proche du bout.
    Renvoie (nouveaux sommets de l'arc, (chemin, segment, t, point)), ou
    None si la frontière d'OSM est trop loin."""
    seq = pts[::-1] if depuis_fin else list(pts)
    bout = seq[0]
    parcouru = 0.0
    for k in range(len(seq) - 1):
        a, b = seq[k], seq[k + 1]
        for w, i, pa, pb in segments.autour(a):
            x = geo.intersection(a, b, pa, pb)
            if x is not None:
                _, t = projete(x, pa, pb)
                nouveaux = [x] + seq[k + 1:]
                return (nouveaux[::-1] if depuis_fin else nouveaux), (w, i, t, x)
        parcouru += geo.distance(a, b)
        if parcouru > CHERCHE_M:
            break
    meilleur = None
    for w, i, pa, pb in segments.autour(bout):
        x, t = projete(bout, pa, pb)
        d = geo.distance(bout, x)
        if d < CHERCHE_M and (meilleur is None or d < meilleur[0]):
            meilleur = (d, (w, i, t, x))
    if meilleur is None:
        return None
    x = meilleur[1][3]
    nouveaux = [x] + seq
    return (nouveaux[::-1] if depuis_fin else nouveaux), meilleur[1]


def parcours(voisins, depart, arrivee, interdits):
    """Plus court chemin (liste de chemins OSM) de depart à arrivee dans le
    graphe de la frontière, sans passer par un nœud interdit, ou None."""
    import heapq
    if depart == arrivee:
        return None
    file = [(0.0, depart, [])]
    vus = set()
    while file:
        d, n, chemins = heapq.heappop(file)
        if n == arrivee:
            return chemins
        if n in vus:
            continue
        vus.add(n)
        if n != depart and n in interdits:
            continue
        for m, w, longueur in voisins.get(n, ()):
            if m not in vus:
                heapq.heappush(file, (d + longueur, m, chemins + [w]))
    return None


def raccorder(tous, reste, lot, voisines, sauter, lignes_mrnf, chemins_osm, index, relations,
              noeud, nouveau_chemin, usages, arrondi):
    """Raccorde les arcs du lot à la frontière d'OSM (voir l'en-tête).
    tous : [(points, {code: rôle})] arcs du lot, modifiés sur place;
    reste : {code: [points]} arcs des voisines qui ne touchent pas le lot;
    lot, voisines : codes; sauter : arcs déjà traités autrement (contour
    repris d'une relation parente); lignes_mrnf : frontière du Québec selon
    le MRNF; chemins_osm : chemins de la relation du Québec dans OSM;
    relations : {code: Relation} du lot et des voisines, mises à jour sur
    place comme si la coupe était faite (leurs membres d'origine gardés
    dans .membres_origine); noeud(p) : nœud à la position p (neuf ou
    existant enregistré).
    Renvoie un dict : arcs de frontière à ne pas tracer, morceaux de la
    frontière par municipalité du lot, morceaux à retirer de chaque
    voisine, chemins coupés et morceaux neufs, relations hors du lot qui
    reçoivent les morceaux, nœuds existants utilisés, rapport."""
    res = {"arcs": set(), "morceaux": defaultdict(list), "retirer": defaultdict(set), "modifies": {},
           "neufs": {}, "relations": {}, "existants": {}, "rapport": [], "nouveaux_noeuds": {},
           "frontiere": set(), "noeuds_raccord": set()}
    if not lignes_mrnf or not chemins_osm:
        return res
    chemins_osm = [w for w in chemins_osm if w in index.chemins
                   and all(n in index.noeuds for n in index.chemins[w]["nodes"])]
    g_mrnf = geo.Grille(lignes_mrnf, pas=0.02)
    # Un arc d'une seule municipalité peut suivre la frontière en partie
    # seulement (le sud d'un contour ouest-sud) : le couper là où il la
    # quitte.
    for k in range(len(tous)):
        pts, roles = tous[k]
        if k in sauter or len(roles) != 1:
            continue
        sur = [suit(g_mrnf, [a, b, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)]) for a, b in zip(pts, pts[1:])]
        if all(sur) or not any(sur):
            continue
        debut = 0
        morceaux = []
        for i in range(1, len(sur) + 1):
            if i == len(sur) or sur[i] != sur[debut]:
                morceaux.append(pts[debut:i + 1])
                debut = i
        if pts[0] == pts[-1] and len(morceaux) > 1 and sur[0] == sur[-1]:
            morceaux[0] = morceaux.pop()[:-1] + morceaux[0]
        tous[k] = (morceaux[0], roles)
        tous.extend((m, dict(roles)) for m in morceaux[1:])
    frontiere = {k for k, (pts, roles) in enumerate(tous)
                 if k not in sauter and len(roles) == 1 and suit(g_mrnf, pts)}
    arcs_voisines = {c: [pts for pts in reste.get(c, []) if suit(g_mrnf, pts)] for c in voisines}
    if not frontiere:
        return res
    triples = {arrondi(tous[k][0][i]) for k in frontiere for i in (0, -1)}
    triples |= {arrondi(pts[i]) for l in arcs_voisines.values() for pts in l for i in (0, -1)}
    segments = Segments(index, chemins_osm)

    # Points de raccord des arcs qui aboutissent à la frontière.
    coupes = defaultdict(list)          # chemin -> [(segment, t, point)]
    x_de_p = {}                         # point triple du MRNF -> point de raccord
    noeud_de_x = {}                     # point de raccord -> nœud
    raccordes = {}
    echecs = set()
    for k, (pts, roles) in enumerate(tous):
        if k in frontiere or k in sauter:
            continue
        for depuis_fin in (False, True):
            if arrondi(pts[-1 if depuis_fin else 0]) not in triples:
                continue
            r = raccord(raccordes.get(k, pts), depuis_fin, segments)
            if r is None:
                echecs |= set(roles) & set(lot)
                continue
            raccordes[k] = r[0]
            w, i, t, x = r[1]
            coupes[w].append((i, t, x))
            x_de_p[arrondi(pts[-1 if depuis_fin else 0])] = arrondi(x)
    if echecs:
        for k in list(frontiere):
            if set(tous[k][1]) & echecs:
                frontiere.discard(k)
        res["rapport"].append("frontière d'OSM introuvable près d'un point triple : %s tracé(s) d'après "
                              "le MRNF" % ", ".join(sorted(echecs)))
    for k, pts in raccordes.items():
        tous[k] = (pts, tous[k][1])
    res["arcs"] = frontiere

    # Coupe des chemins de la frontière aux points de raccord, sans les
    # déplacer : chaque relation qui les contient reçoit les morceaux.
    for r in relations.values():
        r.membres_origine = copy.deepcopy(r.rel["members"])
    morceaux_de = {}
    a_signaler = []     # (chemin coupé, morceaux neufs, relations déjà servies)
    nb_coupes = 0
    exacts = {}
    for w, pts in sorted(coupes.items()):
        e = index.chemins[w]
        ns = list(e["nodes"])
        positions = []
        for i, t, x in sorted(pts, key=lambda c: (c[0], c[1])):
            proche = min((i, i + 1), key=lambda j: geo.distance(index.point(ns[j]), x))
            if geo.distance(index.point(ns[proche]), x) < NOEUD_M:
                n = ns[proche]
                res["existants"][n] = index.point(n)
                # L'arc prend la position exacte du nœud existant (sinon un
                # arrondi différent empêcherait de le reconnaître).
                exacts[arrondi(x)] = index.point(n)
            else:
                n = noeud(x)
                res["nouveaux_noeuds"][n] = x
            positions.append((i, t, n))
            noeud_de_x[arrondi(x)] = n
        # Insérer les nœuds neufs après leur segment (de la fin vers le début).
        for i, t, n in sorted(positions, reverse=True):
            if n not in ns:
                ns.insert(i + 1, n)
                index.noeuds.setdefault(n, {"type": "node", "id": n, "lon": res["nouveaux_noeuds"][n][0],
                                            "lat": res["nouveaux_noeuds"][n][1], "tags": {}})
        coupures = sorted({ns.index(n) for _, _, n in positions} - {0, len(ns) - 1})
        if not coupures:
            continue                    # raccord au bout du chemin : rien à couper
        nb_coupes += len(coupures)
        bornes = [0] + coupures + [len(ns) - 1]
        pieces = [ns[a:b + 1] for a, b in zip(bornes, bornes[1:])]
        res["modifies"][w] = pieces[0]
        e["nodes"] = pieces[0]
        nouveaux = []
        for p in pieces[1:]:
            nw = nouveau_chemin()
            res["neufs"][nw] = (p, dict(e.get("tags", {})))
            index.chemins[nw] = {"type": "way", "id": nw, "nodes": p, "tags": dict(e.get("tags", {}))}
            nouveaux.append(nw)
        morceaux_de[w] = [w] + nouveaux
        ici = set()
        for r in relations.values():
            membres = []
            for m in r.rel["members"]:
                membres.append(m)
                if m["type"] == "way" and m["ref"] == w:
                    membres += [{"type": "way", "ref": n, "role": m["role"]} for n in nouveaux]
            if len(membres) != len(r.rel["members"]):
                r.rel["members"] = membres
                r.chemins = [m["ref"] for m in membres if m["type"] == "way"]
                ici.add(r.id)
        a_signaler.append((w, nouveaux, ici))
    # Les autres relations des chemins coupés (le Québec, la province
    # voisine...), en une seule lecture.
    u = usages([w for w, _, _ in a_signaler]) if a_signaler else {}
    for w, nouveaux, ici in a_signaler:
        for rid in u.get(w, set()) - ici:
            res["relations"].setdefault(rid, []).append((w, nouveaux))
    for k in raccordes:
        pts, roles = tous[k]
        pts = [exacts.get(arrondi(p), p) if i in (0, len(pts) - 1) else p for i, p in enumerate(pts)]
        tous[k] = (pts, roles)
    for xa, p in exacts.items():
        if xa in noeud_de_x:
            noeud_de_x[arrondi(p)] = noeud_de_x[xa]
        for pp, xx in list(x_de_p.items()):
            if xx == xa:
                x_de_p[pp] = arrondi(p)
    if nb_coupes:
        res["rapport"].append("frontière : %d chemin(s) coupé(s) en %d point(s), sans être déplacés"
                              % (len(morceaux_de), nb_coupes))

    # Attribution des morceaux de la frontière : chaque arc de frontière du
    # MRNF va d'un point triple à un autre; ses morceaux sont ceux du plus
    # court chemin, le long de la frontière d'OSM, entre leurs deux points
    # de raccord (sans passer par un autre point de raccord).
    candidats = {w for ws in morceaux_de.values() for w in ws} | set(chemins_osm)
    res["frontiere"] = candidats
    res["noeuds_raccord"] = set(noeud_de_x.values())
    voisins = defaultdict(list)
    for w in candidats:
        ns = index.chemins[w]["nodes"]
        longueur = sum(geo.distance(index.point(a), index.point(b)) for a, b in zip(ns, ns[1:]))
        voisins[ns[0]].append((ns[-1], w, longueur))
        voisins[ns[-1]].append((ns[0], w, longueur))
    raccords = set(noeud_de_x.values())
    for k in sorted(frontiere):
        pts, roles = tous[k]
        (code, role), = roles.items()
        if code in echecs:
            continue
        x1 = noeud_de_x.get(x_de_p.get(arrondi(pts[0])))
        x2 = noeud_de_x.get(x_de_p.get(arrondi(pts[-1])))
        chemin = parcours(voisins, x1, x2, raccords) if x1 is not None and x2 is not None else None
        if not chemin:
            res["rapport"].append("frontière : arc de %s sans parcours entre ses points de raccord" % code)
            continue
        for w in chemin:
            res["morceaux"][code].append(w)
            for c in voisines:
                if c in relations and w in relations[c].chemins:
                    res["retirer"][c].add(w)
    return res
