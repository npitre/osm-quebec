# Frontières du Québec et municipalités absentes d'OSM : comparaison des
# Découpages administratifs du MRNF à l'extrait d'OSM, pour la discussion
# sur les limites. Écrit rapports/Quebec/frontieres.md,
# rapports/Quebec/municipalites.md et rapports/Quebec/frontieres.geojson.
#
# Usage, depuis la racine du dépôt (une dizaine de minutes) :
#   python3 outils/frontieres.py
#
# Facultatif : le contour officiel de l'Ontario (jeu « Province » de
# Géospatial Ontario, Licence du gouvernement ouvert de l'Ontario), pour
# comparer aussi la frontière Québec-Ontario à la version ontarienne :
#   https://ws.gisetl.lrc.gov.on.ca/fmedatadownload/Packages/PROVINCE.zip
# décompressé dans donnees/ontario/ (le fichier PROVINCE.shp y est cherché).

import bisect
import collections
import glob
import os
import re
import sqlite3
import statistics
import struct
import sys
import unicodedata

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import osmium  # noqa: E402

from osmqc import extrait, geo, osm, rapport  # noqa: E402

PBF = extrait.chemin()
SDA = os.environ.get("OSMQC_SDA", os.path.join("donnees", "SDA.gpkg"))
DOSSIER = os.path.join("rapports", "Quebec")

# Types de frontière du SDA (table regio_l, champ RES_CO_TYP).
FRONTIERES = {
    "FROINT": "États-Unis",
    "FRONB": "Nouveau-Brunswick",
    "FROONT": "Ontario",
    "FRO52": "Labrador, le long du 52e parallèle",
    "FROTN": "Labrador, ligne de partage des eaux",
    "FRONT": "Nunavut (baies d'Hudson et d'Ungava, détroit d'Hudson)",
    "FROGSL": "Golfe du Saint-Laurent (limites en mer)",
}
# Frontières en rivière : nom de la rivière dans OSM (expression régulière).
RIVIERES = {"FROONT": ("rivière des Outaouais", r"outaouais|ottawa"),
            "FRONB": ("Ristigouche et Patapédia", r"ristigouche|restigouche|patap")}
PAS_M = 200             # un point tous les 200 m le long des frontières
EAU_M = 3000            # un point à moins de 3 km de l'axe de la rivière est « en rivière »
LOIN = None             # aucun tracé à moins de 5 km


