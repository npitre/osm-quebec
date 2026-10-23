# Chaîne des bouchées : prépare les bouchées du Québec méridional
# (lieux/quebec/, voir outils/bouchees.py) l'une après l'autre, chacune
# sur l'extrait où les précédentes ont été appliquées comme si OSM les
# avait acceptées, et vérifie chacune :
#   - le fichier d'envoi tient dans un groupe de modifications (10 000
#     objets au plus);
#   - après l'envoi simulé, toutes les relations touchées sont des
#     anneaux fermés, et aucun chemin de limite créé n'est orphelin;
#   - relancer la préparation sur l'extrait ainsi modifié ne produit
#     plus rien.
# Tout se fait hors ligne, dans un dossier de travail (sortie/chaine/ par
# défaut) : sa copie de l'extrait, les fichiers d'envoi de chaque
# bouchée et leur rapport de révision (envois/), les journaux (journaux/), les rapports et le bilan
# (chaine.md, chaine.csv). Rien n'est envoyé à OSM.
#
# Usage, depuis la racine du dépôt :
#   python3 outils/chaine.py [--dossier D] [--jusqu-a N] [--sans-relance] [--continuer]
#
# La chaîne reprend où elle s'est arrêtée. Elle s'arrête à la première
# bouchée qui échoue, sauf avec --continuer : la bouchée n'est alors pas
# appliquée, et la suivante part de l'extrait d'avant.

import collections
import csv
import glob
import json
import os
import shutil
import subprocess
import sys
import time
import tomllib
import xml.etree.ElementTree as ET

DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DEPOT)

from osmqc import extrait, geo, osm, progres, rapport, rqa  # noqa: E402

LIMITE = 10000


def options(args):
    o = {"dossier": os.path.join("sortie", "chaine"), "jusqu_a": None, "relance": True, "continuer": False}
    i = 0
    while i < len(args):
        a = args[i]
        if a == "--dossier":
            o["dossier"], i = args[i + 1], i + 1
        elif a == "--jusqu-a":
            o["jusqu_a"], i = int(args[i + 1]), i + 1
        elif a == "--sans-relance":
            o["relance"] = False
        elif a == "--continuer":
            o["continuer"] = True
        else:
            sys.exit("Option inconnue : %s" % a)
        i += 1
    return o


def preparer_dossier(d):
    """Le dossier de travail : les lieux du dépôt, et une copie de
    l'extrait avec son index d'usage (voir extrait.IndexUsages)."""
    for sous in ("envois", "journaux", "donnees"):
        os.makedirs(os.path.join(d, sous), exist_ok=True)
    lien = os.path.join(d, "lieux")
    if not os.path.exists(lien):
        os.symlink(os.path.join(DEPOT, "lieux"), lien)
    pbf = os.path.join(d, "extrait.osm.pbf")
    if not os.path.exists(pbf):
        source = os.path.join(DEPOT, "donnees", "quebec-latest.osm.pbf")
        progres.etape("Copie de l'extrait du Québec")
        extrait.index_usages(source)            # calculé au besoin
        shutil.copy2(source, pbf)
        shutil.copy2(source + ".usages", pbf + ".usages")
        # L'index porte la taille et la date de l'extrait : copy2 garde la
        # date, il reste valable pour la copie.
    return pbf


def extraire_adresses(d, lieux):
    """Les adresses de toutes les bouchées, en une seule lecture du RQA
    (sinon environ 40 secondes par bouchée)."""
    manquants = [l for l in lieux if not os.path.exists(os.path.join(d, "donnees", l["nom"], "rqa.csv"))]
    if not manquants:
        return
    progres.etape("Adresses du RQA pour %d bouchées (une seule lecture)" % len(manquants))
    par_code = {c: l["nom"] for l in manquants for c in l["conf"]["rqa"]["municipalites"]}
    lignes = rqa.lire_zip(os.path.join(DEPOT, "donnees", "RQA_CSV.zip"), list(par_code))
    par_lieu = collections.defaultdict(list)
    for r in lignes:
        par_lieu[par_code[r["code_municipalite"]]].append(r)
    for l in manquants:
        sortie = os.path.join(d, "donnees", l["nom"])
        os.makedirs(sortie, exist_ok=True)
        rqa.ecrire_extrait(par_lieu[l["nom"]], os.path.join(sortie, "rqa.csv"), list(lignes[0]) if lignes else None)


