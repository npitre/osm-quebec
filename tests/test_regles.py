import os
import unittest

from osmqc import adresses, geo, regions, rqa

# Pas d'indicateur de progression pendant les tests (osmqc/progres.py).
os.environ["OSMQC_SANS_PROGRES"] = "1"


def adr(numero, suffixe="", unite="", lon=-61.87, lat=47.36, rue="Chemin du Gros-Cap"):
    return rqa.Adresse(ident="x", municipalite="01023", nom_municipalite="", odonyme="1",
                       rue=rue, numero=numero, suffixe=suffixe, unite=unite,
                       code_postal="G4T 3M1", lon=lon, lat=lat, qualite="Bâtiment",
                       lot="", matricule="", date_creation="", fin="")


class Geo(unittest.TestCase):
    def test_distance(self):
        # Un centième de degré de latitude : environ 1,1 km.
        self.assertAlmostEqual(geo.distance((-61.87, 47.36), (-61.87, 47.37)), 1112, delta=2)

    def test_dedans_avec_trou(self):
        ext = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        trou = [(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]
        self.assertTrue(geo.dedans((1, 1), [ext, trou]))
        self.assertFalse(geo.dedans((5, 5), [ext, trou]))
        self.assertFalse(geo.dedans((11, 5), [ext, trou]))

    def test_assembler(self):
        anneaux, ouverts = geo.assembler([[1, 2, 3], [5, 4, 3], [5, 1]])
        self.assertEqual(ouverts, 0)
        self.assertEqual(len(anneaux), 1)
        self.assertEqual(anneaux[0][0], anneaux[0][-1])


class Noms(unittest.TestCase):
    def test_nom_rue_recompose(self):
        r = {"odonyme_recompose_normal": "Chemin du Gros-Cap (L'Étang-du-Nord)",
             "discriminant_odonyme": "L'Étang-du-Nord"}
        self.assertEqual(rqa.nom_rue(r), "Chemin du Gros-Cap")
        r = {"odonyme_recompose_normal": "4e Rang Sud", "discriminant_odonyme": ""}
        self.assertEqual(rqa.nom_rue(r), "4e Rang Sud")

    def test_nom_rue(self):
        base = {"odonyme_recompose_normal": "", "generique_odonyme": "Chemin", "particule_odonyme": "du",
                "specifique_odonyme": "Gros-Cap", "point_cardinal_odonyme": ""}
        self.assertEqual(rqa.nom_rue(base), "Chemin du Gros-Cap")
        base.update(generique_odonyme="Rue", particule_odonyme="d'", specifique_odonyme="Amiens")
        self.assertEqual(rqa.nom_rue(base), "Rue d'Amiens")
        base.update(particule_odonyme="", specifique_odonyme="Sherbrooke", point_cardinal_odonyme="Est")
        self.assertEqual(rqa.nom_rue(base), "Rue Sherbrooke Est")

    def test_cle_nom(self):
        self.assertEqual(adresses.cle_nom("Chemin du Gros Cap"), adresses.cle_nom("Chemin du Gros-Cap"))
        self.assertEqual(adresses.cle_nom("Chemin Noël"), adresses.cle_nom("Chemin Noel"))


class Regroupement(unittest.TestCase):
    def test_logements_fusionnes(self):
        g = adresses.regrouper([adr("1701"), adr("1701", unite="2")])
        self.assertEqual(list(g), [("01023", "1", "1701")])
        base, autres = g[("01023", "1", "1701")]
        self.assertTrue(base.principale)
        self.assertEqual(len(autres), 1)

    def test_suffixe_au_meme_point(self):
        g = adresses.regrouper([adr("120"), adr("120", suffixe="A")])
        self.assertEqual(list(g), [("01023", "1", "120")])

    def test_suffixe_ailleurs(self):
        g = adresses.regrouper([adr("120"), adr("120", suffixe="A", lat=47.3610)])
        self.assertIn(("01023", "1", "120A"), g)

    def test_sans_adresse_principale(self):
        g = adresses.regrouper([adr("329", unite="1"), adr("329", unite="2")])
        base, autres = g[("01023", "1", "329")]
        self.assertFalse(base.principale)
        self.assertEqual(len(autres), 1)


class Doublons(unittest.TestCase):
    def test_noeud_proche(self):
        e = {"type": "node", "id": 1}
        deja = {"547": [(e, [(-61.8791, 47.3546)])]}
        self.assertIs(adresses.correspondance(deja, "547", (-61.8791, 47.35463)), e)
        self.assertIsNone(adresses.correspondance(deja, "547", (-61.8791, 47.3560)))
        self.assertIsNone(adresses.correspondance(deja, "549", (-61.8791, 47.3546)))

    def test_contour(self):
        e = {"type": "way", "id": 2}
        carre = [(0, 0), (0.01, 0), (0.01, 0.01), (0, 0.01), (0, 0)]
        deja = {"1040": [(e, carre)]}
        self.assertIs(adresses.correspondance(deja, "1040", (0.005, 0.005)), e)


class Arcs(unittest.TestCase):
    def test_trou_partage(self):
        # Une municipalité A avec un trou occupé par la municipalité B :
        # le contour de B est un seul arc, intérieur pour A, extérieur pour B.
        ext = [(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)]
        b = [(4, 4), (6, 4), (6, 6), (4, 6), (4, 4)]
        res = regions.arcs({"A": [[ext, b[::-1]]], "B": [[b]]})
        roles = sorted(sorted(r.items()) for _, r in res)
        self.assertEqual(roles, [[("A", "inner"), ("B", "outer")], [("A", "outer")]])

    def test_voisines(self):
        # Deux carrés côte à côte : un arc commun, un arc propre à chacune.
        a = [(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]
        b = [(1, 0), (2, 0), (2, 1), (1, 1), (1, 0)]
        res = regions.arcs({"A": [[a]], "B": [[b]]})
        communs = [pts for pts, r in res if len(r) == 2]
        self.assertEqual(len(communs), 1)
        self.assertEqual(sorted(communs[0]), [(1, 0), (1, 1)])
        self.assertEqual(len(res), 3)


if __name__ == "__main__":
    unittest.main()
