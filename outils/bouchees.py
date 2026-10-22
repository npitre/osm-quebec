# Découpage du Québec méridional en bouchées pour l'import des limites
# municipales : des groupes de municipalités voisines, chacun assez petit
# pour un seul groupe de modifications d'OSM (10 000 objets au plus).
# Une MRC qui tient dans le budget forme une bouchée, et deux MRC
# voisines de la même région qui tiennent ensemble sont réunies; une MRC
# trop grosse est coupée en groupes de municipalités voisines.
#
# Laissés de côté, pour une discussion à part : la Côte-Nord et le
# Nord-du-Québec (régions 09 et 10), les municipalités qui dépassent à
# elles seules le budget et celles qui n'ont pas de relation dans OSM.
#
# Lit rapports/Quebec/inventaire.csv (outils/inventaire.py) et les
# polygones du MRNF; écrit rapports/Quebec/bouchees.md et bouchees.csv,
# et, avec --lieux, un fichier de lieu par bouchée dans lieux/quebec/.
#
# Usage, depuis la racine du dépôt :
#   python3 outils/bouchees.py [--lieux]

import collections
import csv
import os
import re
import sqlite3
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from osmqc import geo, rapport, regions  # noqa: E402

SDA = os.environ.get("OSMQC_SDA", os.path.join("donnees", "SDA.gpkg"))
DOSSIER = os.path.join("rapports", "Quebec")
LIEUX = os.path.join("lieux", "quebec")
# Objets estimés par bouchée, au pire (voir Couts). Le fichier d'envoi
# réel de la bouchée 1 compte 6,6 % de plus (routes coupées, raccords
# des voisines) : 8 000 laisse de la marge sous la limite de 10 000.
BUDGET = 8000
REGIONS_A_PART = {"09": "Côte-Nord", "10": "Nord-du-Québec"}
VERSION = "V2026-09"


def nb(n):
    return format(int(n), ",").replace(",", " ")


def voisinage(codes):
    """Municipalités voisines (au moins deux sommets du MRNF en commun),
    centre approximatif et sommets de chacune : ({code: {voisines}},
    {code: (lon, lat)}, {code: {sommets}})."""
    db = sqlite3.connect("file:%s?mode=ro" % SDA, uri=True)
    par_point = collections.defaultdict(set)
    somme, sommets = {}, collections.defaultdict(set)
    for code, g in db.execute("select MUS_CO_GEO, geom from munic_s"):
        if code not in codes:
            continue
        pts = {regions.arrondi(p) for poly in geo.wkb_gpkg(g) for a in poly for p in a}
        sommets[code] |= pts
        for p in pts:
            par_point[p].add(code)
        sx, sy, n = somme.get(code, (0, 0, 0))
        somme[code] = (sx + sum(p[0] for p in pts), sy + sum(p[1] for p in pts), n + len(pts))
    communs = collections.Counter()
    for muns in par_point.values():
        if len(muns) > 1:
            for a in muns:
                for b in muns:
                    if a < b:
                        communs[(a, b)] += 1
    vois = collections.defaultdict(set)
    for (a, b), k in communs.items():
        if k >= 2:
            vois[a].add(b)
            vois[b].add(a)
    centres = {c: (sx / n, sy / n) for c, (sx, sy, n) in somme.items()}
    return vois, centres, sommets


class Couts:
    """Objets estimés d'un groupe de municipalités, au pire : tous ses
    sommets du MRNF distincts (la première bouchée qui touche une limite
    commune la crée en entier), plus sa part des nœuds d'OSM à supprimer."""

    def __init__(self, sommets, anciens):
        self.sommets, self.anciens = sommets, anciens

    def unite(self, codes):
        pts = set().union(*(self.sommets[c] for c in codes))
        return pts, len(pts) + sum(self.anciens[c] for c in codes)

    def ajout(self, pts, c):
        """Objets ajoutés par la municipalité c à un groupe de sommets pts."""
        return len(self.sommets[c] - pts) + self.anciens[c]