def lancer(d, pbf, lieu, journal):
    """regions preparer pour un lieu, dans le dossier de travail. Renvoie
    les lignes de sa sortie."""
    env = dict(os.environ, PYTHONPATH=DEPOT, OSMQC_HORS_LIGNE="1", OSMQC_PBF=os.path.abspath(pbf),
               OSMQC_SDA=os.path.join(DEPOT, "donnees", "SDA.gpkg"),
               OSMQC_RQA=os.path.join(DEPOT, "donnees", "RQA_CSV.zip"))
    r = subprocess.run([sys.executable, "-m", "osmqc", "regions", "preparer", "lieux/quebec/%s.toml" % lieu],
                       cwd=d, env=env, capture_output=True, text=True)
    with open(journal, "a", encoding="utf-8") as fh:
        fh.write(r.stdout + r.stderr)
    if r.returncode:
        raise RuntimeError("regions preparer a échoué (voir %s)" % journal)
    return r.stdout.splitlines()


def verifier(osc, pbf_apres):
    """Anneaux des relations touchées et chemins orphelins, après l'envoi
    simulé. Renvoie (relations, incomplètes, [ouvertes], [orphelins])."""
    racine = ET.parse(osc).getroot()
    ids = [int(e.get("id")) for e in racine.iter("relation")]
    idx = osm.Index(extrait.relations(pbf_apres, ids))
    ouvertes, incompletes = [], 0
    for rid in ids:
        rel = idx.relations[rid]
        if rel["tags"].get("type") != "boundary":
            continue
        ws = [m["ref"] for m in rel["members"] if m["type"] == "way"]
        if any(w not in idx.chemins for w in ws):
            incompletes += 1            # hors de l'extrait (Ontario, Canada...)
            continue
        if geo.assembler([idx.chemins[w]["nodes"] for w in ws])[1]:
            ouvertes.append("%d %s" % (rid, rel["tags"].get("name", "")))
    crees = {int(w.get("id")) for b in racine if b.tag == "create" for w in b.iter("way")
             if not any(t.get("k") == "highway" for t in w.iter("tag"))}
    membres = {int(m.get("ref")) for r in racine.iter("relation") for m in r.iter("member")
               if m.get("type") == "way"}
    # Et les nœuds créés dont aucun chemin du fichier ne se sert.
    noeuds = {int(n.get("id")) for b in racine if b.tag == "create" for n in b.iter("node")}
    servent = {int(nd.get("ref")) for b in racine if b.tag != "delete" for nd in b.iter("nd")}
    orphelins = ["way %d" % w for w in sorted(crees - membres)]
    orphelins += ["node %d" % n for n in sorted(noeuds - servent)]
    return len(ids), incompletes, ouvertes, orphelins


def compter(osc):
    racine = ET.parse(osc).getroot()
    return sum(len(b) for b in racine)


