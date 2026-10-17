# Ligne de commande : python3 -m osmqc SECTION COMMANDE lieux/LIEU.toml
#
#   regions trouver     cherche dans OSM les relations des municipalités
#   regions comparer    compare les limites municipales d'OSM et du MRNF
#   regions preparer    construit le remplacement des limites d'OSM
#   regions envoyer     l'envoie (--test ou --reel)
#
#   rues preparer       noms de rue d'OSM comparés aux noms officiels
#   rues envoyer        envoie les renommages (--test ou --reel)
#
#   adresses extraire   extrait du RQA complet les adresses du lieu
#   adresses osm        télécharge les données OSM autour de ces adresses
#   adresses preparer   construit l'import d'adresses
#   adresses envoyer    l'envoie (--test : serveur de test; --reel : OSM)
#
# Données : donnees/LIEU/. Fichiers d'envoi : sortie/LIEU/. Rapports de
# révision (Markdown et GeoJSON, à publier) : rapports/LIEU/, où un
# README.md rédigé à la main commente les résultats.
# Le RQA complet est cherché dans donnees/RQA_CSV.zip (ou $OSMQC_RQA),
# les découpages du MRNF dans donnees/SDA.gpkg (ou $OSMQC_SDA), et
# l'extrait d'OSM dans donnees/quebec-latest.osm.pbf (ou $OSMQC_PBF).

import csv
import json
import os
import sys
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter

from . import adresses, envoi, extrait, osm, osmchange, positions, rapport, regions, rqa, rues


def lire_lieu(chemin):
    with open(chemin, "rb") as fh:
        conf = tomllib.load(fh)
    return os.path.splitext(os.path.basename(chemin))[0], conf


def dossier(*parties):
    d = os.path.join(*parties)
    os.makedirs(d, exist_ok=True)
    return d


def charger_adresses(lieu):
    chemin = os.path.join("donnees", lieu, "rqa.csv")
    if not os.path.exists(chemin):
        sys.exit("Lancez d'abord : python3 -m osmqc adresses extraire lieux/%s.toml" % lieu)
    return rqa.lire_extrait(chemin)


def version_rqa(lieu):
    with open(os.path.join("donnees", lieu, "rqa.csv"), encoding="utf-8") as fh:
        r = next(csv.DictReader(fh))
    return "version AQ" + r["date_diffusion_version"]


API_MAX_TUILES = 20     # sans extrait local, au plus 20 tuiles demandées à l'API


def chemin_pbf():
    """Extrait local d'OSM s'il existe, sinon None (repli sur l'API, pour
    une petite zone seulement)."""
    p = extrait.chemin()
    return p if os.path.exists(p) else None


def noter_source(lieu, texte):
    with open(os.path.join(dossier("donnees", lieu), "osm_source.txt"), "w") as fh:
        fh.write(texte + "\n")


def source_osm(lieu):
    try:
        return open(os.path.join("donnees", lieu, "osm_source.txt")).read().strip()
    except OSError:
        return "API d'OSM"


def chemin_sda():
    sda = os.environ.get("OSMQC_SDA", os.path.join("donnees", "SDA.gpkg"))
    if not os.path.exists(sda):
        sys.exit("Découpages du MRNF introuvables : %s (à télécharger de %s)" % (sda, regions.URL_SDA))
    return sda


# Adresses

def adresses_extraire(lieu, conf):
    zip_ = os.environ.get("OSMQC_RQA", os.path.join("donnees", "RQA_CSV.zip"))
    if not os.path.exists(zip_):
        sys.exit("RQA complet introuvable : %s (à télécharger de %s)" % (zip_, rqa.URL))
    c = conf.get("rqa", {})
    print("Lecture de %s (une minute ou deux)..." % zip_)
    lignes = rqa.lire_zip(zip_, municipalites(conf), c.get("odonymes"))
    rqa.ecrire_extrait(lignes, os.path.join(dossier("donnees", lieu), "rqa.csv"))
    print("%d lignes extraites." % len(lignes))


