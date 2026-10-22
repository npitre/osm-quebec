# Voisines d'un lot de municipalités : celles qui partagent une limite
# avec le lot sans en faire partie. Le remplacement des limites se fait
# par bouchées; chaque envoi doit laisser OSM valide. L'arc commun entre
# une municipalité du lot (A) et une voisine (B) devient donc un seul
# chemin, membre de A et de B, et la relation de B est modifiée en
# partie :
#
#   - les anciens chemins de B qui longent A en sont retirés;
#   - l'arc commun s'arrête au point triple du MRNF, la partie gardée de B
#     à l'ancien point triple d'OSM : un court chemin de raccord, membre
#     de B seulement, les relie. Il disparaît quand B est traitée à son
#     tour (simple ligne de limite qui ne sert plus);
#   - un ancien chemin de limite de B qui ne longe A qu'en partie est
#     coupé au dernier sommet gardé : raccourci s'il ne sert qu'à B,
#     sinon coupé en deux pour que ses autres relations ne changent pas;
#   - un littoral, une route ou un cours d'eau n'est jamais coupé ni
#     modifié (règle 2) : la partie gardée en est recopiée dans un chemin
#     de limite distinct, avec ses propres nœuds, et il est retiré de B.
#
# Si l'anneau de B ne se referme pas, B n'est pas touchée et le cas est
# signalé.

import sqlite3

from . import geo

EPS_M = 1.0     # un sommet également proche des deux tracés est gardé


def voisines(chemin, codes):
    """Municipalités du MRNF qui partagent au moins un côté avec celles
    données, sans en faire partie : {code: (nom, version, polygones)}."""
    from .regions import sda
    codes = set(codes)
    lot = sda(chemin, codes)
    cotes = set()
    o = s = 1e9
    e = n = -1e9
    for _, _, polys in lot.values():
        for poly in polys:
            for anneau in poly:
                for a, b in zip(anneau, anneau[1:]):
                    cotes.add(frozenset((a, b)))
                    o, s = min(o, a[0]), min(s, a[1])
                    e, n = max(e, a[0]), max(n, a[1])
    db = sqlite3.connect("file:%s?mode=ro" % chemin, uri=True)
    tables = {r[0] for r in db.execute("select name from sqlite_master")}
    if "rtree_munic_s_geom" in tables:
        proches = [r[0] for r in db.execute(
            "select m.MUS_CO_GEO from munic_s m join rtree_munic_s_geom r on r.id = m.fid "
            "where r.maxx >= ? and r.minx <= ? and r.maxy >= ? and r.miny <= ?", (o, e, s, n))]
    else:
        proches = [r[0] for r in db.execute("select MUS_CO_GEO from munic_s")]
    candidats = sda(chemin, [c for c in proches if c not in codes])
    res = {}
    for code, (nom, ver, polys) in candidats.items():
        if any(frozenset((a, b)) in cotes
               for poly in polys for anneau in poly for a, b in zip(anneau, anneau[1:])):
            res[code] = (nom, ver, polys)
    return res


def _distance(grille, lignes, p):
    d = grille.distance(p, rayon_deg=0.01)
    if d is None:
        d = min((geo.distance_ligne(p, l) for l in lignes if len(l) > 1), default=1e12)
    return d


