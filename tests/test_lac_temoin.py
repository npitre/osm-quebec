# Essai de bout en bout sur Lac-Témoin, une région fictive (voir
# tests/lac_temoin/fabriquer.py) : les vraies commandes, sur des données
# fabriquées, en mode hors ligne (aucun accès réseau). Deux vérifications :
#
#   - des attentes écrites cas par cas, nommées d'après les règles du
#     README (test_regions_7_..., test_adresses_1_..., etc.);
#   - une sortie de référence, tests/lac_temoin/attendu/ : fichiers
#     d'envoi et rapports. Toute différence fait échouer le test. Après un
#     changement voulu, régénérer la référence et relire le diff de git :
#       OSMQC_REGENERER=1 python3 -m unittest tests.test_lac_temoin

import csv
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ICI = os.path.dirname(os.path.abspath(__file__))
DEPOT = os.path.dirname(ICI)
sys.path.insert(0, os.path.join(ICI, "lac_temoin"))
import fabriquer  # noqa: E402

LIEU = "Lac-Temoin"
ETAPES = ["adresses extraire", "adresses osm", "regions preparer", "rues preparer",
          "adresses preparer"]
REFERENCE = ["sortie/regions.osc", "sortie/rues.osc", "sortie/adresses.osc",
             "rapports/regions.md", "rapports/rues.md", "rapports/adresses.md"]
ATTENDU = os.path.join(ICI, "lac_temoin", "attendu")


def P(x, y):
    return fabriquer.P(x, y)


def lire_osc(chemin):
    """{(action, type, id): {"tags", "nodes", "members", "lon", "lat"}}"""
    res = {}
    for bloc in ET.parse(chemin).getroot():
        for e in bloc:
            o = {"tags": {t.get("k"): t.get("v") for t in e.iter("tag")},
                 "nodes": [int(n.get("ref")) for n in e.iter("nd")],
                 "members": [(m.get("type"), int(m.get("ref")), m.get("role")) for m in e.iter("member")]}
            if e.get("lon"):
                o["lon"], o["lat"] = float(e.get("lon")), float(e.get("lat"))
            res[(bloc.tag, e.tag, int(e.get("id")))] = o
    return res