def lire_zone(lieu, pts, cles_noeuds=extrait.CLES_NOEUDS, cles_chemins=extrait.CLES_CHEMINS,
              marge=0.003):
    """Objets OSM autour des points : dans l'extrait local, ou à défaut
    par l'API pour une petite zone."""
    pbf = chemin_pbf()
    if pbf:
        d = extrait.verifier_fraicheur(pbf)
        noter_source(lieu, "extrait %s du %s" % (os.path.basename(pbf),
                                                 d.strftime("%Y-%m-%d") if d else "?"))
        print("Lecture de l'extrait (une minute environ)...")
        return extrait.zone(pbf, extrait.tuiles(pts, marge), cles_noeuds=cles_noeuds,
                            cles_chemins=cles_chemins)
    nb = len(extrait.tuiles(pts, marge, pas=0.05))
    if nb > API_MAX_TUILES:
        sys.exit("Zone trop grande pour l'API d'OSM (%d tuiles) : téléchargez l'extrait "
                 "du Québec (voir donnees/README.md)." % nb)
    noter_source(lieu, "API d'OSM")
    print("Pas d'extrait local : %d tuiles demandées à l'API d'OSM..." % nb)
    return osm.carte_autour(pts)


def adresses_osm(lieu, conf):
    pts = [a.point for a in charger_adresses(lieu)]
    elems = lire_zone(lieu, pts)
    with open(os.path.join(dossier("donnees", lieu), "osm.json"), "w") as fh:
        json.dump(elems, fh)
        fh.write("\n")
    print("%d objets OSM." % len(elems))


def appliquer_modifications(index, conf):
    """Applique en mémoire les [[adresses.modifier]] (renommage de rues,
    etc.), pour que les vérifications en tiennent compte."""
    for m in conf.get("modifier", []):
        objets = {"node": index.noeuds, "way": index.chemins, "relation": index.relations}[m["type"]]
        if m["id"] in objets:
            objets[m["id"]].setdefault("tags", {}).update(m["tags"])


def adresses_preparer(lieu, conf):
    chemin = os.path.join("donnees", lieu, "osm.json")
    if not os.path.exists(chemin):
        sys.exit("Lancez d'abord : python3 -m osmqc adresses osm lieux/%s.toml" % lieu)
    with open(chemin) as fh:
        index = osm.Index(json.load(fh))
    ca = conf.get("adresses", {})
    # Les adresses sont vérifiées comme si les rues étaient déjà renommées
    # (section rues), pour voir ce qui restera à régler.
    appliquer_modifications(index, conf.get("rues", {}))
    plan_rues, _ = rues.plan_renommage(rues.analyser(charger_adresses(lieu), index))
    rues.appliquer(index, plan_rues)
    appliquer_modifications(index, ca)
    pos = positions.Positions(ca["positions"]) if "positions" in ca else None
    if pos:
        print("Positions %s : %d points%s." % (pos.nom, len(pos.points), "".join(
            ", %d écartés (%s)" % (n, r) for r, n in sorted(pos.ecartes.items()))))
    plan = adresses.preparer(charger_adresses(lieu), index, ca, pos)
    for m in ca.get("modifier", []):
        plan.corriger(m["type"], m["id"], m["tags"], m.get("raison", ""))
    # Versions fraîches des objets à modifier, pour éviter les conflits.
    actuels = {}
    for genre in ("node", "way", "relation"):
        for e in osm.objets(genre, [i for g, i in plan.modifier if g == genre]):
            actuels[(genre, e["id"])] = e
    # Versions des nœuds à supprimer (l'extrait ne les garde que pour les
    # nœuds étiquetés).
    sans_version = {n for n in plan.supprimer_noeuds if index.noeuds[n].get("version") is None}
    if sans_version:
        if chemin_pbf():
            extrait.completer_versions(chemin_pbf(), list(index.noeuds.values()), sans_version)
        else:
            for e in osm.objets("node", sorted(sans_version)):
                index.noeuds[e["id"]].update(e)
    out = dossier("sortie", lieu)
    osmchange.ecrire_osc(osmchange.osc(plan, actuels, index), os.path.join(out, "adresses.osc"))
    complet = osmchange.geojson(plan, actuels, index)
    osmchange.ecrire_geojson(complet, os.path.join(out, "adresses.geojson"))
    osmchange.ecrire_rapport(plan, os.path.join(out, "adresses.csv"))
    rapport.ecrire_geojson_compact(rapport.geojson_allege(complet),
                             os.path.join(dossier("rapports", lieu), "adresses.geojson"))
    rapport.ecrire(os.path.join("rapports", lieu, "adresses.md"),
                   rapport.adresses(lieu, conf, plan, version_rqa(lieu)))
    print("Positions : %s" % ", ".join("%s %d" % kv for kv in Counter(l.position for l in plan.rapport).most_common()))
    print("Statuts : %s" % ", ".join("%s %d" % kv for kv in Counter(l.statut for l in plan.rapport).most_common()))
    print("Import : %d nœuds créés, %d objets modifiés, %d interpolations et %d nœuds supprimés."
          % (len(plan.creer), len(plan.modifier), len(plan.supprimer_chemins), len(plan.supprimer_noeuds)))
    print("Envoi : %s/adresses.osc. Révision : rapports/%s/adresses.md" % (out, lieu))