def densifier(ligne):
    res = [ligne[0]]
    for a, b in zip(ligne, ligne[1:]):
        k = max(1, int(geo.distance(a, b) // PAS_M))
        res += [(a[0] + (b[0] - a[0]) * i / k, a[1] + (b[1] - a[1]) * i / k) for i in range(1, k + 1)]
    return res


def distances(points, grille):
    return [grille.distance(p, rayon_deg=0.05) for p in points]


def resume(ds):
    """Médiane, 90e centile et parts au-delà de 20 m, 100 m et 1 km;
    LOIN (aucun tracé à moins de 5 km) compte comme très loin."""
    v = sorted(1e9 if d is None else d for d in ds)
    q = lambda f: v[int(f * (len(v) - 1))]
    fmt = lambda d: ("plus de 5 km" if d >= 1e9 else "%.0f m" % d if d < 1000
                     else ("%.1f km" % (d / 1000)).replace(".", ","))
    part = lambda s: "%d %%" % round(100 * sum(d > s for d in v) / len(v))
    return [len(v), fmt(q(.5)), fmt(q(.9)), part(20), part(100), part(1000)]


def frontieres_mrnf():
    db = sqlite3.connect("file:%s?mode=ro" % SDA, uri=True)
    res = collections.defaultdict(list)
    for typ, g in db.execute("select RES_CO_TYP, geom from regio_l"):
        if typ in FRONTIERES:
            res[typ] += geo.wkb_gpkg_lignes(g)
    return res


def relation_quebec():
    filtre = osmium.filter.TagFilter(("boundary", "administrative"))
    for o in osmium.FileProcessor(PBF, osmium.osm.RELATION).with_filter(filtre):
        if o.tags.get("admin_level") == "4" and o.tags.get("name") in ("Québec", "Quebec"):
            return o.id
    sys.exit("Relation du Québec introuvable dans l'extrait.")


def rivieres(motif, boite):
    """Axe (waterway=river) et rives (polygones natural=water) d'une
    rivière dans un rectangle : (lignes de l'axe, lignes des rives)."""
    noms = re.compile(motif, re.I)
    membres = set()
    for o in osmium.FileProcessor(PBF, osmium.osm.RELATION).with_filter(
            osmium.filter.TagFilter(("natural", "water"))):
        if noms.search(o.tags.get("name", "")):
            membres.update(m.ref for m in o.members if m.type == "w")
    dedans = lambda l: any(boite[0] <= x <= boite[2] and boite[1] <= y <= boite[3] for x, y in l[::5] + l[-1:])
    aucun = osmium.filter.KeyFilter("osmqc-aucun")
    aucun.enable_for(osmium.osm.NODE)
    axe, rives = [], []
    for o in osmium.FileProcessor(PBF, osmium.osm.NODE | osmium.osm.WAY).with_locations().with_filter(aucun):
        if not o.is_way():
            continue
        t = o.tags
        est_axe = t.get("waterway") == "river" and noms.search(t.get("name", ""))
        est_rive = o.id in membres or (t.get("natural") == "water" and noms.search(t.get("name", "")))
        if not (est_axe or est_rive):
            continue
        l = [(n.lon, n.lat) for n in o.nodes if n.location.valid()]
        if l and dedans(l):
            (axe if est_axe else rives).append(l)
    return axe, rives


def genre(t):
    return next((k + "=" + t[k] for k in ("waterway", "natural") if k in t), "limite seule")


def main():
    os.makedirs(DOSSIER, exist_ok=True)
    date = extrait.date(PBF)
    mrnf = frontieres_mrnf()
    qc = relation_quebec()
    idx = osm.Index(extrait.relations(PBF, [qc]))
    chemins = [w for w in (m["ref"] for m in idx.relations[qc]["members"] if m["type"] == "way")
               if w in idx.chemins]
    lignes_osm = {w: idx.ligne(w) for w in chemins}
    grille_osm = geo.Grille(list(lignes_osm.values()), pas=0.02)
    print("Relation du Québec : %d, %d chemins." % (qc, len(chemins)), flush=True)

    s = "# Frontières du Québec : MRNF et OSM\n\n"
    s += ("Comparaison des frontières du Québec selon les Découpages administratifs du MRNF "
          "(table `regio_l`) et de la relation du Québec dans OSM "
          "([%d](https://www.openstreetmap.org/relation/%d)), extrait de Geofabrik du %s. Un point "
          "tous les %d m le long de chaque frontière du MRNF; écart : distance au tracé d'OSM le "
          "plus proche. Produit par `outils/frontieres.py`. Commentaires : [README](README.md).\n\n"
          % (qc, qc, date.strftime("%Y-%m-%d") if date else "?", PAS_M))
    lignes = []
    carte = []
    for typ, nom in FRONTIERES.items():
        pts = [p for l in mrnf[typ] for p in densifier(l)]
        ds = distances(pts, grille_osm)
        lignes.append([nom, "`%s`" % typ] + resume(ds))
        carte += [(typ, p, d) for p, d in zip(pts, ds) if d is None or d > 100][::5]
        print(typ, lignes[-1], flush=True)
    s += rapport.tableau(["Frontière", "Code", "Points", "Écart médian", "90 % à moins de",
                          "Plus de 20 m", "Plus de 100 m", "Plus de 1 km"], lignes)

    compo = collections.Counter(genre(idx.chemins[w].get("tags", {})) for w in chemins)
    speciaux = [w for w in chemins if any(k.startswith("disputed") or k in ("note", "fixme", "description")
                                          for k in idx.chemins[w].get("tags", {}))]
    s += ("\nChemins de la relation du Québec : %s. Avec une étiquette `disputed*`, `note`, `fixme` "
          "ou `description` : %d.\n" % (", ".join("%s %d" % kv for kv in compo.most_common()), len(speciaux)))

    # Frontières en rivière : où passent les deux tracés?
    for typ, (riviere, motif) in RIVIERES.items():
        lm = mrnf[typ]
        grille_m = geo.Grille(lm, pas=0.02)
        tous = [p for l in lm for p in l]
        boite = (min(p[0] for p in tous) - 0.02, min(p[1] for p in tous) - 0.02,
                 max(p[0] for p in tous) + 0.02, max(p[1] for p in tous) + 0.02)
        pres = [w for w in chemins if any((grille_m.distance(p, 0.02) or 1e9) < EAU_M for p in lignes_osm[w][::5])]
        axe, rives = rivieres(motif, boite)
        g_axe, g_rive = geo.Grille(axe, pas=0.02), geo.Grille(rives, pas=0.02)
        s += "\n## %s : %s\n\n" % (FRONTIERES[typ], riviere)
        s += ("Chemins de la relation du Québec le long de cette frontière : %s. Axe de la rivière "
              "dans OSM : %d chemins `waterway=river`; rives : %d chemins des polygones d'eau.\n\n"
              % (", ".join("%s %d" % kv for kv in collections.Counter(
                  genre(idx.chemins[w].get("tags", {})) for w in pres).most_common()), len(axe), len(rives)))
        lignes = []
        sans_rives = False
        for source, polylignes, autre in (("MRNF", lm, grille_osm), ("OSM", [lignes_osm[w] for w in pres], grille_m)):
            pts = [p for l in polylignes for p in densifier(l)]
            eau = [p for p in pts if (g_axe.distance(p, 0.05) or 1e9) < EAU_M]
            terre = [p for p in pts if (g_axe.distance(p, 0.05) or 1e9) >= EAU_M]
            for partie, ps in (("en rivière", eau), ("ailleurs", terre)):
                if not ps:
                    continue
                for cible, g in (("l'autre tracé", autre), ("l'axe de la rivière", g_axe), ("la rive", g_rive)):
                    if partie == "ailleurs" and cible != "l'autre tracé":
                        continue
                    ds = distances(ps, g)
                    # Rives mal couvertes (plans d'eau d'un autre nom) : pas de mesure.
                    if cible == "la rive" and sum(d is None for d in ds) > 0.5 * len(ds):
                        sans_rives = True
                        continue
                    lignes.append([source, partie, cible] + resume(ds))
        s += rapport.tableau(["Tracé", "Partie", "Distance à", "Points", "Médiane", "90 % à moins de",
                              "Plus de 20 m", "Plus de 100 m", "Plus de 1 km"], lignes)
        if sans_rives:
            s += ("\nDistance aux rives non mesurée : la plupart des plans d'eau de la rivière ne "
                  "portent pas son nom dans OSM (lacs, élargissements).\n")
        print(typ, "rivière faite", flush=True)

    # Ontario, ligne terrestre au nord du 48e parallèle : écart est-ouest.
    m = sorted((p for l in mrnf["FROONT"] for p in l if p[1] > 48.0), key=lambda p: p[1])
    lats = [p[1] for p in m]
    lon_m = statistics.median(p[0] for p in m)

    def lon_mrnf(lat):
        i = min(max(bisect.bisect(lats, lat), 1), len(m) - 1)
        a, b = m[i - 1], m[i]
        t = 0 if b[1] == a[1] else (lat - a[1]) / (b[1] - a[1])
        return a[0] + t * (b[0] - a[0])
    par = collections.defaultdict(list)
    for w in chemins:
        for p in lignes_osm[w]:
            if lats[0] <= p[1] <= lats[-1] and abs(p[0] - lon_m) < 0.05:
                d = geo.distance(p, (lon_mrnf(p[1]), p[1]))
                par[int(p[1] * 2) / 2].append(d if p[0] > lon_m else -d)
    s += ("\n## Ontario : ligne terrestre au nord du 48e parallèle\n\n"
          "Ligne presque nord-sud, du lac Témiscamingue à la baie James : %d sommets au MRNF. "
          "Écart est-ouest des nœuds d'OSM (positif : OSM plus à l'est).\n\n" % len(m))
    s += rapport.tableau(["Latitude", "Nœuds d'OSM", "Écart médian"],
                         [[("%.1f" % k).replace(".", ","), len(v), "%+.0f m" % statistics.median(v)]
                          for k, v in sorted(par.items())])
    s += ontario(mrnf["FROONT"], [lignes_osm[w] for w in chemins], lon_mrnf, lats, lon_m)
    rapport.ecrire(os.path.join(DOSSIER, "frontieres.md"), s)
    rapport.ecrire_geojson_compact({"type": "FeatureCollection", "features": [
        {"type": "Feature", "geometry": {"type": "Point", "coordinates": list(p)},
         "properties": {"frontiere": FRONTIERES[typ], "ecart_m": round(d) if d is not None else None,
                        "marker-size": "small",
                        "marker-color": "#d62728" if d is None or d > 1000 else "#ff7f0e"}}
        for typ, p, d in carte]}, os.path.join(DOSSIER, "frontieres.geojson"))
    municipalites()


def polygone_shp(chemin):
    """Sommets du premier polygone d'un fichier shapefile (type 5), en
    coordonnées géographiques."""
    b = open(chemin, "rb").read()
    o = 108
    nb_parts, nb_pts = struct.unpack("<2i", b[o + 36:o + 44])
    q = o + 44 + 4 * nb_parts
    return [struct.unpack("<2d", b[q + 16 * i:q + 16 * i + 16]) for i in range(nb_pts)]


def ontario(lignes_mrnf, lignes_osm, lon_mrnf, lats, lon_m):
    """Frontière Québec-Ontario selon l'Ontario, comparée au MRNF et à OSM."""
    shp = glob.glob(os.path.join("donnees", "ontario", "**", "PROVINCE.shp"), recursive=True)
    if not shp:
        return ""
    on = polygone_shp(shp[0])
    g_on, g_m = geo.Grille([on], pas=0.02), geo.Grille(lignes_mrnf, pas=0.02)
    osm_qc = [l for l in lignes_osm if any((g_m.distance(p, 0.02) or 1e9) < EAU_M for p in l[::5])]
    g_osm = geo.Grille(osm_qc, pas=0.02)
    pts_osm = [p for l in osm_qc for p in l]
    pts_on = [p for p in on if (g_m.distance(p, 0.02) or 1e9) < EAU_M]
    pts_m = [p for l in lignes_mrnf for p in densifier(l)]
    s = ("\n## Ontario : tracé officiel de l'Ontario\n\n"
         "Contour de la province selon l'Ontario (jeu « Province » de Géospatial Ontario, tenu par "
         "le bureau de l'arpenteur général, Licence du gouvernement ouvert de l'Ontario; précision "
         "annoncée : à 100 m près). Distances entre les sommets ou nœuds de chaque tracé et l'autre "
         "tracé, le long de la frontière Québec-Ontario.\n\n")
    s += rapport.tableau(["Tracé", "Distance à", "Points", "Médiane", "90 % à moins de",
                          "Plus de 20 m", "Plus de 100 m", "Plus de 1 km"], [
        ["OSM", "Ontario"] + resume(distances(pts_osm, g_on)),
        ["Ontario", "OSM"] + resume(distances(pts_on, g_osm)),
        ["MRNF", "Ontario"] + resume(distances(pts_m, g_on)),
        ["Ontario", "MRNF"] + resume(distances(pts_on, g_m))])
    par = collections.defaultdict(list)
    for p in on:
        if lats[0] <= p[1] <= lats[-1] and abs(p[0] - lon_m) < 0.05:
            d = geo.distance(p, (lon_mrnf(p[1]), p[1]))
            par[int(p[1] * 2) / 2].append(d if p[0] > lon_m else -d)
    s += ("\nLigne terrestre au nord du 48e parallèle : écart est-ouest des sommets de l'Ontario "
          "par rapport au MRNF (positif : Ontario plus à l'est).\n\n")
    s += rapport.tableau(["Latitude", "Sommets de l'Ontario", "Écart médian"],
                         [[("%.1f" % k).replace(".", ","), len(v), "%+.0f m" % statistics.median(v)]
                          for k, v in sorted(par.items())])
    return s


DESIGNATIONS = {"M": "Municipalité", "V": "Ville", "P": "Paroisse", "VL": "Village", "CT": "Canton",
                "CU": "Cantons unis", "G": "Territoire aquatique (TNO aquatique)", "R": "Réserve indienne",
                "EI": "Établissement indien", "NO": "Territoire non organisé", "TI": "Terre inuite",
                "VN": "Village nordique", "VC": "Village cri", "VK": "Village naskapi",
                "TK": "Terre réservée naskapie", "TC": "Terre réservée crie", "GR": "Gouvernement régional"}


def cle(s):
    s = unicodedata.normalize("NFD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", s)


def municipalites():
    db = sqlite3.connect("file:%s?mode=ro" % SDA, uri=True)
    mrnf = list(db.execute("select MUS_CO_GEO, MUS_NM_MUN, MUS_CO_DES, MUS_NM_MRC, MUS_NM_REG from munic_s "
                           "order by MUS_CO_DES, MUS_NM_REG, MUS_NM_MUN"))
    codes = {c for c, *_ in mrnf}
    par_ref, par_nom = {}, collections.defaultdict(list)
    for o in osmium.FileProcessor(PBF, osmium.osm.RELATION).with_filter(
            osmium.filter.TagFilter(("boundary", "administrative"))):
        t = dict(o.tags)
        if t.get("ref:qc"):
            par_ref.setdefault(t["ref:qc"], (o.id, t.get("name"), t.get("admin_level")))
        if t.get("admin_level") in ("8", "9", "10"):
            par_nom[cle(t.get("name"))].append((o.id, t.get("name"), t.get("admin_level"), t.get("ref:qc")))
    absentes, homonymes = [], []
    for code, nom, des, mrc, reg in mrnf:
        if code in par_ref:
            continue
        (homonymes if par_nom.get(cle(nom)) else absentes).append((code, nom, des, mrc, reg))
    lien = lambda i: "[%d](https://www.openstreetmap.org/relation/%d)" % (i, i)
    s = "# Municipalités du MRNF absentes d'OSM\n\n"
    s += ("Municipalités des Découpages administratifs du MRNF (table `munic_s`) sans relation "
          "`boundary=administrative` portant leur code (`ref:qc`) dans OSM. Produit par "
          "`outils/frontieres.py`. Commentaires : [README](README.md).\n\n")
    s += rapport.tableau(["Municipalités du MRNF", "Trouvées par ref:qc", "Relation d'un autre code, même nom",
                          "Absentes"], [[len(mrnf), len(mrnf) - len(absentes) - len(homonymes),
                                         len(homonymes), len(absentes)]])
    s += "\n## Relation d'un autre code, ou sans code, portant le même nom\n\n"
    s += rapport.tableau(["Code", "Nom", "Désignation", "MRC", "Relations d'OSM de ce nom"], [
        [c, n, DESIGNATIONS.get(d, d), m, ", ".join("%s (niveau %s, ref:qc %s)" % (lien(i), lv, r or "aucun")
                                                   for i, _, lv, r in par_nom[cle(n)])]
        for c, n, d, m, _ in homonymes])
    s += "\n## Absentes\n\n"
    s += rapport.tableau(["Code", "Nom", "Désignation", "MRC", "Région"],
                         [[c, n, DESIGNATIONS.get(d, d), m, r] for c, n, d, m, r in absentes])
    # Les relations de région (niveau 5) et de MRC (6) ont leur propre série de codes.
    autres = sorted((r, v) for r, v in par_ref.items() if r not in codes and v[2] not in ("5", "6"))
    s += "\n## Municipalités d'OSM au code ref:qc inconnu du MRNF\n\n"
    s += rapport.tableau(["ref:qc", "Relation", "Nom", "Niveau"],
                         [[r, lien(i), n, lv] for r, (i, n, lv) in autres]) if autres else "Aucun.\n"
    rapport.ecrire(os.path.join(DOSSIER, "municipalites.md"), s)
    print("Municipalités : %d absentes, %d homonymes, %d codes inconnus." % (len(absentes), len(homonymes),
                                                                          len(autres)), flush=True)


if __name__ == "__main__":
    main()