def duree(s):
    s = int(s)
    return "%d:%02d" % (s // 60, s % 60)


def bilan(d, resultats):
    entetes = ["bouchee", "lieu", "objets", "relations", "ouvertes", "orphelins", "relance",
               "non_modifiees", "duree", "statut"]
    with open(os.path.join(d, "chaine.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=entetes)
        w.writeheader()
        for r in resultats:
            w.writerow({k: r[k] if not isinstance(r[k], list) else "; ".join(r[k]) for k in entetes})
    ok = [r for r in resultats if r["statut"] == "appliquée"]
    s = "# Chaîne des bouchées du Québec méridional\n\n"
    s += ("Chaque bouchée préparée sur l'extrait où les précédentes ont été appliquées, comme si OSM "
          "les avait acceptées (outils/chaine.py). Rien n'a été envoyé à OSM.\n\n")
    s += rapport.tableau(["Bouchées traitées", "Appliquées", "Objets", "Plus gros envoi",
                          "Relations non modifiées"],
                         [[len(resultats), len(ok), sum(r["objets"] for r in ok),
                           max((r["objets"] for r in ok), default=0),
                           sum(len(r["non_modifiees"]) for r in resultats)]])
    s += "\n## Bouchées\n\n"
    s += rapport.tableau(["N°", "Lieu", "Objets", "Relations", "Ouvertes", "Orphelins", "Relance",
                          "Non modifiées", "Durée", "Statut"],
                         [[r["bouchee"], r["lieu"], r["objets"], r["relations"], len(r["ouvertes"]),
                           len(r["orphelins"]), r["relance"], len(r["non_modifiees"]), r["duree"], r["statut"]]
                          for r in resultats])
    nm = [(r["lieu"], x) for r in resultats for x in r["non_modifiees"]]
    if nm:
        s += "\n## Relations non modifiées\n\n"
        s += rapport.tableau(["Bouchée", "Relation"], [[l, x] for l, x in nm])
    rapport.ecrire(os.path.join(d, "chaine.md"), s)


def main():
    o = options(sys.argv[1:])
    d = o["dossier"]
    pbf = preparer_dossier(d)
    lieux = []
    for f in sorted(glob.glob(os.path.join(DEPOT, "lieux", "quebec", "Q*.toml"))):
        nom = os.path.splitext(os.path.basename(f))[0]
        with open(f, "rb") as fh:
            lieux.append({"nom": nom, "numero": int(nom[1:4]), "conf": tomllib.load(fh)})
    if o["jusqu_a"]:
        lieux = [l for l in lieux if l["numero"] <= o["jusqu_a"]]
    etat_f = os.path.join(d, "etat.json")
    resultats = json.load(open(etat_f)) if os.path.exists(etat_f) else []
    faites = {r["lieu"] for r in resultats}
    a_faire = [l for l in lieux if l["nom"] not in faites]
    extraire_adresses(d, a_faire)
    for l in a_faire:
        debut = time.monotonic()
        nom = l["nom"]
        progres.etape("Bouchée %d sur %d : %s" % (l["numero"], len(lieux), l["conf"].get("nom", nom)))
        journal = os.path.join(d, "journaux", nom + ".log")
        sortie = lancer(d, pbf, nom, journal)
        # Le fichier d'envoi et son rapport de révision, gardés avant que la
        # relance ne les remplace.
        osc = os.path.join(d, "envois", nom + ".osc")
        shutil.copy(os.path.join(d, "sortie", nom, "regions.osc"), osc)
        shutil.copy(os.path.join(d, "rapports", nom, "regions.md"), os.path.join(d, "envois", nom + ".md"))
        r = {"bouchee": l["numero"], "lieu": nom, "objets": compter(osc), "relations": 0, "ouvertes": [],
             "orphelins": [], "relance": "", "duree": "", "statut": "",
             "non_modifiees": [x.strip() for x in sortie if "non modifiée" in x]}
        neuf = os.path.join(d, "extrait.neuf.osm.pbf")
        extrait.appliquer(pbf, osc, neuf)
        r["relations"], _, r["ouvertes"], r["orphelins"] = verifier(osc, neuf)
        echec = [m for m, c in (("plus de %d objets" % LIMITE, r["objets"] > LIMITE),
                                ("anneaux ouverts", r["ouvertes"]), ("orphelins", r["orphelins"])) if c]
        if not echec and o["relance"]:
            journal_r = os.path.join(d, "journaux", nom + ".relance.log")
            lancer(d, neuf, nom, journal_r)
            reste = compter(os.path.join(d, "sortie", nom, "regions.osc"))
            r["relance"] = "vide" if not reste else "%d objets" % reste
            if reste:
                echec.append("relance non vide")
        if echec:
            # L'extrait de la bouchée qui échoue est gardé pour l'examen
            # (extrait.echec.osm.pbf); la suivante part de celui d'avant.
            r["statut"] = "échec : " + ", ".join(echec)
            os.replace(neuf, os.path.join(d, "extrait.echec.osm.pbf"))
            if os.path.exists(neuf + ".usages"):
                os.replace(neuf + ".usages", os.path.join(d, "extrait.echec.osm.pbf.usages"))
        else:
            r["statut"] = "appliquée"
            os.replace(neuf, pbf)
            os.replace(neuf + ".usages", pbf + ".usages")
        r["duree"] = duree(time.monotonic() - debut)
        progres.etape("  %s objets, %d relations, %d non modifiées, relance %s, %s : %s" % (
            r["objets"], r["relations"], len(r["non_modifiees"]), r["relance"] or "non faite", r["duree"],
            r["statut"]))
        resultats.append(r)
        with open(etat_f + ".tmp", "w") as fh:
            json.dump(resultats, fh, ensure_ascii=False, indent=1)
            fh.write("\n")
        os.replace(etat_f + ".tmp", etat_f)
        bilan(d, resultats)
        if echec and not o["continuer"]:
            sys.exit("Arrêt à la bouchée %d (%s). Voir %s." % (l["numero"], r["statut"], journal))
    progres.etape("Chaîne terminée : %d bouchées" % len(resultats))


if __name__ == "__main__":
    main()