def couper(muns, couts, vois, centres):
    """Groupes de municipalités voisines d'au plus BUDGET objets. muns :
    codes d'une MRC trop grosse. Chaque groupe part d'un « coin » (la
    municipalité qui a le moins de voisines libres, la plus à l'ouest en
    cas d'égalité) et prend d'abord les voisines les plus enclavées, pour
    ne pas laisser de poches isolées; les petits restes sont réunis plus
    tard à une bouchée voisine."""
    # Une enclave (une seule voisine, de la même MRC) va avec sa
    # municipalité hôte.
    hote = {c: next(iter(vois[c])) for c in muns if len(vois[c]) == 1 and next(iter(vois[c])) in muns}
    bloc = lambda c: [e for e, h in hote.items() if h == c]
    reste = set(muns) - set(hote)
    libres = lambda c: len(vois[c] & reste)
    groupes = []
    while reste:
        depart = min(reste, key=lambda c: (libres(c), centres[c]))
        g = [depart] + bloc(depart)
        pts, total = couts.unite(g)
        reste.difference_update(g)
        while True:
            bord = [c for c in {v for x in g for v in vois[x]} & reste
                    if total + sum(couts.ajout(pts, x) for x in [c] + bloc(c)) <= BUDGET]
            if not bord:
                break
            cx = sum(centres[c][0] for c in g) / len(g)
            cy = sum(centres[c][1] for c in g) / len(g)
            c = min(bord, key=lambda c: (libres(c), (centres[c][0] - cx) ** 2 + (centres[c][1] - cy) ** 2))
            g += [c] + bloc(c)
            pts, total = couts.unite(g)
            reste.difference_update(g)
        groupes.append(g)
    return groupes


def decouper(lignes):
    """Bouchées du Québec méridional : [{regions, mrcs, codes, estimation}],
    et les municipalités laissées de côté : [(ligne, raison)]."""
    a_part, candidates = [], []
    for l in lignes:
        if l["region"] in REGIONS_A_PART:
            a_part.append((l, "région %s %s" % (l["region"], REGIONS_A_PART[l["region"]])))
        elif not l["relation"]:
            a_part.append((l, "absente d'OSM"))
        else:
            candidates.append(l)
    vois, centres, sommets = voisinage({l["code"] for l in candidates})
    couts = Couts(sommets, {l["code"]: int(l["estimation"]) - int(l["sommets_mrnf"]) for l in candidates})
    retenues = []
    for l in candidates:
        l["seule"] = couts.unite([l["code"]])[1]
        if l["seule"] > BUDGET:
            a_part.append((l, "plus de %s objets" % nb(BUDGET)))
        else:
            retenues.append(l)
    codes = {l["code"] for l in retenues}
    vois = collections.defaultdict(set, {c: vs & codes for c, vs in vois.items() if c in codes})
    info = {l["code"]: l for l in retenues}
    bouchees = []
    par_region = collections.OrderedDict()
    for l in retenues:
        par_region.setdefault(l["region"], collections.OrderedDict()).setdefault(l["mrc"], []).append(l["code"])
    for reg, mrcs in par_region.items():
        unites = []
        for mrc, muns in mrcs.items():
            groupes = [muns] if couts.unite(muns)[1] <= BUDGET else couper(muns, couts, vois, centres)
            for k, g in enumerate(groupes):
                pts, total = couts.unite(g)
                unites.append({"regions": [reg], "mrcs": [mrc], "parties": [(mrc, k + 1, len(groupes))],
                               "codes": sorted(g), "points": pts, "estimation": total})
        # Réunir deux unités voisines de la région tant qu'elles tiennent
        # ensemble, les plus petites d'abord.
        reunir(unites, vois, lambda a, b: True)
        bouchees += unites
    # Puis une petite bouchée (moins de la moitié du budget) avec une
    # voisine d'une autre région : Laval, ou un reste isolé par une
    # municipalité laissée de côté.
    reunir(bouchees, vois, lambda a, b: min(a["estimation"], b["estimation"]) < BUDGET / 2)
    # Enfin, une très petite bouchée (moins du quart du budget) sans
    # voisine qui ait de la place, souvent séparée des autres par un TNO
    # aquatique absent d'OSM, rejoint la bouchée la plus proche (moins de
    # 50 km) qui en a.
    centre = lambda u: (sum(centres[c][0] for c in u["codes"]) / len(u["codes"]),
                        sum(centres[c][1] for c in u["codes"]) / len(u["codes"]))
    for u in sorted([u for u in bouchees if u["estimation"] < BUDGET / 4], key=lambda u: u["estimation"]):
        if u not in bouchees:
            continue
        proches = [(geo.distance(centre(u), centre(v)), id(v), v) for v in bouchees
                   if v is not u and u["estimation"] + v["estimation"] <= BUDGET]
        proches = [p for p in proches if p[0] < 50000]
        if proches:
            v = min(proches)[2]
            fusion(v, u)
            bouchees.remove(u)
    bouchees.sort(key=lambda u: (min(u["regions"]), min(u["mrcs"])))
    for k, b in enumerate(bouchees, 1):
        b["numero"] = k
        b["nom"] = nom_bouchee(b, info)
    return bouchees, a_part, info