class LacTemoin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = tempfile.mkdtemp(prefix="lac-temoin-")
        fabriquer.fabriquer(cls.dossier)
        os.makedirs(os.path.join(cls.dossier, "lieux"))
        shutil.copy(os.path.join(ICI, "lac_temoin", LIEU + ".toml"), os.path.join(cls.dossier, "lieux"))
        env = dict(os.environ, PYTHONPATH=DEPOT, OSMQC_HORS_LIGNE="1",
                   OSMQC_RQA=os.path.join(cls.dossier, "RQA_CSV.zip"),
                   OSMQC_SDA=os.path.join(cls.dossier, "SDA.gpkg"),
                   OSMQC_PBF=os.path.join(cls.dossier, "lac-temoin.osm.pbf"))
        for etape in ETAPES:
            r = subprocess.run([sys.executable, "-m", "osmqc"] + etape.split() + ["lieux/%s.toml" % LIEU],
                               cwd=cls.dossier, env=env, capture_output=True, text=True)
            if r.returncode:
                raise AssertionError("« %s » a échoué :\n%s%s" % (etape, r.stdout, r.stderr))
        cls.carte = fabriquer.carte()
        sortie = os.path.join(cls.dossier, "sortie", LIEU)
        cls.regions = lire_osc(os.path.join(sortie, "regions.osc"))
        cls.rues = lire_osc(os.path.join(sortie, "rues.osc"))
        cls.adr = lire_osc(os.path.join(sortie, "adresses.osc"))
        with open(os.path.join(sortie, "adresses.csv"), encoding="utf-8") as fh:
            cls.lignes = list(csv.DictReader(fh))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dossier)

    # Outils

    def rapport(self, nom):
        with open(os.path.join(self.dossier, "rapports", LIEU, nom), encoding="utf-8") as fh:
            return fh.read()

    def noeud(self, x, y):
        return self.carte.par_point[P(x, y)]

    def crees(self, osc, genre):
        return {i: o for (a, g, i), o in osc.items() if a == "create" and g == genre}

    def nouveaux_chemins_limite(self):
        return {i: o for i, o in self.crees(self.regions, "way").items() if "boundary" in o["tags"]}

    def adresse(self, numero, rue="Chemin du Lac"):
        """Nœud créé pour cette adresse, ou None."""
        trouves = [o for o in self.crees(self.adr, "node").values()
                   if o["tags"].get("addr:street") == rue and o["tags"]["addr:housenumber"] == numero]
        self.assertLessEqual(len(trouves), 1)
        return trouves[0] if trouves else None

    def ligne(self, numero, rue="Chemin du Lac"):
        (l,) = [l for l in self.lignes if l["rue"] == rue and l["numero"] == numero]
        return l

    # Régions

    def test_regions_1_trace_du_mrnf(self):
        noeuds = self.crees(self.regions, "node")
        commune = [o for o in self.nouveaux_chemins_limite().values()
                   if all(noeuds[n]["lon"] == P(20, 0)[0] for n in o["nodes"] if n in noeuds)]
        self.assertEqual(len(commune), 1)       # la limite commune, à x = 20 comme au MRNF

    def test_regions_2_chemins_propres(self):
        for o in self.nouveaux_chemins_limite().values():
            self.assertTrue(all(n < 0 for n in o["nodes"]))
            self.assertLessEqual(set(o["tags"]), {"boundary", "admin_level", "note"})

    def test_regions_3_limite_commune(self):
        membres = {i: {r for _, r, _ in self.regions[("modify", "relation", i)]["members"] if r < 0}
                   for i in (1001, 1002)}
        self.assertEqual(len(membres[1001] & membres[1002]), 1)

    def test_regions_5_ce_qui_sort(self):
        supprimes = {(g, i) for (a, g, i) in self.regions if a == "delete"}
        self.assertEqual({i for g, i in supprimes if g == "way"}, {101, 105})   # lignes de limite seules
        self.assertEqual({i for g, i in supprimes if g == "node"}, {self.noeud(0, 20), self.noeud(40, 20)})
        # Frontière (102), rivière (103) et chemin avec note (104) : retirés, pas supprimés.
        for rel in (1001, 1002):
            refs = {r for _, r, _ in self.regions[("modify", "relation", rel)]["members"]}
            self.assertFalse(refs & {101, 102, 103, 104, 105})

    def test_regions_5_note_reportee(self):
        notes = [o for o in self.nouveaux_chemins_limite().values() if "note" in o["tags"]]
        self.assertEqual([o["tags"]["note"] for o in notes], ["Limite à vérifier sur le terrain"])

    def test_regions_5_etiquettes_des_relations(self):
        for ident, _, tags in self.carte.relations:
            if ident in (1001, 1002):
                self.assertEqual(self.regions[("modify", "relation", ident)]["tags"], tags)

    def test_regions_6_verification(self):
        r = self.rapport("regions.md")
        self.assertIn("15 Rue Principale", r)     # du mauvais côté de l'ancienne limite d'OSM

    def test_regions_7_coupures(self):
        noeuds = self.crees(self.regions, "node")
        for route in (301, 310):
            fin = self.regions[("modify", "way", route)]["nodes"][-1]
            self.assertEqual(noeuds[fin]["lon"], P(20, 0)[0])     # coupée à x = 20
        neufs = {i for i, o in self.crees(self.regions, "way").items() if "highway" in o["tags"]}
        self.assertEqual(len(neufs), 2)
        membres = [r for _, r, _ in self.regions[("modify", "relation", 700)]["members"]]
        self.assertEqual(membres[:2], [300, 301])
        self.assertIn(membres[2], neufs)        # le nouveau segment suit l'ancien
        self.assertEqual(self.regions[("modify", "relation", 700)]["tags"]["ref"], "999")

    def test_regions_8_lien_lieu(self):
        r = self.rapport("regions.md")
        self.assertRegex(r, r"\| Sainte-Vérification \| sans lien \|")
        self.assertRegex(r, r"\| Lac-Témoin \| lié \|")

    # Rues

    def renommes(self):
        return {i: o["tags"] for (a, g, i), o in self.rues.items() if a == "modify"}

    def test_rues_1_nom_officiel(self):
        self.assertEqual(self.renommes()[323]["name"], "Rue Saint-Jean")      # « St- » du RQA

    def test_rues_2_renommage(self):
        r = self.renommes()
        self.assertEqual(r[321]["name"], "Chemin de La Pointe")             # casse
        self.assertEqual(r[322]["name"], "Chemin de La Pointe")             # segment relié
        self.assertEqual(r[330]["name"], "Chemin du Tour-du-Lac")           # tirets
        self.assertTrue(all("old_name" not in r[w] for w in (321, 322, 323, 330)))
        self.assertEqual(r[326]["old_name"], "Chemin du Quai")              # renommage à la main
        self.assertEqual(set(r), {321, 322, 323, 326, 330})

    def test_rues_3_autres_ecarts(self):
        r = self.rapport("rues.md")
        for nom in ("Chemin des Érables", "Allée des Bouleaux", "Chemin Fantôme"):
            self.assertIn(nom, r)
        self.assertNotIn(324, self.renommes())                              # Chemin Cormier

    def test_rues_4_adresses_apres_renommage(self):
        self.assertIsNotNone(self.adresse("10", "Chemin de La Pointe"))
        self.assertIsNotNone(self.adresse("5", "Rue Saint-Jean"))
        self.assertIsNotNone(self.adresse("1", "Chemin de la Jetée"))

    # Adresses

    def test_adresses_1_logements_et_suffixes(self):
        self.assertEqual(self.adresse("250")["tags"]["addr:unit"], "1;2")
        self.assertIsNotNone(self.adresse("270;270A"))
        self.assertIsNotNone(self.adresse("280"))
        self.assertIsNotNone(self.adresse("280B"))                          # à 76 m : distincte
        self.assertEqual(self.adresse("290")["tags"]["addr:unit"], "1")     # sans adresse principale
        self.assertIsNotNone(self.adresse("300A;300B"))                     # pas de « 300 » inventé
        self.assertNotIn("pas d'adresse principale", self.ligne("280B")["detail"])

    def test_logements_douteux(self):
        self.assertNotIn("addr:unit", self.adresse("260")["tags"])
        self.assertIn("9999-260 Chemin du Lac", self.rapport("adresses.md"))

    def test_adresses_2_terminees(self):
        self.assertFalse([l for l in self.lignes if l["numero"] == "60" and l["rue"] == "Chemin du Lac"])

    def test_adresses_3_exclusions(self):
        self.assertEqual(self.ligne("70")["statut"], "exclu")
        self.assertIsNone(self.adresse("70"))

    def test_adresses_4_rue_dans_osm(self):
        for num, rue in (("1", "Chemin des Érables"), ("2", "Allée des Bouleaux"), ("1", "Chemin Fantôme")):
            self.assertEqual(self.ligne(num, rue)["statut"], "à revoir")
            self.assertIsNone(self.adresse(num, rue))

    def test_adresses_5_doublons(self):
        n30 = next(i for i, (p, t) in self.carte.noeuds.items() if t.get("addr:housenumber") == "30")
        self.assertEqual(self.adr[("modify", "node", n30)]["tags"],
                         {"addr:housenumber": "30", "addr:street": "Chemin du Lac", "addr:postcode": "J0T 1A0"})
        self.assertEqual(self.ligne("40")["statut"], "existant")
        self.assertEqual(self.ligne("50")["statut"], "existant")             # bâtiment numéroté
        for num in ("30", "40", "50"):
            self.assertIsNone(self.adresse(num))

    def test_adresses_6_etiquettes(self):
        for o in self.crees(self.adr, "node").values():
            self.assertLessEqual(set(o["tags"]), {"addr:housenumber", "addr:street", "addr:postcode",
                                                  "addr:unit", "entrance"})
            self.assertIn("addr:postcode", o["tags"])

    def test_adresses_7_interpolations(self):
        supprimes = {i for (a, g, i) in self.adr if a == "delete" and g == "way"}
        self.assertEqual(supprimes, {400})      # 402 : autre municipalité; 404 : nœud partagé
        noeuds = {i for (a, g, i) in self.adr if a == "delete" and g == "node"}
        self.assertEqual(noeuds, {n for w, ns, _ in self.carte.chemins if w == 400 for n in ns})

    def test_adresses_8_positions_et_entree(self):
        rue = "Rue des Portes"
        a10, a20, a30 = (self.adresse(n, rue) for n in ("10", "20", "30"))
        self.assertEqual((a10["lon"], a10["lat"]), P(35, 3.5))
        self.assertEqual(a10["tags"]["entrance"], "home")
        self.assertEqual(a20["tags"]["entrance"], "shop")
        self.assertEqual((a30["lon"], a30["lat"]), P(34.9, 10))             # vérifiée, loin du RQA
        self.assertNotIn("entrance", a30["tags"])
        self.assertIn("vérifié", self.ligne("30", rue)["detail"])
        for num in ("40", "50", "52", "60"):                                # approximative, partagée, aucune
            self.assertEqual(self.ligne(num, rue)["position"], "RQA")

    # Sortie de référence

    def test_sortie_de_reference(self):
        regenerer = os.environ.get("OSMQC_REGENERER")
        differences = []
        for f in REFERENCE:
            dossier, nom = f.split("/")
            produit = os.path.join(self.dossier, dossier, LIEU, nom)
            attendu = os.path.join(ATTENDU, nom)
            if regenerer:
                os.makedirs(ATTENDU, exist_ok=True)
                shutil.copy(produit, attendu)
                continue
            with open(produit, encoding="utf-8") as a, open(attendu, encoding="utf-8") as b:
                if a.read() != b.read():
                    differences.append(nom)
        self.assertEqual(differences, [], "sortie différente de tests/lac_temoin/attendu/ : relancer avec "
                         "OSMQC_REGENERER=1 si le changement est voulu, puis relire le diff")


if __name__ == "__main__":
    unittest.main()
