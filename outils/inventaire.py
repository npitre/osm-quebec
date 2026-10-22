# Inventaire de tout le Québec avant l'import des limites municipales :
# pour chaque municipalité du MRNF, sa relation dans OSM, le nombre de
# sommets de son tracé officiel et de nœuds de sa relation actuelle, et
# une estimation du nombre d'objets à envoyer; par MRC et par région, les
# totaux. Sert à choisir les bouchées. Écrit rapports/Quebec/inventaire.md
# et rapports/Quebec/inventaire.csv.
#
# Usage, depuis la racine du dépôt (quelques minutes) :
#   python3 outils/inventaire.py
#
# Estimation : sommets du MRNF à créer (un sommet partagé par deux
# municipalités compte pour moitié à chacune), plus les nœuds des simples
# lignes de limite d'OSM, supprimés quand plus rien ne s'en sert (même
# partage). Les routes à couper ne sont pas comptées : dans la
# Petite-Nation, elles ajoutent environ 5 %.

import collections
import csv
import os
import sqlite3
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import osmium  # noqa: E402

from osmqc import extrait, geo, osm, progres, rapport, regions  # noqa: E402

PBF = extrait.chemin()
SDA = os.environ.get("OSMQC_SDA", os.path.join("donnees", "SDA.gpkg"))
DOSSIER = os.path.join("rapports", "Quebec")
LIMITE = 10000          # objets par groupe de modifications (API d'OSM)
SEUIL = 9000            # au-delà, une municipalité ne tient pas dans un seul envoi
LIEN = "[%d](https://www.openstreetmap.org/relation/%d)"


def mrnf():
    """{code: {nom, mrc, nom_mrc, region, nom_region, polygones}}; une
    municipalité en plusieurs entités voit ses polygones réunis."""
    db = sqlite3.connect("file:%s?mode=ro" % SDA, uri=True)
    res = {}
    for code, nom, mrc, nmrc, reg, nreg, g in db.execute(
            "select MUS_CO_GEO, MUS_NM_MUN, MUS_CO_MRC, MUS_NM_MRC, MUS_CO_REG, MUS_NM_REG, geom "
            "from munic_s order by MUS_CO_GEO"):
        m = res.setdefault(code, {"nom": nom, "mrc": mrc, "nom_mrc": nmrc, "region": reg,
                                  "nom_region": nreg, "polygones": []})
        m["polygones"] += geo.wkb_gpkg(g)
    return res


def relations_osm():
    """Relations boundary=administrative portant un ref:qc :
    {ref:qc: [(id, nom, admin_level)]}, toutes, pour voir les doublons."""
    res = collections.defaultdict(list)
    fp = osmium.FileProcessor(PBF, osmium.osm.RELATION).with_filter(
        osmium.filter.TagFilter(("boundary", "administrative")))
    for o in progres.suivre(fp, PBF, "relations de limite (ref:qc)"):
        if o.tags.get("ref:qc"):
            res[o.tags["ref:qc"]].append((o.id, o.tags.get("name", ""), o.tags.get("admin_level", "")))
    return res


def parts(ensembles):
    """Part de chaque clé dans des ensembles de points ou de nœuds qui se
    recoupent : un élément commun à k clés compte 1/k pour chacune."""
    compte = collections.Counter()
    for pts in ensembles.values():
        compte.update(pts)
    return {c: sum(1 / compte[p] for p in pts) for c, pts in ensembles.items()}


