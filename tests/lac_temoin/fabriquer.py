# Lac-Témoin : région fictive de test, fabriquée de toutes pièces pour
# essayer le pipeline de bout en bout (tests/test_lac_temoin.py).
#
# Trois municipalités, dans la MRC du Témoin (99) : Lac-Témoin (99001)
# au sud-ouest, Sainte-Vérification (99002) au sud-est, et
# Rivière-Contrôle (99003) au nord. Les coordonnées sont en millièmes de
# degré autour de 72° O, 47° N (un millième vaut environ 76 m d'est en
# ouest et 111 m du sud au nord).
#
#        0          19 20                 40
#   30   +---------------------------------+
#        |        Rivière-Contrôle         |
#   20   +-----------+--+------------------+
#        | Lac-Témoin   |  Sainte-Vérification
#        |           |  |                  |
#    0   +-----------+--+------------------+
#
# Le premier lot (Lac-Témoin.toml) traite les deux municipalités du sud;
# Rivière-Contrôle, voisine hors du lot, est modifiée en partie. Le
# second lot (Riviere-Controle.toml) la traite ensuite.
#
# Selon le MRNF, la limite commune est à x = 20. Dans OSM, elle est à
# x = 19 et c'est une rivière; le côté est de Sainte-Vérification, lui,
# suit déjà exactement le MRNF. Chaque objet ci-dessous illustre un cas
# d'une règle du README; tests/test_lac_temoin.py vérifie le résultat.
#
# Usage : python3 fabriquer.py DOSSIER
# Écrit DOSSIER/RQA_CSV.zip, DOSSIER/SDA.gpkg, DOSSIER/lac-temoin.osm.pbf
# et DOSSIER/donnees/Lac-Temoin/portes.csv.

import csv
import io
import os
import sqlite3
import struct
import sys
import zipfile

import osmium

X0, Y0 = -72.0, 47.0
DATE_EXTRAIT = "2026-10-16T00:00:00Z"


def P(x, y):
    return (round(X0 + x / 1000, 7), round(Y0 + y / 1000, 7))


# Découpages administratifs (MRNF)

MUNICIPALITES = {
    "99001": ("Lac-Témoin", [(0, 0), (20, 0), (20, 20), (0, 20), (0, 0)]),
    # Deux sommets à moins d'un millimètre l'un de l'autre au nord : un
    # seul nœud dans OSM, qui ne garde que 7 décimales.
    "99002": ("Sainte-Vérification", [(20, 0), (40, 0), (40, 20), (30.000005, 20), (30, 20),
                                      (20, 20), (20, 0)]),
    "99003": ("Rivière-Contrôle", [(0, 20), (20, 20), (30, 20), (30.000005, 20), (40, 20),
                                   (40, 30), (0, 30), (0, 20)]),
}


def wkb_polygone(anneau):
    # Coordonnées brutes, non arrondies, comme celles du MRNF.
    pts = [(X0 + x / 1000, Y0 + y / 1000) for x, y in anneau]
    return struct.pack("<BIII", 1, 3, 1, len(pts)) + b"".join(struct.pack("<dd", *p) for p in pts)


def ecrire_sda(chemin):
    db = sqlite3.connect(chemin)
    db.execute("create table munic_s (MUS_CO_GEO text, MUS_NM_MUN text, MUS_CO_VER text, "
               "MUS_CO_MRC text, geom blob)")
    db.execute("create table mrc_s (MRS_CO_MRC text, MRS_NM_MRC text)")
    for code, (nom, anneau) in MUNICIPALITES.items():
        # En-tête GeoPackage : « GP », version 0, drapeaux (petit-boutiste,
        # sans enveloppe), SRID 4326, puis le WKB.
        geom = b"GP\x00\x01" + struct.pack("<i", 4326) + wkb_polygone(anneau)
        db.execute("insert into munic_s values (?, ?, ?, ?, ?)", (code, nom, "V2026-09", "99", geom))
    db.execute("insert into mrc_s values ('99', 'MRC du Témoin')")
    db.commit()
    db.close()


# OpenStreetMap