def reunir(unites, vois, permis):
    """Réunit deux à deux les unités voisines qui tiennent ensemble dans
    le budget (et que permis(a, b) accepte), les plus petites d'abord.
    unites : liste modifiée sur place."""
    while True:
        paires = []
        for i, a in enumerate(unites):
            va = {v for c in a["codes"] for v in vois[c]}
            for b in unites[i + 1:]:
                if va & set(b["codes"]) and permis(a, b):
                    total = a["estimation"] + b["estimation"] - len(a["points"] & b["points"])
                    if total <= BUDGET:
                        paires.append((total, id(a), id(b), a, b))
        if not paires:
            return
        _, _, _, a, b = min(paires)
        fusion(a, b)
        unites.remove(b)


def fusion(a, b):
    """Ajoute l'unité b à l'unité a."""
    for k in ("regions", "mrcs"):
        a[k] += [m for m in b[k] if m not in a[k]]
    a["parties"] += b["parties"]
    a["codes"] = sorted(a["codes"] + b["codes"])
    a["estimation"] += b["estimation"] - len(a["points"] & b["points"])
    a["points"] |= b["points"]


def nom_bouchee(b, info):
    noms = {}
    for c in b["codes"]:
        noms.setdefault(info[c]["mrc"], info[c]["nom_mrc"])
    parties = []
    for mrc, k, n in b["parties"]:
        parties.append(noms[mrc] + (" (%d de %d)" % (k, n) if n > 1 else ""))
    return ", ".join(parties)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")


def ecrire_lieu(b, info):
    """Fichier de lieu d'une bouchée : ses municipalités et leurs
    relations, pour les limites seulement."""
    nom = "Q%03d-%s" % (b["numero"], slug(b["nom"].split(",")[0].split(" (")[0]))
    s = "# Bouchée %d de l'import des limites du Québec méridional (outils/bouchees.py).\n" % b["numero"]
    s += "# Ne pas modifier à la main : relancer outils/bouchees.py --lieux.\n\n"
    s += "nom = %s\n\n" % toml_texte("%s (bouchée %d)" % (b["nom"], b["numero"]))
    s += "[rqa]\nmunicipalites = [%s]\n\n" % ", ".join('"%s"' % c for c in b["codes"])
    s += "[regions.osm]\n"
    for c in b["codes"]:
        s += '"%s" = %s   # %s\n' % (c, info[c]["relation"], info[c]["nom"])
    s += "\n[regions.groupe]\n"
    s += "comment = %s\n" % toml_texte("Limites municipales (%s) d'après les Découpages administratifs du MRNF"
                                       % b["nom"])
    s += "source = %s\n" % toml_texte("Découpages administratifs (MRNF), version %s" % VERSION)
    s += "# discussion = \"\"   # obligatoire avant un envoi réel\n"
    os.makedirs(LIEUX, exist_ok=True)
    with open(os.path.join(LIEUX, nom + ".toml"), "w", encoding="utf-8") as fh:
        fh.write(s)
    return nom


def toml_texte(s):
    return '"%s"' % s.replace("\\", "\\\\").replace('"', '\\"')


