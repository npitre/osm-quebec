# Validation d'un lieu avant l'envoi de ses limites : prépare le lieu
# (versions actuelles des relations lues à l'API, sauf hors ligne),
# applique son fichier d'envoi à une copie de l'extrait comme si OSM
# l'avait accepté, et vérifie, comme la chaîne des bouchées
# (outils/chaine.py) :
#   - le fichier d'envoi tient dans un groupe de modifications;
#   - toutes les relations touchées, même hors du fichier d'envoi, sont
#     des anneaux fermés, et aucune ne garde un chemin supprimé;
#   - aucun chemin de limite ni nœud créé n'est orphelin;
#   - relancer la préparation sur l'extrait modifié ne produit plus rien.
# Rien n'est envoyé à OSM.
#
# Usage, depuis la racine du dépôt :
#   python3 outils/valider.py lieux/LIEU.toml [--dossier D]
# La copie de l'extrait et la relance vont dans D (par défaut
# sortie/validation/LIEU/); le fichier d'envoi validé reste dans
# sortie/LIEU/regions.osc.

import os
import shutil
import subprocess
import sys

DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DEPOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from chaine import LIMITE, compter, verifier  # noqa: E402

from osmqc import extrait, progres  # noqa: E402


def preparer(lieu_toml, cwd, env):
    r = subprocess.run([sys.executable, "-m", "osmqc", "regions", "preparer", lieu_toml],
                       cwd=cwd, env=env, capture_output=True, text=True)
    if r.returncode:
        sys.exit("regions preparer a échoué :\n%s%s" % (r.stdout, r.stderr[-3000:]))
    return r.stdout.splitlines()


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit("Usage : python3 outils/valider.py lieux/LIEU.toml [--dossier D]")
    lieu_toml = args[0]
    lieu = os.path.splitext(os.path.basename(lieu_toml))[0]
    d = args[args.index("--dossier") + 1] if "--dossier" in args else os.path.join("sortie", "validation", lieu)
    pbf = extrait.chemin()
    env = dict(os.environ, PYTHONPATH=DEPOT)

    progres.etape("Préparation de %s" % lieu)
    sortie = preparer(lieu_toml, DEPOT, env)
    for l in sortie:
        if l.startswith("Remplacement") or "non modifiée" in l:
            print(l)
    osc = os.path.join(DEPOT, "sortie", lieu, "regions.osc")
    objets = compter(osc)

    progres.etape("Envoi simulé sur une copie de l'extrait")
    if os.path.exists(d):
        shutil.rmtree(d)
    os.makedirs(d)
    apres = os.path.join(d, "apres.osm.pbf")
    extrait.appliquer(pbf, osc, apres)
    relations, incompletes, ouvertes, orphelins = verifier(osc, pbf, apres)

    progres.etape("Relance hors ligne sur l'extrait modifié")
    copie = os.path.join(d, "copie")
    os.makedirs(os.path.join(copie, os.path.dirname(lieu_toml)), exist_ok=True)
    shutil.copy(lieu_toml, os.path.join(copie, lieu_toml))
    source = os.path.join(DEPOT, "donnees", lieu)
    if os.path.isdir(source):
        shutil.copytree(source, os.path.join(copie, "donnees", lieu),
                        ignore=shutil.ignore_patterns("osm_limites.json*"))
    env_r = dict(env, OSMQC_HORS_LIGNE="1", OSMQC_PBF=os.path.abspath(apres),
                 OSMQC_SDA=os.path.abspath(os.environ.get("OSMQC_SDA", os.path.join(DEPOT, "donnees", "SDA.gpkg"))),
                 OSMQC_RQA=os.path.abspath(os.environ.get("OSMQC_RQA", os.path.join(DEPOT, "donnees", "RQA_CSV.zip"))))
    for l in preparer(lieu_toml, copie, env_r):
        if "non modifiée" in l:
            print("relance :", l)
    reste = compter(os.path.join(copie, "sortie", lieu, "regions.osc"))

    print("Fichier d'envoi : %s, %d objets (au plus %d)" % (osc, objets, LIMITE))
    print("Relations vérifiées : %d, dont %d incomplètes dans l'extrait; ouvertes : %s"
          % (relations, incompletes, ", ".join(ouvertes) or "aucune"))
    print("Orphelins : %s" % (", ".join(orphelins) or "aucun"))
    print("Relance : %s" % ("vide" if not reste else "%d objets" % reste))
    ok = objets <= LIMITE and not ouvertes and not orphelins and not reste
    print("Validation : %s" % ("réussie" if ok else "ÉCHEC"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