class Carte:
    def __init__(self):
        self.noeuds = {}        # id -> (point, étiquettes)
        self.par_point = {}
        self.chemins = []       # (id, [nœuds], étiquettes)
        self.relations = []     # (id, [(type, ref, rôle)], étiquettes)
        self.prochain = 1

    def noeud(self, x, y, tags=None, partage=True):
        """Nœud au point (x, y); sans étiquettes et si partage, le même
        nœud sert à tous les chemins qui passent par ce point."""
        p = P(x, y)
        if partage and not tags and p in self.par_point:
            return self.par_point[p]
        n = self.prochain
        self.prochain += 1
        self.noeuds[n] = (p, tags or {})
        if partage and not tags:
            self.par_point[p] = n
        return n

    def chemin(self, ident, points, tags, partage=True):
        assert ident not in {w for w, _, _ in self.chemins}, "chemin %d déjà pris" % ident
        ids = [self.noeud(x, y, partage=partage) for x, y in points]
        self.chemins.append((ident, ids, tags))
        return ids

    def ecrire(self, chemin):
        h = osmium.io.Header()
        h.set("osmosis_replication_timestamp", DATE_EXTRAIT)
        if os.path.exists(chemin):
            os.unlink(chemin)
        w = osmium.SimpleWriter(chemin, header=h)
        for n, (p, tags) in sorted(self.noeuds.items()):
            w.add_node(osmium.osm.mutable.Node(id=n, location=p, tags=tags, version=1))
        for ident, ids, tags in sorted(self.chemins, key=lambda c: c[0]):
            w.add_way(osmium.osm.mutable.Way(id=ident, nodes=ids, tags=tags, version=2))
        for ident, membres, tags in sorted(self.relations, key=lambda r: r[0]):
            w.add_relation(osmium.osm.mutable.Relation(id=ident, members=membres, tags=tags, version=3))
        w.close()


LIMITE = {"boundary": "administrative", "admin_level": "8"}
CANVEC = "NRCan-CanVec-7.0"