def main():
    progres.etape("Municipalités du MRNF")
    muns = mrnf()
    sommets = parts({c: {regions.arrondi(p) for poly in m["polygones"] for a in poly for p in a}
                     for c, m in muns.items()})
    par_ref = relations_osm()
    trouvees = {}
    for c in muns:
        rels = [r for r in par_ref.get(c, []) if r[2] == "8"]
        if rels:
            trouvees[c] = rels[0][0]
    progres.etape("Relations des %d municipalités trouvées dans OSM" % len(trouvees))
    index = osm.Index(extrait.relations(PBF, sorted(set(trouvees.values()))))
    progres.etape("Composition des relations")
    noeuds_limite, info = {}, {}
    for c, rid in trouvees.items():
        r = index.relations.get(rid)
        if r is None:
            continue
        ws = [m["ref"] for m in r["members"] if m["type"] == "way"]
        presents = [w for w in ws if w in index.chemins]
        genres = collections.Counter(regions.genre_chemin(index.chemins[w].get("tags", {})) for w in presents)
        _, ouverts = geo.assembler([index.chemins[w]["nodes"] for w in presents])
        noeuds_limite[c] = {n for w in presents if regions.ligne_de_limite(index.chemins[w].get("tags", {}))
                            for n in index.chemins[w]["nodes"]}
        tous = {n for w in presents for n in index.chemins[w]["nodes"]}
        info[c] = {"chemins": len(ws), "noeuds": len(tous), "genres": genres, "ouverts": ouverts,
                   "incomplete": len(presents) != len(ws)}
    anciens = parts(noeuds_limite)

    progres.etape("Rapport")
    lignes = []
    for c, m in sorted(muns.items(), key=lambda kv: (kv[1]["region"], kv[1]["mrc"], kv[0])):
        i = info.get(c, {})
        est = round(sommets[c] + anciens.get(c, 0)) if c in trouvees else 0
        g = i.get("genres", collections.Counter())
        littoral = sum(k for genre, k in g.items() if genre.startswith("natural="))
        eau = sum(k for genre, k in g.items() if genre.startswith("waterway="))
        notes = []
        if c not in trouvees:
            autres = par_ref.get(c, [])
            notes.append("absente" + (" (niveau %s)" % "/".join(r[2] for r in autres) if autres else ""))
        elif len([r for r in par_ref[c] if r[2] == "8"]) > 1:
            notes.append("ref:qc en double")
        if i.get("ouverts"):
            notes.append("anneau ouvert")
        if i.get("incomplete"):
            notes.append("membres hors de l'extrait")
        if est > SEUIL:
            notes.append("plus de %d objets" % SEUIL)
        lignes.append({"code": c, "nom": m["nom"], "mrc": m["mrc"], "nom_mrc": m["nom_mrc"],
                       "region": m["region"], "nom_region": m["nom_region"], "relation": trouvees.get(c, ""),
                       "sommets_mrnf": round(sommets[c]), "noeuds_osm": i.get("noeuds", 0),
                       "chemins_osm": i.get("chemins", 0), "littoral": littoral, "cours_d_eau": eau,
                       "estimation": est, "notes": "; ".join(notes)})
    with open(os.path.join(DOSSIER, "inventaire.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lignes[0]))
        w.writeheader()
        w.writerows(lignes)
    rapport.ecrire(os.path.join(DOSSIER, "inventaire.md"), texte(lignes, len(muns)))
    print("Inventaire : %d municipalités, %d dans OSM, %d objets estimés." % (
        len(lignes), len(trouvees), sum(l["estimation"] for l in lignes)))


def texte(lignes, total):
    presentes = [l for l in lignes if l["relation"]]
    est = sum(l["estimation"] for l in lignes)
    s = "# Inventaire des limites municipales du Québec\n\n"
    s += ("Chaque municipalité des Découpages administratifs du MRNF (table `munic_s`), sa relation "
          "d'OSM (`ref:qc`, niveau 8), le nombre de sommets de son tracé officiel et de nœuds de sa "
          "relation actuelle, et une estimation des objets à envoyer pour la remplacer. Produit par "
          "`outils/inventaire.py`; détail par municipalité dans [inventaire.csv](inventaire.csv).\n\n")
    s += ("Estimation : sommets du MRNF à créer, plus nœuds des simples lignes de limite d'OSM à "
          "supprimer; un sommet ou un nœud commun à deux municipalités compte pour moitié à chacune. "
          "Les routes à couper ne sont pas comptées (environ 5 %% de plus dans la Petite-Nation). "
          "Un groupe de modifications d'OSM accepte au plus %s objets.\n\n" % nb(LIMITE))
    s += rapport.tableau(
        ["Municipalités du MRNF", "Dans OSM", "Sommets du MRNF", "Nœuds dans OSM", "Objets estimés",
         "Envois de 9 000 objets, au moins"],
        [[total, len(presentes), nb(sum(l["sommets_mrnf"] for l in lignes)),
          nb(sum(l["noeuds_osm"] for l in lignes)), nb(est), nb(-(-est // SEUIL))]])

    s += "\n## Par région\n\n"
    regs = collections.OrderedDict()
    for l in lignes:
        regs.setdefault((l["region"], l["nom_region"]), []).append(l)
    s += rapport.tableau(["Région", "Municipalités", "Dans OSM", "MRC", "Sommets du MRNF", "Nœuds dans OSM",
                          "Objets estimés"],
                         [["%s %s" % k, len(ls), sum(1 for l in ls if l["relation"]), len({l["mrc"] for l in ls}),
                           nb(sum(l["sommets_mrnf"] for l in ls)), nb(sum(l["noeuds_osm"] for l in ls)),
                           nb(sum(l["estimation"] for l in ls))] for k, ls in regs.items()])

    grandes = sorted((l for l in lignes if l["estimation"] > SEUIL), key=lambda l: -l["estimation"])
    s += "\n## Municipalités de plus de %s objets\n\n" % nb(SEUIL)
    s += ("Elles ne tiennent pas dans un seul groupe de modifications : leurs chemins neufs devront "
          "être envoyés en plusieurs fois avant la modification de la relation.\n\n")
    s += rapport.tableau(["Code", "Municipalité", "MRC", "Relation", "Sommets du MRNF", "Nœuds dans OSM",
                          "Littoral", "Objets estimés"],
                         [[l["code"], l["nom"], l["nom_mrc"], lien(l["relation"]), nb(l["sommets_mrnf"]),
                           nb(l["noeuds_osm"]), l["littoral"], nb(l["estimation"])] for l in grandes])

    cotes = sorted((l for l in presentes if l["littoral"]), key=lambda l: -l["littoral"])
    s += "\n## Relations faites en partie de littoral\n\n"
    s += ("Chemins `natural=*` membres de la relation (littoral, surtout). La règle 2 les retire de la "
          "relation, et la limite devient un chemin distinct.\n\n")
    s += rapport.tableau(["Code", "Municipalité", "MRC", "Relation", "Chemins", "Dont natural=*",
                          "Dont waterway=*"],
                         [[l["code"], l["nom"], l["nom_mrc"], lien(l["relation"]), l["chemins_osm"], l["littoral"],
                           l["cours_d_eau"]] for l in cotes]) if cotes else "Aucune.\n"

    autres = [l for l in lignes if l["notes"] and "plus de" not in l["notes"]]
    s += "\n## Autres cas à noter\n\n"
    s += ("Absentes (voir aussi [municipalites.md](municipalites.md)), `ref:qc` en double, anneau "
          "ouvert dans OSM, membres hors de l'extrait.\n\n")
    s += rapport.tableau(["Code", "Municipalité", "MRC", "Relation", "Notes"],
                         [[l["code"], l["nom"], l["nom_mrc"], lien(l["relation"]), l["notes"]]
                          for l in autres]) if autres else "Aucun.\n"

    s += "\n## Par MRC\n\n"
    mrcs = collections.OrderedDict()
    for l in lignes:
        mrcs.setdefault((l["region"], l["mrc"], l["nom_mrc"]), []).append(l)
    s += rapport.tableau(["Région", "MRC", "Municipalités", "Dans OSM", "Sommets du MRNF", "Nœuds dans OSM",
                          "Objets estimés", "Plus grosse municipalité"],
                         [[r, "%s %s" % (m, n), len(ls), sum(1 for l in ls if l["relation"]),
                           nb(sum(l["sommets_mrnf"] for l in ls)), nb(sum(l["noeuds_osm"] for l in ls)),
                           nb(sum(l["estimation"] for l in ls)),
                           "%s (%s)" % (max(ls, key=lambda l: l["estimation"])["nom"],
                                        nb(max(l["estimation"] for l in ls)))]
                          for (r, m, n), ls in mrcs.items()])
    return s


def nb(n):
    return format(int(n), ",").replace(",", " ")


def lien(rid):
    return LIEN % (rid, rid) if rid else ""


if __name__ == "__main__":
    main()