# Régions

def municipalites(conf):
    """Municipalités du lieu : liste explicite de [rqa], sinon toutes
    celles de la MRC indiquée dans [regions] (mrc = "80")."""
    if conf.get("rqa", {}).get("municipalites"):
        return conf["rqa"]["municipalites"]
    mrc = conf.get("regions", {}).get("mrc")
    if not mrc:
        sys.exit("Indiquez [rqa] municipalites ou [regions] mrc.")
    return sorted(regions.municipalites_mrc(chemin_sda(), mrc))


def regions_trouver(lieu, conf):
    sda = chemin_sda()
    mrc = conf["regions"].get("mrc")
    noms = regions.municipalites_mrc(sda, mrc) if mrc else {
        c: v[0] for c, v in regions.sda(sda, municipalites(conf)).items()}
    contexte = regions.nom_mrc(sda, mrc) if mrc else ""
    pbf = chemin_pbf()
    connues = extrait.limites_admin(pbf) if pbf else None
    print("[regions.osm]")
    for code, nom in sorted(noms.items()):
        if connues is not None:
            r = connues.get(code, (None,))[0]
        else:
            r = regions.trouver_relation(code, nom, contexte)
        if r:
            print('"%s" = %d   # %s' % (code, r, nom))
        else:
            print("  # \"%s\" : %s, absente d'OSM (ou sans ref:qc)" % (code, nom))
    print("}")


def regions_comparer(lieu, conf, preparer=False):
    cr = conf["regions"]
    pbf = chemin_pbf()
    if pbf:
        extrait.verifier_fraicheur(pbf)
    ids = [int(r) for r in cr["osm"].values()] + ([int(cr["exterieur"])] if cr.get("exterieur") else [])
    # Toutes les relations en un seul passage dans l'extrait.
    commun = osm.Index(extrait.relations(pbf, ids)) if pbf else None
    rels = {code: regions.Relation(int(r), pbf, commun) for code, r in cr["osm"].items()}
    officiel = regions.sda(chemin_sda(), list(rels))
    for code, r in sorted(rels.items()):
        print("OSM %s (relation %d) : %d anneaux; chemins : %s" % (
            r.tags.get("name"), r.id, len(r.anneaux),
            ", ".join("%s %d" % kv for kv in r.composition.most_common())))
    polys = {c: v[2] for c, v in officiel.items()}
    anneaux = {c: r.anneaux for c, r in rels.items()}
    compte, ecarts = regions.comparer(charger_adresses(lieu), polys, anneaux)
    for src in ("MRNF", "OSM"):
        print("%s : %d adresses dans la bonne municipalité, %d non" % (
            src, compte[(src, True)], compte[(src, False)]))
    plan = supp = None
    # Lien de chaque relation avec son nœud de lieu (règle 8).
    liens = {c: regions.lien_lieu(r.rel, r.index) for c, r in rels.items()}
    for c, (statut, detail) in sorted(liens.items()):
        if statut != "lié":
            print("Lien avec le nœud de lieu, %s : %s (%s)" % (rels[c].tags.get("name"), statut, detail))
    if preparer:
        ext = regions.Relation(int(cr["exterieur"]), pbf, commun) if cr.get("exterieur") else None
        plan = regions.preparer(polys, rels, ext)
        plan["liens"] = liens
        index = commun or osm.Index([e for r in rels.values() for e in r.index.tous()])
        supp = regions.supprimables(plan["retires"], index, [r.id for r in rels.values()], pbf)
        # Chemins protégés (note, fixme, description, disputed*) : jamais
        # supprimés; leur note passe au chemin neuf le plus proche.
        proteges = [w for w in plan["retires"] if regions.protege(index.chemins[w].get("tags", {}))]
        plan["proteges"] = regions.reporter_notes(proteges, index, plan)
        actuelles = {c: osm.objets("relation", [r.id])[0] for c, r in rels.items()}
        apres, _ = regions.comparer(charger_adresses(lieu), polys, regions.anneaux_proposes(plan, ext))
        plan["verification"] = apres
        print("Limites proposées : %d adresses dans la bonne municipalité, %d non" % (
            apres[("OSM", True)], apres[("OSM", False)]))
        # Routes qui traversent les limites : coupures à ajouter ou à déplacer.
        nouvelles = regions.lignes_limites(plan, ext)
        anciennes = [a for r in rels.values() for a in r.anneaux]
        idx_routes = routes_autour(lieu, nouvelles + anciennes)
        plan["coupures"] = regions.coupures(idx_routes, nouvelles, anciennes)
        print("Coupures de routes : %s" % ", ".join(
            "%s %d" % kv for kv in Counter(c[0] for c in plan["coupures"]).most_common()))
        plan["decoupe"] = couper_routes(plan, idx_routes, pbf)
        out = dossier("sortie", lieu)
        osmchange.ecrire_osc(osmchange.osc_regions(plan, actuelles, supp[0], supp[1], index,
                                                   str(cr.get("admin_level", "8"))),
                             os.path.join(out, "regions.osc"))
        for ligne in plan["rapport"]:
            print("  " + ligne)
        print("Remplacement : %d nœuds et %d chemins créés, %d relations modifiées, "
              "%d chemins retirés dont %d supprimés; %d chemins protégés; %d routes coupées." % (
                  len(plan["noeuds"]), len(plan["chemins"]), len(plan["membres"]),
                  len(plan["retires"]), len(supp[0]), len(plan["proteges"]),
                  len(plan["decoupe"]["modifies"])))
        print("Envoi : %s/regions.osc" % out)
    noms = {c: v[0] for c, v in officiel.items()}
    rapport.ecrire_geojson_compact(regions.geojson(polys, anneaux, ecarts, noms,
                                             plan.get("coupures") if plan else None),
                             os.path.join(dossier("rapports", lieu), "regions.geojson"))
    rapport.ecrire(os.path.join("rapports", lieu, "regions.md"),
                   rapport.regions(lieu, conf, officiel, rels, compte, ecarts, plan, supp))
    print("Révision : rapports/%s/regions.md" % lieu)