def carte():
    c = Carte()

    # Limites actuelles d'OSM (règles 2 et 5 des régions).
    # Ligne de limite seule, avec une bosse 333 m au sud du MRNF (y = 17,
    # de x = 1 à 5), où deux routes ont gardé une coupure.
    c.chemin(101, [(19, 20), (5, 20), (5, 17), (1, 17), (1, 20), (0, 20), (0, 0)], dict(LIMITE))
    c.chemin(102, [(0, 0), (19, 0)], {"boundary": "administrative", "admin_level": "4"})   # frontière
    c.chemin(103, [(19, 0), (19, 20)], {"waterway": "river", "name": "Rivière Témoin"})
    c.chemin(104, [(19, 0), (40, 0)], dict(LIMITE, note="Limite à vérifier sur le terrain"))
    c.chemin(105, [(40, 20), (19, 20)], dict(LIMITE))
    # Le côté est de Sainte-Vérification suit déjà exactement le MRNF
    # (tracé à la main par quelqu'un) : il est réutilisé tel quel.
    c.chemin(106, [(40, 0), (40, 20)], dict(LIMITE))
    lieu = c.noeud(8, 12, {"place": "village", "name": "Lac-Témoin"})
    c.relations.append((1001, [("w", 101, "outer"), ("w", 102, "outer"), ("w", 103, "outer"),
                               ("n", lieu, "label")],
                        {"type": "boundary", "boundary": "administrative", "admin_level": "8",
                         "name": "Lac-Témoin", "ref:qc": "99001"}))
    # Sainte-Vérification n'a pas de membre label (règle 8).
    c.relations.append((1002, [("w", 103, "outer"), ("w", 104, "outer"), ("w", 106, "outer"),
                               ("w", 105, "outer")],
                        {"type": "boundary", "boundary": "administrative", "admin_level": "8",
                         "name": "Sainte-Vérification", "ref:qc": "99002"}))

    # Rivière-Contrôle, voisine du premier lot. Son ancienne limite sud
    # double celle du lot, 67 m plus au nord (y = 20,6) : des tracés
    # parallèles, comme on en voit entre deux municipalités traitées
    # séparément.
    c.chemin(120, [(36, 20.6), (10, 20.6)], dict(LIMITE))                  # longe le lot : supprimée
    # Un ruisseau fait à la fois une partie de la limite sud et le bas de la
    # limite ouest : jamais coupé; sa partie ouest est recopiée.
    c.chemin(110, [(10, 20.6), (0, 20.6), (0, 26)], {"waterway": "stream", "name": "Ruisseau Contrôle"})
    c.chemin(121, [(0, 26), (0, 30), (40, 30)], dict(LIMITE))
    # Le côté est sert aussi à une aire protégée : coupé en deux, l'aire
    # garde ses deux morceaux.
    c.chemin(122, [(40, 30), (40, 20.6), (36, 20.6)], dict(LIMITE))
    c.chemin(123, [(36, 20.6), (36, 32), (40, 32), (40, 30)], {"boundary": "protected_area"})
    lieu_rc = c.noeud(20, 25, {"place": "hamlet", "name": "Rivière-Contrôle"})
    c.relations.append((1003, [("w", 120, "outer"), ("w", 110, "outer"), ("w", 121, "outer"),
                               ("w", 122, "outer"), ("n", lieu_rc, "label")],
                        {"type": "boundary", "boundary": "administrative", "admin_level": "8",
                         "name": "Rivière-Contrôle", "ref:qc": "99003"}))
    c.relations.append((1004, [("w", 122, "outer"), ("w", 123, "outer")],
                        {"type": "boundary", "boundary": "protected_area", "name": "Réserve du Contrôle"}))

    # Routes qui traversent les limites (règle 7 des régions).
    route = {"highway": "secondary", "name": "Route 999", "ref": "999"}
    c.chemin(300, [(5, 8), (12, 8), (19, 8)], dict(route))      # coupée sur l'ancienne limite
    c.chemin(301, [(19, 8), (26, 8), (35, 8)], dict(route))
    c.relations.append((700, [("w", 300, ""), ("w", 301, "")],
                        {"type": "route", "route": "road", "ref": "999", "network": "CA:QC"}))
    c.chemin(310, [(16, 15), (24, 15)], {"highway": "residential", "name": "Rue Principale"})

    # Rues de Lac-Témoin (règles des rues).
    # Coupé sur la bosse de l'ancienne limite : coupure à fusionner.
    c.chemin(320, [(3, 2), (3, 17)], {"highway": "residential", "name": "Chemin du Lac"})
    c.chemin(328, [(3, 17), (3, 18)], {"highway": "residential", "name": "Chemin du Lac"})
    # Coupée aussi sur la bosse, mais un sentier de motoneige ne suit que
    # le bout nord : la fusion est refusée.
    c.chemin(332, [(4.5, 15), (4.5, 17)], {"highway": "residential", "name": "Allée du Témoin"})
    c.chemin(333, [(4.5, 17), (4.5, 19)], {"highway": "residential", "name": "Allée du Témoin"})
    c.relations.append((703, [("w", 333, "")], {"type": "route", "route": "snowmobile",
                                               "name": "Sentier du Témoin"}))
    c.chemin(321, [(6, 2), (6, 18)], {"highway": "residential", "name": "Chemin de la Pointe"})
    c.chemin(322, [(6, 18), (10, 19)], {"highway": "footway", "name": "Chemin de la Pointe"})
    c.chemin(323, [(9, 2), (9, 6)], {"highway": "residential", "name": "Rue St. Jean"})
    c.chemin(324, [(12, 2), (12, 6)], {"highway": "residential", "name": "Chemin Cormier"})
    c.chemin(325, [(15, 2), (15, 6)], {"highway": "service"})
    c.chemin(326, [(9, 10), (9, 14)], {"highway": "residential", "name": "Chemin du Quai"})
    # Rues de Sainte-Vérification.
    c.chemin(330, [(30, 2), (30, 18)], {"highway": "residential", "name": "Chemin du Tour du Lac"})
    c.chemin(331, [(34, 2), (34, 18)], {"highway": "residential", "name": "Rue des Portes"})

    # Adresses déjà dans OSM (règle 5 des adresses).
    c.noeud(3.45, 5, {"addr:housenumber": "30", "addr:street": "Ch. du Lac"})
    c.noeud(3.45, 6, {"addr:housenumber": "40", "addr:street": "Chemin du Lac",
                      "addr:postcode": "J0T 1A0"})
    c.chemin(350, [(3.3, 6.9), (3.6, 6.9), (3.6, 7.1), (3.3, 7.1), (3.3, 6.9)],
             {"building": "house", "addr:housenumber": "50", "addr:street": "Chemin du Lac",
              "addr:postcode": "J0T 1A0"})

    # Interpolations CanVec (règle 7 des adresses).
    def interpolation(ident, y0, y1, ville, partage=False):
        a = c.noeud(2.8, y0, {"addr:housenumber": "1000", "addr:street": "Chemin du Lac",
                              "addr:city": ville, "source": CANVEC})
        b = c.noeud(2.8, y1, {"addr:housenumber": "1200", "addr:street": "Chemin du Lac",
                              "addr:city": ville, "source": CANVEC})
        c.chemins.append((ident, [a, b], {"addr:interpolation": "even", "source": CANVEC}))
        if partage:
            c.chemins.append((ident + 1, [b, c.noeud(2, y1)], {"highway": "footway"}))
    interpolation(400, 9, 12, "Lac-Témoin")             # supprimée
    interpolation(402, 13, 15, "Ailleurs")              # autre municipalité : gardée
    interpolation(404, 16, 17.5, "Lac-Témoin", True)    # nœud partagé : gardée

    # Bâtiments de la rue des Portes (règle 8 des adresses : entrance=*).
    c.chemin(500, [(35, 3), (36, 3), (36, 4), (35, 4), (35, 3)], {"building": "house"})
    c.chemin(501, [(35, 5), (36, 5), (36, 6), (35, 6), (35, 5)], {"building": "retail"})
    return c