def main():
    with open(os.path.join(DOSSIER, "inventaire.csv"), encoding="utf-8") as fh:
        lignes = list(csv.DictReader(fh))
    bouchees, a_part, info = decouper(lignes)
    noms = {}
    if "--lieux" in sys.argv[1:]:
        noms = {b["numero"]: ecrire_lieu(b, info) for b in bouchees}
    with open(os.path.join(DOSSIER, "bouchees.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["bouchee", "code", "nom", "mrc", "region", "estimation"])
        for b in bouchees:
            for c in b["codes"]:
                w.writerow([b["numero"], c, info[c]["nom"], info[c]["mrc"], info[c]["region"],
                            info[c]["estimation"]])
    rapport.ecrire(os.path.join(DOSSIER, "bouchees.md"), texte(bouchees, a_part, info, noms))
    print("Bouchées : %d, de %s à %s objets estimés; %d municipalités laissées de côté." % (
        len(bouchees), nb(min(b["estimation"] for b in bouchees)), nb(max(b["estimation"] for b in bouchees)),
        len(a_part)))


def texte(bouchees, a_part, info, noms):
    total = sum(b["estimation"] for b in bouchees)
    s = "# Bouchées du Québec méridional\n\n"
    s += ("Découpage des municipalités du Québec méridional en bouchées pour l'import des limites, "
          "chacune assez petite pour un seul groupe de modifications d'OSM. Produit par "
          "`outils/bouchees.py`, d'après l'[inventaire](inventaire.md); détail dans "
          "[bouchees.csv](bouchees.csv).\n\n")
    s += ("Budget : %s objets estimés par bouchée, au pire : tous les sommets distincts du MRNF de "
          "ses municipalités (la première bouchée qui touche une limite commune la crée en entier), "
          "plus leur part des nœuds d'OSM à supprimer. Le fichier d'envoi réel de la bouchée 1 compte "
          "6,6 %% de plus (routes coupées, raccords des voisines), sous la limite de 10 000 objets "
          "d'OSM; les bouchées suivantes coûtent moins, puisqu'elles reprennent les limites déjà "
          "conformes. Une MRC qui tient dans le budget forme une bouchée; deux MRC voisines "
          "de la même région qui tiennent ensemble sont réunies; une MRC trop grosse est coupée en "
          "groupes de municipalités voisines, en partant de l'ouest.\n\n" % nb(BUDGET))
    s += rapport.tableau(["Bouchées", "Municipalités", "Objets estimés, au pire", "Moyenne par bouchée",
                          "Laissées de côté"],
                         [[len(bouchees), sum(len(b["codes"]) for b in bouchees), nb(total),
                           nb(total / len(bouchees)), len(a_part)]])
    s += "\n## Bouchées\n\n"
    entetes = ["N°", "Région", "MRC", "Municipalités", "Objets estimés"] + (["Lieu"] if noms else [])
    s += rapport.tableau(entetes, [
        [b["numero"], ", ".join(b["regions"]), b["nom"], len(b["codes"]), nb(b["estimation"])]
        + (["`lieux/quebec/%s.toml`" % noms[b["numero"]]] if noms else []) for b in bouchees])
    s += "\n## Laissées de côté\n\n"
    raisons = collections.Counter(r if not r.startswith("région") else r for _, r in a_part)
    s += rapport.tableau(["Raison", "Municipalités", "Objets estimés"],
                         [[r, k, nb(sum(l.get("seule", int(l["estimation"])) for l, rr in a_part if rr == r))]
                          for r, k in sorted(raisons.items())])
    grosses = [(l, r) for l, r in a_part if r.startswith("plus de")]
    if grosses:
        s += "\n### Plus de %s objets, hors des régions 09 et 10\n\n" % nb(BUDGET)
        s += rapport.tableau(["Code", "Municipalité", "MRC", "Région", "Objets estimés"],
                             [[l["code"], l["nom"], l["nom_mrc"], l["nom_region"], nb(l["seule"])]
                              for l, _ in sorted(grosses, key=lambda x: -x[0]["seule"])])
    return s


if __name__ == "__main__":
    main()