def couper_routes(plan, idx_routes, pbf):
    """Coupe les routes aux limites proposées, à partir de leur version
    actuelle dans OSM. Une route modifiée depuis l'extrait est laissée de
    côté et signalée."""
    wids = sorted({c[5] for c in plan["coupures"]
                   if c[0] in ("coupure à ajouter", "coupure à déplacer")})
    if not wids:
        return {"noeuds": {}, "chemins": {}, "modifies": {}, "relations": {}, "rapport": [],
                "actuels": {}, "rels_actuelles": {}}
    actuels = {e["id"]: e for e in osm.objets("way", wids)}
    ignores = []
    for w in wids:
        a = actuels.get(w)
        if a is None or a["nodes"] != idx_routes.chemins[w]["nodes"]:
            ignores.append(w)
            actuels.pop(w, None)
    if pbf:
        rels_ids = sorted({r for rs in extrait.usages(pbf, [], list(actuels))[2].values() for r in rs})
    else:
        rels_ids = sorted({r for w in actuels for r in regions.relations_du_chemin(w)})
    rels_actuelles = {e["id"]: e for e in osm.objets("relation", rels_ids)}
    for w, e in actuels.items():
        idx_routes.chemins[w] = e
    prochain_noeud = min([-1] + list(plan["noeuds"].values())) - 1
    prochain_chemin = min([-1] + [w for w, _, _ in plan["chemins"]]) - 1
    d = regions.decouper(idx_routes, plan["coupures"], rels_actuelles, prochain_noeud, prochain_chemin)
    d["rapport"] += ["way %d laissé de côté : modifié depuis l'extrait" % w for w in ignores]
    d["actuels"] = actuels
    d["rels_actuelles"] = rels_actuelles
    return d


