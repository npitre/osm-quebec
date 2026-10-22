import os
import unittest

from osmqc import osm, regions, rues, rqa

# Pas d'indicateur de progression pendant les tests (osmqc/progres.py).
os.environ["OSMQC_SANS_PROGRES"] = "1"

# Petits jeux de données construits à la main, autour de 46° N, 75° O.
# Un millième de degré vaut environ 77 m en longitude et 111 m en latitude.
LON, LAT = -75.0, 46.0


def index(noeuds, chemins):
    """noeuds : {id: (dx, dy)} en millièmes de degré; chemins :
    [(id, [ids de nœuds], {étiquettes})]."""
    elems = [{"type": "node", "id": n, "lon": LON + dx / 1000, "lat": LAT + dy / 1000, "version": 1}
             for n, (dx, dy) in noeuds.items()]
    elems += [{"type": "way", "id": w, "nodes": ns, "tags": t, "version": 1} for w, ns, t in chemins]
    return osm.Index(elems)


def adr(numero, rue, dx, dy, municipalite="80135"):
    return rqa.Adresse(ident="x", municipalite=municipalite, nom_municipalite="", odonyme="1",
                       rue=rue, numero=numero, suffixe="", unite="", code_postal="",
                       lon=LON + dx / 1000, lat=LAT + dy / 1000, qualite="Bâtiment",
                       lot="", matricule="", date_creation="", fin="")


def rue(nom, highway="residential"):
    return {"highway": highway, "name": nom}


def statut(resultats, nom):
    return next(r for r in resultats if r.officiel == nom)


class Rues(unittest.TestCase):
    def setUp(self):
        # Une rue est-ouest de deux segments, le long de y = 0.
        self.noeuds = {1: (0, 0), 2: (5, 0), 3: (10, 0)}

    def test_conforme(self):
        idx = index(self.noeuds, [(10, [1, 2], rue("Chemin du Tour-du-Lac")),
                                  (11, [2, 3], rue("Chemin du Tour-du-Lac"))])
        r = rues.analyser([adr("1084", "Chemin du Tour-du-Lac", 1, 0.3)], idx)
        self.assertEqual(statut(r, "Chemin du Tour-du-Lac").statut, "conforme")

    def test_casse_renomme_toute_la_rue(self):
        # Le second segment est loin des adresses, mais il est relié au
        # premier et porte le même nom : il est renommé aussi.
        noeuds = {1: (0, 0), 2: (5, 0), 3: (20, 0)}
        idx = index(noeuds, [(10, [1, 2], rue("Chemin de la Martinique")),
                             (11, [2, 3], rue("Chemin de la Martinique"))])
        r = statut(rues.analyser([adr("10", "Chemin de La Martinique", 1, 0.3)], idx),
                   "Chemin de La Martinique")
        self.assertEqual(r.statut, "à renommer")
        self.assertEqual(r.renommer, [10, 11])
        plan, conflits = rues.plan_renommage([r])
        self.assertEqual(plan, {10: "Chemin de La Martinique", 11: "Chemin de La Martinique"})
        self.assertEqual(conflits, {})

    def test_tirets_et_accents(self):
        idx = index(self.noeuds, [(10, [1, 2], rue("Chemin du Tour du Lac"))])
        r = statut(rues.analyser([adr("1084", "Chemin du Tour-du-Lac", 1, 0.3)], idx),
                   "Chemin du Tour-du-Lac")
        self.assertEqual(r.statut, "à renommer")

    def test_autre_nom_non_renomme(self):
        idx = index(self.noeuds, [(10, [1, 2], rue("Chemin Cormier"))])
        r = statut(rues.analyser([adr("5", "Chemin de la Promenade", 1, 0.3)], idx),
                   "Chemin de la Promenade")
        self.assertEqual(r.statut, "autre nom")
        self.assertEqual(r.renommer, [])
        self.assertEqual(r.candidats[0][0], 10)

    def test_voie_sans_nom(self):
        idx = index(self.noeuds, [(10, [1, 2], {"highway": "service"})])
        r = statut(rues.analyser([adr("3", "Allée des Belles-Vues", 1, 0.3)], idx),
                   "Allée des Belles-Vues")
        self.assertEqual(r.statut, "sans nom")
        self.assertEqual(r.candidats[0][0], 10)

    def test_absente(self):
        idx = index(self.noeuds, [(10, [1, 2], rue("Chemin du Tour-du-Lac"))])
        # À 2 km de toute voie.
        r = statut(rues.analyser([adr("1", "Île du Canard-Blanc", 1, 20)], idx), "Île du Canard-Blanc")
        self.assertEqual(r.statut, "absente")

    def test_conflit(self):
        a = rues.Rue("Rue de la Forge", "1", 1, renommer=[10])
        b = rues.Rue("Rue De La Forge", "2", 1, renommer=[10])
        plan, conflits = rues.plan_renommage([a, b])
        self.assertEqual(plan, {})
        self.assertIn(10, conflits)