# Référentiel québécois des adresses

COLONNES = ["identifiant_unique_adresse", "date_diffusion_version", "date_creation",
            "date_modification", "date_fin", "numero_municipal", "numero_municipal_suffixe",
            "numero_unite", "type_unite", "code_postal", "seqodo", "generique_odonyme",
            "particule_odonyme", "specifique_odonyme", "point_cardinal_odonyme",
            "odonyme_recompose_normal", "discriminant_odonyme", "qualite_positionnement_geometrique",
            "categorie", "nombre_unite", "numero_lot", "matricule_unite_evaluation",
            "code_municipalite", "nom_municipalite", "longitude", "latitude"]

RUES = {    # nom officiel : (seqodo, municipalité)
    "Chemin du Lac": ("1", "99001"),
    "Chemin de La Pointe": ("2", "99001"),
    "Rue St-Jean": ("3", "99001"),
    "Chemin des Érables": ("4", "99001"),
    "Allée des Bouleaux": ("5", "99001"),
    "Chemin Fantôme": ("6", "99001"),
    "Chemin de la Jetée": ("7", "99001"),
    "Route 999": ("8", None),
    "Rue Principale": ("9", None),
    "Chemin du Tour-du-Lac": ("10", "99002"),
    "Rue des Portes": ("11", "99002"),
    "Chemin du Nord": ("12", "99003"),
}
POSTAL = {"99001": "J0T1A0", "99002": "J0T1B0", "99003": "J0T1C0"}


def matricule(n):
    return "%018d" % n


ADRESSES = [
    # (rue, numéro, x, y, autres champs)
    ("Chemin du Lac", "10", 3.4, 3, {}),
    ("Chemin du Lac", "20", 3.4, 4, {}),
    ("Chemin du Lac", "30", 3.4, 5, {}),                    # doublon à corriger
    ("Chemin du Lac", "40", 3.4, 6, {}),                    # doublon inchangé
    ("Chemin du Lac", "50", 3.45, 7, {}),                   # dans un bâtiment numéroté
    ("Chemin du Lac", "60", 3.4, 8, {"date_fin": "20240101"}),
    ("Chemin du Lac", "70", 3.4, 9, {}),                    # exclu dans le fichier du lieu
    ("Chemin du Lac", "110", 3.4, 10, {}),
    ("Chemin du Lac", "250", 3.4, 11, {"nombre_unite": "2", "matricule_unite_evaluation": matricule(250)}),
    ("Chemin du Lac", "250", 3.4, 11, {"numero_unite": "1", "matricule_unite_evaluation": matricule(251)}),
    ("Chemin du Lac", "250", 3.4, 11, {"numero_unite": "2", "matricule_unite_evaluation": matricule(252)}),
    ("Chemin du Lac", "260", 3.4, 12, {"nombre_unite": "1", "matricule_unite_evaluation": matricule(260)}),
    ("Chemin du Lac", "260", 3.4, 12, {"numero_unite": "9999", "date_creation": "20211211201507"}),
    ("Chemin du Lac", "270", 3.4, 13, {}),
    ("Chemin du Lac", "270", 3.4, 13, {"numero_municipal_suffixe": "A"}),
    ("Chemin du Lac", "280", 3.4, 14, {}),
    ("Chemin du Lac", "280", 4.4, 14, {"numero_municipal_suffixe": "B"}),   # à 76 m : distincte
    ("Chemin du Lac", "290", 3.4, 15, {"numero_unite": "1"}),                # sans adresse principale
    ("Chemin du Lac", "300", 3.4, 16, {"numero_municipal_suffixe": "A"}),   # suffixes sans
    ("Chemin du Lac", "300", 3.4, 16, {"numero_municipal_suffixe": "B"}),   # numéro de base
    ("Chemin de La Pointe", "10", 6.4, 3, {}),
    ("Chemin de La Pointe", "20", 6.4, 4, {}),
    ("Rue St-Jean", "5", 9.4, 3, {}),
    ("Rue St-Jean", "7", 9.4, 4, {}),
    ("Chemin des Érables", "1", 12.4, 3, {}),
    ("Chemin des Érables", "3", 12.4, 4, {}),
    ("Allée des Bouleaux", "2", 15.4, 3, {}),
    ("Allée des Bouleaux", "4", 15.4, 4, {}),
    ("Chemin Fantôme", "1", 16, 18.5, {}),
    ("Chemin de la Jetée", "1", 9.4, 11, {}),
    ("Chemin de la Jetée", "3", 9.4, 13, {}),
    ("Route 999", "500", 10, 8.3, {"code_municipalite": "99001"}),
    ("Route 999", "600", 30, 8.3, {"code_municipalite": "99002"}),
    ("Rue Principale", "15", 19.5, 15.3, {"code_municipalite": "99001"}),   # entre les deux limites
    ("Rue Principale", "25", 22, 15.3, {"code_municipalite": "99002"}),
    ("Chemin du Tour-du-Lac", "100", 30.4, 3, {}),
    ("Chemin du Tour-du-Lac", "200", 30.4, 4, {}),
    ("Rue des Portes", "10", 34.4, 3.5, {"matricule_unite_evaluation": matricule(10)}),
    ("Rue des Portes", "20", 34.4, 5.5, {"categorie": "COMM", "matricule_unite_evaluation": matricule(20)}),
    ("Rue des Portes", "30", 34.4, 7, {"matricule_unite_evaluation": matricule(30)}),
    ("Rue des Portes", "40", 34.4, 9, {"matricule_unite_evaluation": matricule(40)}),
    ("Rue des Portes", "50", 34.4, 11, {"matricule_unite_evaluation": matricule(50)}),
    ("Rue des Portes", "52", 34.4, 12, {"matricule_unite_evaluation": matricule(50)}),
    ("Rue des Portes", "60", 34.4, 13, {}),
    ("Chemin du Nord", "1", 20, 25.3, {}),
]