def routes_autour(lieu, lignes):
    """Données OSM le long des limites (pour les routes qui les
    traversent), gardées dans donnees/LIEU/osm_limites.json."""
    chemin = os.path.join(dossier("donnees", lieu), "osm_limites.json")
    if not os.path.exists(chemin):
        pts = []
        for l in lignes:
            pas = max(1, len(l) // 200)
            pts += l[::pas] + l[-1:]
        elems = lire_zone(lieu, pts, cles_noeuds=("highway",), cles_chemins=("highway",),
                          marge=0.002)
        with open(chemin, "w") as fh:
            json.dump(elems, fh)
            fh.write("\n")
    with open(chemin) as fh:
        return osm.Index(json.load(fh))


# Rues

def rues_preparer(lieu, conf):
    chemin = os.path.join("donnees", lieu, "osm.json")
    if not os.path.exists(chemin):
        sys.exit("Lancez d'abord : python3 -m osmqc adresses osm lieux/%s.toml" % lieu)
    with open(chemin) as fh:
        index = osm.Index(json.load(fh))
    cr = conf.get("rues", {})
    # Les renommages explicites comptent comme déjà faits pour l'analyse.
    appliquer_modifications(index, cr)
    liste = rues.analyser(charger_adresses(lieu), index)
    # Une rue à renommer peut se prolonger hors de la zone lue (loin des
    # adresses) : on va chercher tous ses segments dans l'extrait, puis on
    # refait l'analyse. Seuls les segments reliés sont renommés.
    a_suivre = {n for r in liste if r.statut == "à renommer" for n in r.noms_osm if n != r.officiel}
    if a_suivre and chemin_pbf():
        for e in extrait.chemins_nommes(chemin_pbf(), a_suivre):
            dico = index.chemins if e["type"] == "way" else index.noeuds
            dico.setdefault(e["id"], e)
        appliquer_modifications(index, cr)
        liste = rues.analyser(charger_adresses(lieu), index)
    plan, conflits = rues.plan_renommage(liste)
    noms = dict(plan)
    raisons = {w: "nom officiel (RQA) : %s" % n for w, n in plan.items()}
    for m in cr.get("modifier", []):
        if m["type"] == "way" and "name" in m["tags"]:
            noms[m["id"]] = m["tags"]["name"]
            raisons[m["id"]] = m.get("raison", "")
    extra = {m["id"]: m["tags"] for m in cr.get("modifier", []) if m["type"] == "way"}
    actuels = {e["id"]: e for e in osm.objets("way", sorted(noms))}
    import xml.etree.ElementTree as ET_
    racine = ET_.Element("osmChange", version="0.6", generator="osmqc")
    modif = ET_.SubElement(racine, "modify")
    changes = []
    for w in sorted(noms):
        e = actuels[w]
        tags = rues.etiquettes_renommage(e.get("tags", {}), noms[w], extra.get(w))
        if all(e.get("tags", {}).get(k) == v for k, v in tags.items()):
            continue
        changes.append((w, e.get("tags", {}).get("name", ""), noms[w], raisons[w]))
        modif.append(osmchange.element_xml(e, tags))
    ET_.indent(racine)
    out = dossier("sortie", lieu)
    osmchange.ecrire_osc(racine, os.path.join(out, "rues.osc"))
    rapport.ecrire(os.path.join(dossier("rapports", lieu), "rues.md"),
                   rapport.rues(lieu, conf, liste, changes, conflits))
    rapport.ecrire_geojson_compact(rapport.rues_geojson(liste, changes, index),
                             os.path.join("rapports", lieu, "rues.geojson"))
    print("Rues : %s" % ", ".join("%s %d" % kv for kv in Counter(r.statut for r in liste).most_common()))
    print("Renommage : %d chemins%s." % (len(changes), "; %d conflits" % len(conflits) if conflits else ""))
    print("Envoi : %s/rues.osc. Révision : rapports/%s/rues.md" % (out, lieu))


# Envoi

def envoyer(lieu, conf, section, args):
    mode = "reel" if "--reel" in args else "test" if "--test" in args else None
    if not mode:
        sys.exit("Ajoutez --test (serveur de test) ou --reel (OpenStreetMap).")
    tags = envoi.etiquettes(conf[section]["groupe"], mode, section)
    osc = ET.parse(os.path.join("sortie", lieu, section + ".osc")).getroot()
    envoi.envoyer(osc, tags, mode)


def main():
    args = sys.argv[1:]
    if len(args) < 3:
        print("\n".join(l[2:] for l in open(__file__).read().split("\n\n")[0].splitlines()))
        sys.exit(1)
    section, cmd, chemin = args[:3]
    lieu, conf = lire_lieu(chemin)
    conf["_source_osm"] = source_osm(lieu)
    actions = {
        ("adresses", "extraire"): lambda: adresses_extraire(lieu, conf),
        ("adresses", "osm"): lambda: adresses_osm(lieu, conf),
        ("adresses", "preparer"): lambda: adresses_preparer(lieu, conf),
        ("adresses", "envoyer"): lambda: envoyer(lieu, conf, "adresses", args[3:]),
        ("regions", "trouver"): lambda: regions_trouver(lieu, conf),
        ("regions", "comparer"): lambda: regions_comparer(lieu, conf),
        ("regions", "preparer"): lambda: regions_comparer(lieu, conf, preparer=True),
        ("regions", "envoyer"): lambda: envoyer(lieu, conf, "regions", args[3:]),
        ("rues", "preparer"): lambda: rues_preparer(lieu, conf),
        ("rues", "envoyer"): lambda: envoyer(lieu, conf, "rues", args[3:]),
    }
    if (section, cmd) not in actions:
        sys.exit("Commande inconnue : %s %s" % (section, cmd))
    actions[(section, cmd)]()


main()
