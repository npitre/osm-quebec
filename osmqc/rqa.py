# Lecture du Référentiel québécois des adresses (RQA) du MRNF.
#
# Source : fichier complet RQA_CSV.zip (un seul RQA.csv d'environ
# 3 Go une fois décompressé), lu en continu sans être décompressé sur
# disque. Licence CC BY 4.0, avec permission explicite du MRNF pour
# OpenStreetMap :
# https://wiki.openstreetmap.org/wiki/FR:Minist%C3%A8re_des_Ressources_naturelles_et_des_For%C3%AAts

import csv
import io
import re
import zipfile
from dataclasses import dataclass

URL = ("https://diffusion.mern.gouv.qc.ca/diffusion/RGQ/Vectoriel/Theme/Local/"
       "RQA/CSV/RQA_CSV.zip")


@dataclass
class Adresse:
    ident: str          # identifiant_unique_adresse
    municipalite: str   # code_municipalite (ex. 01023)
    nom_municipalite: str
    odonyme: str        # seqodo : identifiant de la rue
    rue: str            # nom de rue tel qu'il doit paraître dans OSM
    numero: str         # numéro municipal, sans suffixe
    suffixe: str
    unite: str
    code_postal: str    # « G4T 3M1 »
    lon: float
    lat: float
    qualite: str        # qualite_positionnement_geometrique
    lot: str
    matricule: str
    date_creation: str
    fin: str            # date_fin : adresse qui n'existe plus
    categorie: str = ""  # catégorie d'utilisation du rôle (RESI, VILL, COMM...)

    @property
    def point(self):
        return (self.lon, self.lat)

    @property
    def principale(self):
        """Adresse sans suffixe ni logement."""
        return not self.suffixe and not self.unite

    @property
    def logement(self):
        """Numéro de logement : l'unité (2-1701), ou un suffixe en
        chiffres (329 1)."""
        if self.unite:
            return self.unite
        return self.suffixe if self.suffixe.isdigit() else ""


def nom_rue(r):
    """Nom de rue pour OSM : l'odonyme recomposé du RQA, dans l'ordre
    usuel (« 4e Rang Sud », « Route 321 Sud »), sans le discriminant des
    municipalités fusionnées (« Chemin du Gros-Cap » et non « Chemin du
    Gros-Cap (L'Étang-du-Nord) »)."""
    nom = (r.get("odonyme_recompose_normal") or "").strip()
    disc = (r.get("discriminant_odonyme") or "").strip()
    if disc and nom.endswith("(%s)" % disc):
        nom = nom[:-len(disc) - 2].strip()
    if nom:
        return developper(nom)
    # Sans forme recomposée : générique, particule, spécifique, point cardinal.
    nom = r["generique_odonyme"]
    if r["particule_odonyme"]:
        nom += " " + r["particule_odonyme"]
    sep = "" if nom.endswith("'") else " "
    nom += sep + r["specifique_odonyme"]
    if r["point_cardinal_odonyme"]:
        nom += " " + r["point_cardinal_odonyme"]
    return developper(nom.strip())


ABREVIATIONS = [(r"(?<!\w)St[-.] ?(?=\w)", "Saint-"), (r"(?<!\w)Ste[-.] ?(?=\w)", "Sainte-")]


def developper(nom):
    """Abréviations développées, selon la règle d'OSM : « Rue St-Julien »
    devient « Rue Saint-Julien »."""
    for motif, forme in ABREVIATIONS:
        nom = re.sub(motif, forme, nom)
    return nom


def adresse(r):
    cp = r["code_postal"]
    return Adresse(
        ident=r["identifiant_unique_adresse"],
        municipalite=r["code_municipalite"],
        nom_municipalite=r["nom_municipalite"],
        odonyme=r["seqodo"],
        rue=nom_rue(r),
        numero=r["numero_municipal"],
        suffixe=r["numero_municipal_suffixe"],
        unite=r["numero_unite"],
        code_postal=cp[:3] + " " + cp[3:] if len(cp) == 6 else cp,
        lon=float(r["longitude"]),
        lat=float(r["latitude"]),
        qualite=r["qualite_positionnement_geometrique"],
        lot=r["numero_lot"],
        matricule=r["matricule_unite_evaluation"],
        date_creation=r["date_creation"],
        fin=r["date_fin"],
        categorie=r.get("categorie", ""),
    )


def lire_zip(chemin, municipalites, odonymes=None):
    """Lit les lignes du RQA complet pour les municipalités données
    (codes géographiques) et, au besoin, seulement certaines rues
    (seqodo). Renvoie la liste des lignes brutes (dict)."""
    municipalites = set(municipalites)
    odonymes = set(odonymes or [])
    with zipfile.ZipFile(chemin) as z:
        with z.open("RQA.csv") as brut:
            texte = io.TextIOWrapper(brut, encoding="utf-8-sig", newline="")
            lignes = []
            for r in csv.DictReader(texte):
                if r["code_municipalite"] not in municipalites:
                    continue
                if odonymes and r["seqodo"] not in odonymes:
                    continue
                lignes.append(r)
    return lignes


def ecrire_extrait(lignes, chemin):
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lignes[0].keys()))
        w.writeheader()
        w.writerows(lignes)


def lire_extrait(chemin):
    with open(chemin, newline="", encoding="utf-8") as fh:
        return [adresse(r) for r in csv.DictReader(fh)]