def _une_portion_par_chaine(anneaux, bouts, nb_chaines, point, index, imposes):
    """Chaque portion d'un anneau qui longe le lot est remplacée par une
    chaîne de l'arc commun, raccordée à ses deux bouts. anneaux : [(V,
    le_long)], tous les anneaux de la relation. S'il y a plus de portions
    que de chaînes, l'ancien tracé ne fait que frôler le lot ailleurs (le
    long d'une frontière gardée, par exemple) : seules restent retirées
    les portions dont les extrémités sont les plus proches des bouts de
    chaîne; les autres sont gardées. Une portion qui contient un nœud
    imposé (morceau de frontière à retirer) reste retirée. Renvoie les
    le_long corrigés."""
    portions = []           # (anneau, indices)
    for k, (V, le_long) in enumerate(anneaux):
        n = len(V)
        debut = next((i for i in range(n) if le_long[i - 1] and not le_long[i]), None)
        if debut is None:
            continue
        for d in range(n):
            j = (debut + d) % n
            if le_long[j] and not le_long[j - 1]:
                portions.append((k, [j]))
            elif le_long[j]:
                portions[-1][1].append(j)
    pos = lambda m: point(m) if m < 0 else index.point(m)
    if not portions and bouts:
        # Aucun nœud ne longe le lot : l'ancien tracé passe au large de
        # l'arc commun par un long segment. On retire, pour chaque chaîne,
        # les nœuds de l'anneau le plus proche compris entre ceux qui sont
        # les plus proches de ses deux bouts, par le plus court chemin.
        res = [list(l) for _, l in anneaux]
        for a, b in zip(bouts[::2], bouts[1::2]):
            k = min(range(len(anneaux)), key=lambda k: min(geo.distance(pos(n), point(a)) for n in anneaux[k][0]))
            V = anneaux[k][0]
            ia = min(range(len(V)), key=lambda i: geo.distance(pos(V[i]), point(a)))
            ib = min(range(len(V)), key=lambda i: geo.distance(pos(V[i]), point(b)))
            avant = (ib - ia) % len(V)
            js = [(ia + d) % len(V) for d in range(avant + 1)] if avant <= len(V) - avant \
                else [(ib + d) % len(V) for d in range(len(V) - avant + 1)]
            if len(js) < len(V):
                for j in js:
                    res[k][j] = True
        return res
    if len(portions) <= max(nb_chaines, 1) or not bouts:
        return [l for _, l in anneaux]

    def ecart(p):
        # Les nœuds gardés juste avant et juste après la portion.
        V = anneaux[p[0]][0]
        a, b = V[(p[1][0] - 1) % len(V)], V[(p[1][-1] + 1) % len(V)]
        return max(min(geo.distance(pos(a), point(c)) for c in bouts),
                   min(geo.distance(pos(b), point(c)) for c in bouts))
    forcees = [p for p in portions if any(anneaux[p[0]][0][j] in imposes for j in p[1])]
    libres = sorted((p for p in portions if p not in forcees), key=ecart)
    retirees = forcees + libres[:max(0, nb_chaines - len(forcees))]
    res = [[False] * len(V) if any(le_long) and not all(le_long) else list(le_long) for V, le_long in anneaux]
    for k, js in retirees:
        for j in js:
            res[k][j] = True
    return res