class Coupures(unittest.TestCase):
    # Une limite nord-sud en x = 0, de y = -10 à y = 10.
    limite = [(LON, LAT - 0.010), (LON, LAT + 0.010)]

    def actions(self, idx, nouvelles, anciennes=()):
        return sorted(c[0] for c in regions.coupures(idx, nouvelles, list(anciennes)))

    def test_deja_coupee(self):
        # Deux segments du même nom se rejoignent sur la limite.
        idx = index({1: (-5, 0), 2: (0, 0), 3: (5, 0)},
                    [(10, [1, 2], rue("Route 315", "secondary")),
                     (11, [2, 3], rue("Route 315", "secondary"))])
        self.assertEqual(self.actions(idx, [self.limite]), ["déjà coupée"])

    def test_coupure_a_ajouter(self):
        idx = index({1: (-5, 0), 2: (5, 0)}, [(10, [1, 2], rue("Route 315", "secondary"))])
        self.assertEqual(self.actions(idx, [self.limite]), ["coupure à ajouter"])

    def test_coupure_a_deplacer(self):
        # La coupure existe, mais à environ 150 m de la limite.
        idx = index({1: (-5, 0), 2: (2, 0), 3: (6, 0)},
                    [(10, [1, 2], rue("Route 315", "secondary")),
                     (11, [2, 3], rue("Route 315", "secondary"))])
        self.assertEqual(self.actions(idx, [self.limite]), ["coupure à déplacer"])

    def test_cul_de_sac_n_est_pas_une_coupure(self):
        # Une route qui finit sur l'ancienne limite (un quai au bord de
        # l'eau) n'a pas de coupure à retirer.
        ancienne = [(LON + 0.005, LAT - 0.010), (LON + 0.005, LAT + 0.010)]
        idx = index({1: (-5, 0), 2: (5, 0)}, [(10, [1, 2], rue("Chemin du Quai"))])
        loin = [(LON + 0.050, LAT - 0.010), (LON + 0.050, LAT + 0.010)]
        self.assertEqual(self.actions(idx, [loin], [ancienne]), [])

    def test_coupure_devenue_inutile(self):
        # Coupure sur l'ancienne limite, loin des nouvelles, entre deux
        # segments aux étiquettes identiques : inutile.
        ancienne = [(LON + 0.005, LAT - 0.010), (LON + 0.005, LAT + 0.010)]
        loin = [(LON + 0.050, LAT - 0.010), (LON + 0.050, LAT + 0.010)]
        idx = index({1: (0, 0), 2: (5, 0), 3: (10, 0)},
                    [(10, [1, 2], rue("Chemin de la Grave")),
                     (11, [2, 3], rue("Chemin de la Grave"))])
        self.assertEqual(self.actions(idx, [loin], [ancienne]), ["coupure devenue inutile"])

    def test_coupure_utile_a_autre_chose(self):
        # Même situation, mais un des segments est un pont : la coupure
        # sert à autre chose et n'est pas signalée.
        ancienne = [(LON + 0.005, LAT - 0.010), (LON + 0.005, LAT + 0.010)]
        loin = [(LON + 0.050, LAT - 0.010), (LON + 0.050, LAT + 0.010)]
        pont = dict(rue("Chemin de la Grave"), bridge="yes")
        idx = index({1: (0, 0), 2: (5, 0), 3: (10, 0)},
                    [(10, [1, 2], rue("Chemin de la Grave")), (11, [2, 3], pont)])
        self.assertEqual(self.actions(idx, [loin], [ancienne]), [])


if __name__ == "__main__":
    unittest.main()