# Portes de la Chaire Mobilité (CSV du rôle corrigé), par matricule :
# (x, y, sur la porte, approximatif).
PORTES = {
    10: (35, 3.5, "true", "false"),       # sur le contour du bâtiment 500
    20: (35, 5.5, "true", "false"),       # sur le contour du bâtiment 501 (commerce)
    30: (34.9, 10, "true", "false"),      # vérifiée, à plus de 300 m du point du RQA
    40: (34.6, 9, "true", "true"),        # approximative : écartée
    50: (34.6, 11.5, "true", "false"),    # deux numéros pour la même unité : ignorée
}


def lignes_rqa():
    res = []
    for i, (rue, num, x, y, autres) in enumerate(ADRESSES, 1):
        seqodo, mun = RUES[rue]
        mun = autres.get("code_municipalite", mun)
        lon, lat = P(x, y)
        r = {k: "" for k in COLONNES}
        r.update({
            "identifiant_unique_adresse": "%032x" % (0x7e0000 + i),
            "date_diffusion_version": "20261001",
            "date_creation": "20160212120103",
            "numero_municipal": num,
            "code_postal": POSTAL[mun],
            "seqodo": seqodo,
            "odonyme_recompose_normal": rue,
            "qualite_positionnement_geometrique": "Bâtiment",
            "categorie": "RESI",
            "nombre_unite": "1",
            "numero_lot": str(1000000 + i) if autres.get("matricule_unite_evaluation") else "",
            "code_municipalite": mun,
            "nom_municipalite": MUNICIPALITES[mun][0],
            "longitude": repr(lon),
            "latitude": repr(lat),
        })
        r.update(autres)
        if r["numero_unite"] and not autres.get("matricule_unite_evaluation"):
            r["numero_lot"] = ""
        res.append(r)
    return res


def ecrire_rqa(chemin):
    texte = io.StringIO()
    w = csv.DictWriter(texte, fieldnames=COLONNES)
    w.writeheader()
    w.writerows(lignes_rqa())
    with zipfile.ZipFile(chemin, "w") as z:
        z.writestr("RQA.csv", texte.getvalue())


def ecrire_portes(chemin):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["id_provinc", "geog", "geog_changed_entrance_aligned", "geog_approximate",
                    "is_ignored"])
        for m, (x, y, porte, approx) in sorted(PORTES.items()):
            mun = "99002"
            w.writerow([mun + matricule(m), "SRID=4326;POINT(%r %r)" % P(x, y), porte, approx, "false"])


def fabriquer(dossier):
    os.makedirs(dossier, exist_ok=True)
    ecrire_sda(os.path.join(dossier, "SDA.gpkg"))
    ecrire_rqa(os.path.join(dossier, "RQA_CSV.zip"))
    carte().ecrire(os.path.join(dossier, "lac-temoin.osm.pbf"))
    ecrire_portes(os.path.join(dossier, "donnees", "Lac-Temoin", "portes.csv"))


if __name__ == "__main__":
    fabriquer(sys.argv[1])