def modifier(rel, index, communs, autres, point, noeud, nouveau_chemin, usages, lot, retirer=frozenset(),
             garder=frozenset()):
    """Modification partielle de la relation rel (une voisine B).
    communs : [(chemin, [nœuds], rôle)] chemins de l'arc commun avec le lot
    (neufs ou réutilisés), qui deviennent membres de B; autres : polylignes
    du reste du contour de B selon le MRNF; point(nœud) : position d'un
    nœud neuf ou existant; noeud(p) : nœud neuf à la position p;
    nouveau_chemin() : identifiant négatif libre; usages(chemins) :
    {chemin: {relations}} dans tout OSM; lot : identifiants des relations
    du lot; retirer : morceaux de la frontière du Québec attribués au lot,
    à retirer de B; garder : morceaux de la frontière que B garde, jamais
    classés le long du lot (voir osmqc/frontiere.py).
    Renvoie (résultat, None) ou (None, raison). Résultat : membres de B,
    chemins neufs de B (raccords et copies), chemins raccourcis ou coupés,
    morceaux neufs et relations où ils entrent, nœuds libérés, chemins
    retirés de B, rapport."""
    roles = {m["ref"]: m["role"] for m in rel.rel["members"] if m["type"] == "way"}
    anciens = [w for w in rel.chemins if w in index.chemins]
    if len(anciens) != len(rel.chemins):
        return None, "membres absents de l'extrait"
    aretes = {}
    for w in anciens:
        ns = index.chemins[w]["nodes"]
        for a, b in zip(ns, ns[1:]):
            aretes.setdefault(frozenset((a, b)), w)
    anneaux, ouverts = geo.assembler([index.chemins[w]["nodes"] for w in anciens])
    if ouverts:
        return None, "anneau ouvert dans OSM"
    # Déjà raccordée (envoi précédent) : l'arc commun en fait partie et son
    # anneau est fermé. Rien à faire.
    if all(w in roles for w, _, _ in communs) and not retirer:
        return {"membres": list(rel.rel["members"]), "chemins": [], "modifies": {}, "neufs": {},
                "relations": {}, "liberes": set(), "retires": [], "rapport": []}, None

    lignes_c = [[point(n) for n in ids] for _, ids, _ in communs]
    grille_c = geo.Grille(lignes_c)
    grille_o = geo.Grille(autres) if autres else None

    # Morceaux de la frontière du Québec attribués au lot : retirés de B.
    gardes_b = {n for w in anciens if w not in retirer for n in index.chemins[w]["nodes"]}
    forces = {n for w in retirer if w in index.chemins for n in index.chemins[w]["nodes"]} - gardes_b

    gardes_fr = {n for w in garder if w in index.chemins for n in index.chemins[w]["nodes"]}

    def longe(n):
        if n in gardes_fr:
            return False
        if n in forces:
            return True
        p = index.point(n)
        if grille_o is None:
            return True
        return _distance(grille_c, lignes_c, p) + EPS_M < _distance(grille_o, autres, p)

    # Bouts libres de l'arc commun : là où les raccords s'accrochent.
    chaines, _ = geo.assembler([ids for _, ids, _ in communs])
    bouts = [c[k] for c in chaines if c[0] != c[-1] for k in (0, -1)]
    role_bout = {n: r for _, ids, r in communs for n in (ids[0], ids[-1])}

    from .regions import frontiere, ligne_de_limite

    def modifiable(tags):
        """Une simple ligne de limite (pas une frontière, pas un littoral,
        une route ou un cours d'eau) : on peut la couper."""
        return ligne_de_limite(tags) and not frontiere(tags)

    garder = []         # (chemin, rôle) existants gardés tels quels
    modifies = {}       # chemin -> nœuds (raccourci ou coupé)
    neufs = {}          # morceau neuf -> (nœuds, étiquettes)
    relations = {}      # relation -> membres, avec les morceaux neufs
    chemins = []        # (chemin neuf, nœuds, rôle) : copies et raccords
    liberes = set()
    rapport = []
    nb_raccords = nb_copies = nb_coupes = 0
    morceaux_par_chemin = {}

    plans = []
    corriges = _une_portion_par_chaine([(a[:-1], [longe(n) for n in a[:-1]]) for a in anneaux], bouts,
                                       len(bouts) // 2, point, index, forces)
    for anneau, le_long in zip(anneaux, corriges):
        V = anneau[:-1]
        if not any(le_long):
            plans.append(("entier", anneau, None))
            continue
        if all(le_long):
            continue                    # remplacé en entier par l'arc commun
        debut = next(i for i in range(len(V)) if le_long[i - 1] and not le_long[i])
        V = V[debut:] + V[:debut]
        le_long = le_long[debut:] + le_long[:debut]
        troncons, cur = [], []
        for n, l in zip(V, le_long):
            if not l:
                cur.append(n)
            elif cur:
                troncons.append(cur)
                cur = []
        if cur:
            troncons.append(cur)
        plans.append(("troncons", anneau, troncons))
        for t in troncons:
            for a, b in zip(t, t[1:]):
                w = aretes[frozenset((a, b))]
                morceaux_par_chemin.setdefault(w, set()).add(id(t))

    for genre, anneau, troncons in plans:
        if genre == "entier":
            for a, b in zip(anneau, anneau[1:]):
                w = aretes[frozenset((a, b))]
                if (w, roles[w]) not in garder:
                    garder.append((w, roles[w]))
            continue
        for t in troncons:
            # Morceaux du tronçon gardé, chemin par chemin.
            morceaux = []
            for a, b in zip(t, t[1:]):
                w = aretes[frozenset((a, b))]
                if morceaux and morceaux[-1][0] == w:
                    morceaux[-1][1].append(b)
                else:
                    morceaux.append((w, [a, b]))
            # Nature de chaque morceau : gardé entier, coupé, ou recopié.
            natures = []
            for w, ns in morceaux:
                e = index.chemins[w]
                if len(ns) == len(e["nodes"]) and set(ns) == set(e["nodes"]):
                    natures.append("entier")
                elif modifiable(e.get("tags", {})) and len(morceaux_par_chemin.get(w, ())) == 1:
                    natures.append("coupé")
                else:
                    natures.append("copie")
            debut_t, fin_t = t[0], t[-1]
            for k, ((w, ns), nature) in enumerate(zip(morceaux, natures)):
                e = index.chemins[w]
                tags = e.get("tags", {})
                role = roles[w]
                if nature == "entier":
                    garder.append((w, role))
                elif nature == "coupé":
                    if e["nodes"][0] == e["nodes"][-1]:
                        # Chemin fermé : la partie gardée est ns elle-même,
                        # le reste finit d'en faire le tour. Le sens du
                        # chemin est conservé.
                        cycle = e["nodes"][:-1]
                        k0 = cycle.index(ns[0])
                        tour = cycle[k0:] + cycle[:k0] + [ns[0]]
                        if tour[:len(ns)] == ns:
                            garde, restes = ns, [tour[len(ns) - 1:]]
                        else:
                            tour = tour[::-1]
                            garde, restes = ns[::-1], [tour[len(ns) - 1:][::-1]]
                    else:
                        i, j = sorted((e["nodes"].index(ns[0]), e["nodes"].index(ns[-1])))
                        garde = e["nodes"][i:j + 1]
                        restes = [r for r in (e["nodes"][:i + 1], e["nodes"][j:]) if len(r) > 1]
                    autres_rels = usages([w]).get(w, set()) - {rel.id} - set(lot)
                    modifies[w] = garde
                    garder.append((w, role))
                    nb_coupes += 1
                    if autres_rels:
                        nouveaux = []
                        for r in restes:
                            nw = nouveau_chemin()
                            neufs[nw] = (r, dict(tags))
                            nouveaux.append(nw)
                        for rid in autres_rels:
                            relations.setdefault(rid, []).append((w, nouveaux))
                    else:
                        liberes.update(n for r in restes for n in r if n not in garde)
                else:
                    # Littoral, route, cours d'eau : copie distincte de la
                    # partie gardée. Le nœud de jonction avec un morceau
                    # existant voisin est gardé; tous les autres sont neufs.
                    ids = []
                    for x, n in enumerate(ns):
                        voisin = k - 1 if x == 0 else k + 1 if x == len(ns) - 1 else None
                        existant = voisin is not None and 0 <= voisin < len(natures) and natures[voisin] != "copie"
                        ids.append(n if existant else noeud(index.point(n)))
                    chemins.append((nouveau_chemin(), ids, role))
                    nb_copies += 1
                    if k == 0:
                        debut_t = ids[0]
                    if k == len(morceaux) - 1:
                        fin_t = ids[-1]
            # Raccords : chaque bout du tronçon gardé va au bout libre de
            # l'arc commun le plus proche.
            for n in (debut_t, fin_t):
                p = point(n) if n < 0 else index.point(n)
                if not bouts:
                    return None, "aucun bout libre sur l'arc commun"
                b = min(bouts, key=lambda c: geo.distance(point(c), p))
                bouts.remove(b)
                if b == n:
                    continue
                if geo.distance(point(b), p) < 0.01:
                    return None, "raccord de longueur nulle"
                chemins.append((nouveau_chemin(), [b, n], role_bout.get(b, "outer")))
                nb_raccords += 1

    membres = [m for m in rel.rel["members"] if m["type"] != "way"]
    membres += [{"type": "way", "ref": w, "role": r} for w, r in garder]
    membres += [{"type": "way", "ref": w, "role": r} for w, _, r in chemins]
    membres += [{"type": "way", "ref": w, "role": r} for w, _, r in communs]
    vus = set()
    membres = [m for m in membres if not ((m["type"], m["ref"], m["role"]) in vus
                                          or vus.add((m["type"], m["ref"], m["role"])))]

    # L'anneau de B doit se refermer.
    def noeuds_de(w):
        if w in modifies:
            return modifies[w]
        # Un chemin négatif hors des raccords et de l'arc commun : morceau
        # neuf d'une coupe précédente, ajouté à l'index.
        return next((ids for x, ids, _ in chemins + communs if x == w), None) or index.chemins[w]["nodes"]
    _, ouverts = geo.assembler([noeuds_de(m["ref"]) for m in membres if m["type"] == "way"])
    if ouverts:
        return None, "l'anneau ne se referme pas"
    gardes = {m["ref"] for m in membres if m["type"] == "way"}
    retires = sorted(w for w in anciens if w not in gardes)
    if retires or chemins or modifies:
        rapport.append("%s : %d chemin(s) retiré(s), %d raccord(s), %d copie(s), %d chemin(s) coupé(s)" % (
            rel.tags.get("name", rel.id), len(retires), nb_raccords, nb_copies, nb_coupes))
    return {"membres": membres, "chemins": chemins, "modifies": modifies, "neufs": neufs,
            "relations": relations, "liberes": liberes, "retires": retires, "rapport": rapport}, None
