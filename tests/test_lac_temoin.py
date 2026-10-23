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
import math
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
sys.path.insert(0, DEPOT)
import fabriquer  # noqa: E402
import osmium  # noqa: E402
from osmqc import extrait, geo  # noqa: E402

# Pas d'indicateur de progression pendant les tests (osmqc/progres.py).
os.environ["OSMQC_SANS_PROGRES"] = "1"

LIEU = "Lac-Temoin"
LOT2 = "Riviere-Controle"
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


def lancer(dossier, etapes, lieu=LIEU):
    env = dict(os.environ, PYTHONPATH=DEPOT, OSMQC_HORS_LIGNE="1",
               OSMQC_RQA=os.path.join(dossier, "RQA_CSV.zip"),
               OSMQC_SDA=os.path.join(dossier, "SDA.gpkg"),
               OSMQC_PBF=os.path.join(dossier, "lac-temoin.osm.pbf"))
    for etape in etapes:
        r = subprocess.run([sys.executable, "-m", "osmqc"] + etape.split() + ["lieux/%s.toml" % lieu],
                           cwd=dossier, env=env, capture_output=True, text=True)
        if r.returncode:
            raise AssertionError("« %s » a échoué :\n%s%s" % (etape, r.stdout, r.stderr))


def envoi_simule(dossier, section, lieu=LIEU):
    """Applique sortie/LIEU/SECTION.osc à l'extrait, comme si OSM l'avait
    accepté."""
    pbf = os.path.join(dossier, "lac-temoin.osm.pbf")
    neuf = os.path.join(dossier, "neuf.osm.pbf")
    extrait.appliquer(pbf, os.path.join(dossier, "sortie", lieu, section + ".osc"), neuf)
    os.replace(neuf, pbf)
    # L'index de l'usage des nœuds, tenu à jour par l'envoi, suit l'extrait.
    if os.path.exists(neuf + ".usages"):
        os.replace(neuf + ".usages", pbf + ".usages")


def lire_extrait(dossier):
    """(positions des nœuds, chemins, relations) de l'extrait."""
    pos, chemins, rels = {}, {}, {}
    for o in osmium.FileProcessor(os.path.join(dossier, "lac-temoin.osm.pbf")):
        if o.is_node():
            pos[o.id] = (o.location.lon, o.location.lat)
        elif o.is_way():
            chemins[o.id] = ([n.ref for n in o.nodes], dict(o.tags))
        else:
            rels[o.id] = ([(m.type, m.ref, m.role) for m in o.members], dict(o.tags))
    return pos, chemins, rels


def index_compare(pbf):
    """(index tenu à jour par l'envoi simulé, index recalculé de l'extrait),
    sous une forme comparable."""
    forme = lambda i: ({n: sorted(ws) for n, ws in i.par_noeud.items()}, i.membres)
    extrait._INDEX.clear()
    tenu = extrait.index_usages(pbf, construire=False)
    return (forme(tenu) if tenu else None), forme(extrait._construire_index(pbf, None))


def vide(chemin):
    return [len(b) for b in ET.parse(chemin).getroot()] == [0, 0, 0]


class LacTemoin(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dossier = tempfile.mkdtemp(prefix="lac-temoin-")
        fabriquer.fabriquer(cls.dossier)
        os.makedirs(os.path.join(cls.dossier, "lieux"))
        for lieu in (LIEU, LOT2):
            shutil.copy(os.path.join(ICI, "lac_temoin", lieu + ".toml"), os.path.join(cls.dossier, "lieux"))
        lancer(cls.dossier, ETAPES)
        # Suite, sur une copie : envoi simulé du premier lot, relance (qui
        # ne doit plus rien produire), second lot, son envoi, et relance
        # des deux lots. L'extrait est lu après chaque envoi.
        cls.apres = cls.dossier + "-apres"
        shutil.copytree(cls.dossier, cls.apres)
        envoi_simule(cls.apres, "regions")
        cls.extrait_lot1 = lire_extrait(cls.apres)
        cls.index_lot1 = index_compare(os.path.join(cls.apres, "lac-temoin.osm.pbf"))
        lancer(cls.apres, ["regions preparer"])
        cls.regions_apres = ET.parse(os.path.join(cls.apres, "sortie", LIEU, "regions.osc")).getroot()
        lancer(cls.apres, ["adresses extraire", "regions preparer"], LOT2)
        cls.lot2 = lire_osc(os.path.join(cls.apres, "sortie", LOT2, "regions.osc"))
        envoi_simule(cls.apres, "regions", LOT2)
        cls.extrait_lot2 = lire_extrait(cls.apres)
        lancer(cls.apres, ["regions preparer"])
        lancer(cls.apres, ["regions preparer"], LOT2)
        cls.relances = [vide(os.path.join(cls.apres, "sortie", l, "regions.osc")) for l in (LIEU, LOT2)]
        cls.carte = fabriquer.carte()
        cls.carte_tags = {w: t for w, _, t in cls.carte.chemins}
        sortie = os.path.join(cls.dossier, "sortie", LIEU)
        cls.regions = lire_osc(os.path.join(sortie, "regions.osc"))
        cls.rues = lire_osc(os.path.join(sortie, "rues.osc"))
        cls.adr = lire_osc(os.path.join(sortie, "adresses.osc"))
        with open(os.path.join(sortie, "adresses.csv"), encoding="utf-8") as fh:
            cls.lignes = list(csv.DictReader(fh))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.dossier)
        shutil.rmtree(cls.apres)

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
        lon = {i: o["lon"] for i, o in self.crees(self.regions, "node").items()}
        lon.update({n: p[0] for n, (p, _) in self.carte.noeuds.items()})
        commune = [o for o in self.nouveaux_chemins_limite().values()
                   if all(lon[n] == P(20, 0)[0] for n in o["nodes"])]
        self.assertEqual(len(commune), 1)       # la limite commune, à x = 20 comme au MRNF

    def test_regions_2_chemins_propres(self):
        # Nœuds neufs, ou nœuds d'un chemin de limite existant (le chemin
        # conforme 106, les limites gardées de la voisine); jamais un nœud
        # qui ne sert qu'à une route, une rivière ou un autre objet.
        de_limite = {n for w, ns, t in self.carte.chemins if t.get("boundary") == "administrative"
                     for n in ns}
        for o in self.nouveaux_chemins_limite().values():
            self.assertTrue(all(n < 0 or n in de_limite for n in o["nodes"]), o["nodes"])
            self.assertLessEqual(set(o["tags"]), {"boundary", "admin_level", "note"})

    def test_regions_3_limite_commune(self):
        membres = {i: {r for _, r, _ in self.regions[("modify", "relation", i)]["members"] if r < 0}
                   for i in (1001, 1002)}
        self.assertEqual(len(membres[1001] & membres[1002]), 1)

    def test_regions_5_ce_qui_sort(self):
        supprimes = {(g, i) for (a, g, i) in self.regions if a == "delete"}
        limites = {i for g, i in supprimes if g == "way" and "highway" not in self.carte_tags[i]}
        self.assertEqual(limites, {101, 105, 120})   # lignes de limite seules
        # Les nœuds de la bosse de 101 partent avec elle. (40, 20) sert
        # encore au chemin conforme 106; (0, 20), pile au point triple du
        # MRNF, est réutilisé par les chemins neufs.
        self.assertEqual({i for g, i in supprimes if g == "node"},
                         {self.noeud(x, y) for x, y in ((5, 20), (5, 17), (1, 17), (1, 20))})
        neufs = [o["nodes"] for o in self.nouveaux_chemins_limite().values()]
        self.assertTrue([ns for ns in neufs if self.noeud(0, 20) in ns])
        # Rivière (103) et chemin avec note (104) : retirés, pas supprimés.
        for rel in (1001, 1002):
            refs = {r for _, r, _ in self.regions[("modify", "relation", rel)]["members"]}
            self.assertFalse(refs & {101, 103, 104, 105})
        self.assertFalse([k for k in self.regions if k[0] == "delete" and k[2] in (103, 104)])

    def test_regions_chemin_deja_conforme(self):
        # Le côté est de Sainte-Vérification suivait déjà le MRNF : gardé
        # tel quel, et les chemins neufs se raccordent à ses nœuds.
        self.assertIn(("way", 106, "outer"), self.regions[("modify", "relation", 1002)]["members"])
        self.assertFalse([k for k in self.regions if k[1:] == ("way", 106)])
        noeuds = self.crees(self.regions, "node")
        self.assertNotIn(P(40, 0)[0], {o["lon"] for o in noeuds.values()})

    def test_fichiers_d_envoi_valides(self):
        # Pour les trois fichiers : pas de nœud répété dans un chemin, et
        # toute référence vise un objet créé, ou existant et non supprimé.
        existants = {("node", n) for n in self.carte.noeuds} | {("way", w) for w, _, _ in self.carte.chemins}
        existants |= {("relation", r) for r, _, _ in self.carte.relations}
        for osc in (self.regions, self.rues, self.adr):
            crees = {(g, i) for (a, g, i) in osc if a == "create"}
            supprimes = {(g, i) for (a, g, i) in osc if a == "delete"}
            for (a, g, i), o in osc.items():
                if a == "delete":
                    continue
                ns = o["nodes"]
                self.assertFalse([k for k in range(1, len(ns)) if ns[k] == ns[k - 1]], (g, i))
                if g == "way":
                    self.assertGreaterEqual(len(set(ns)), 2, (g, i))
                refs = [("node", n) for n in ns] + [(t, r) for t, r, _ in o["members"]]
                for ref in refs:
                    self.assertTrue(ref in crees or (ref in existants and ref not in supprimes), (g, i, ref))

    def test_regions_envoi_simule_puis_relance(self):
        # Après l'envoi, plus rien à faire : tout est reconnu comme conforme.
        self.assertEqual([(b.tag, len(b)) for b in self.regions_apres],
                         [("create", 0), ("modify", 0), ("delete", 0)])

    # Voisines et lots successifs

    def test_voisine_modifiee_en_partie(self):
        rc = self.regions[("modify", "relation", 1003)]["members"]
        refs = {r for t, r, _ in rc if t == "way"}
        # Les arcs communs avec le lot (y = 20) sont membres de la voisine.
        communs = {r for _, r, _ in self.regions[("modify", "relation", 1001)]["members"]} | \
                  {r for _, r, _ in self.regions[("modify", "relation", 1002)]["members"]}
        self.assertEqual(len(refs & communs), 2)
        # Ancienne limite sud supprimée; ruisseau retiré sans être touché.
        self.assertIn(("delete", "way", 120), self.regions)
        self.assertFalse(refs & {110, 120})
        self.assertFalse([k for k in self.regions if k[1:] == ("way", 110)])
        # Côté est raccourci; l'aire protégée garde ses deux morceaux.
        reste = self.regions[("modify", "way", 122)]["nodes"]
        self.assertEqual(len(reste), 2)
        aire = [r for t, r, _ in self.regions[("modify", "relation", 1004)]["members"]]
        self.assertEqual(aire[0], 122)
        self.assertLess(aire[1], 0)
        self.assertEqual(aire[2], 123)
        # Deux raccords et une copie du ruisseau, membres de la voisine seule.
        provisoires = [r for r in refs if r < 0 and r not in communs]
        self.assertEqual(len(provisoires), 3)

    def test_aucun_cours_d_eau_modifie(self):
        # Règle 2 : une rivière ou un ruisseau n'est jamais modifié ni
        # supprimé, même quand il formait une limite.
        for osc in (self.regions, self.lot2):
            for (a, g, i), o in osc.items():
                if a != "create" and g == "way":
                    self.assertNotIn("waterway", self.carte_tags.get(i, {}), (a, i))

    def anneaux_fermes(self, extrait_):
        pos, chemins, rels = extrait_
        for rid, (membres, tags) in rels.items():
            if tags.get("type") != "boundary" or tags.get("admin_level") not in ("5", "6", "8"):
                continue                # le Québec et la province voisine sont incomplets ici
            _, ouverts = geo.assembler([chemins[r][0] for t, r, _ in membres if t == "w"])
            self.assertEqual(ouverts, 0, (rid, tags.get("name")))
        # Aucun chemin de limite créé orphelin (un chemin protégé retiré
        # reste, lui, en place).
        membres = {r for m, _ in rels.values() for t, r, _ in m if t == "w"}
        orphelins = [w for w, (_, t) in chemins.items()
                     if t.get("boundary") and w not in membres and w not in self.carte_tags]
        self.assertEqual(orphelins, [])
        # Ni nœud créé dont aucun chemin ne se sert.
        servent = {n for ns, _ in chemins.values() for n in ns}
        self.assertEqual([n for n in pos if n not in servent and n not in self.carte.noeuds], [])

    def test_anneaux_fermes_apres_chaque_envoi(self):
        self.anneaux_fermes(self.extrait_lot1)
        self.anneaux_fermes(self.extrait_lot2)

    def test_second_lot(self):
        # Lac-Témoin et Sainte-Vérification ne changent pas : leurs arcs
        # avec Rivière-Contrôle sont déjà conformes.
        self.assertFalse([k for k in self.lot2 if k[1] == "relation" and k[2] in (1001, 1002)])
        self.assertIn(("modify", "relation", 1003), self.lot2)
        # Après son envoi, Rivière-Contrôle ne garde que des chemins sur le
        # tracé du MRNF : raccords et copie ont disparu.
        pos, chemins, rels = self.extrait_lot2
        anneau = [P(x, y) for x, y in fabriquer.MUNICIPALITES["99003"][1]]
        for t, r, _ in rels[1003][0]:
            if t == "w":
                for n in chemins[r][0]:
                    self.assertLess(geo.distance_ligne(pos[n], anneau), 0.01, r)
        # La réserve, elle, est restée entière.
        self.assertEqual(len([m for m in rels[1004][0] if m[0] == "w"]), 3)

    def test_mrc_et_region(self):
        # Le lot touche le contour de la MRC et de la région : elles
        # prennent ses arcs, avec deux raccords partagés vers l'ancien
        # contour gardé au nord (le chemin 133, raccourci).
        mrc, reg = (self.regions[("modify", "relation", r)]["members"] for r in (1200, 1300))
        self.assertEqual(mrc, reg)
        neufs = self.crees(self.regions, "way")
        nord = {self.noeud(40, 30), self.noeud(0, 30)}
        raccords = [neufs[r] for _, r, _ in mrc if r < 0 and set(neufs[r]["nodes"]) & nord]
        self.assertEqual(len(raccords), 2)
        self.assertTrue(all(o["tags"]["admin_level"] == "5" for o in raccords))
        self.assertEqual(self.regions[("modify", "way", 133)]["nodes"], [self.noeud(40, 30), self.noeud(0, 30)])
        # Après le second lot, leur contour ne suit plus que le tracé du
        # MRNF, la frontière gardée à part.
        pos, chemins, rels = self.extrait_lot2
        contour = [P(x, y) for x, y in fabriquer.CONTOUR]
        frontiere = {w for t, w, _ in rels[1100][0] if t == "w"}
        sur_frontiere = {n for w in frontiere for n in chemins[w][0]}
        for rid in (1200, 1300):
            ws = [r for t, r, _ in rels[rid][0] if t == "w"]
            self.assertNotIn(133, ws)
            for w in ws:
                if w not in frontiere:
                    for n in set(chemins[w][0]) - sur_frontiere:
                        self.assertLess(geo.distance_ligne(pos[n], contour), 0.01, (rid, w))

    def test_index_usages_tenu_a_jour(self):
        # L'envoi simulé tient à jour l'index de l'usage des nœuds : pour
        # chaque nœud de limite de l'extrait, les mêmes chemins que l'index
        # recalculé. Il peut garder en plus des nœuds qui ne sont plus de
        # limite (ceux de la rivière 103, retirée des relations), avec leur
        # usage exact, et des nœuds membres en surplus.
        tenu, recalcule = self.index_lot1
        self.assertIsNotNone(tenu)
        par_noeud, membres_tenus = tenu
        attendu, membres = recalcule
        self.assertEqual({n: par_noeud.get(n) for n in attendu}, attendu)
        self.assertTrue(membres <= membres_tenus)

    def test_relance_apres_les_deux_lots(self):
        self.assertEqual(self.relances, [True, True])

    def test_frontiere_gardee(self):
        # La frontière du Québec (y = -0,5 dans OSM, y = 0 au MRNF) est
        # gardée : coupée à (20; -0,5), là où la limite commune la rejoint,
        # sans qu'aucun nœud ne bouge.
        noeuds = self.crees(self.regions, "node")
        x = [n for n, o in noeuds.items() if (o["lon"], o["lat"]) == P(20, -0.5)]
        self.assertEqual(len(x), 1)
        ouest = self.regions[("modify", "way", 107)]["nodes"]
        self.assertEqual(ouest, [self.noeud(19, -0.5), x[0]])
        (morceau,) = [i for i, o in self.crees(self.regions, "way").items()
                      if o["tags"].get("admin_level") == "4"]
        self.assertEqual(self.crees(self.regions, "way")[morceau]["nodes"], [x[0], self.noeud(40, -0.5)])
        for rel in (1100, 1101):            # le Québec et la province voisine
            membres = [r for _, r, _ in self.regions[("modify", "relation", rel)]["members"]]
            self.assertEqual(membres, [102, 107, morceau])
        # Chaque municipalité garde sa part de la frontière.
        lt = {r for _, r, _ in self.regions[("modify", "relation", 1001)]["members"]}
        sv = {r for _, r, _ in self.regions[("modify", "relation", 1002)]["members"]}
        self.assertTrue({102, 107} <= lt and morceau not in lt)
        self.assertTrue(morceau in sv and not {102, 107} & sv)
        # La limite commune descend jusqu'à la frontière d'OSM.
        commune = [o for o in self.nouveaux_chemins_limite().values()
                   if x[0] in o["nodes"] and o["tags"]["admin_level"] == "8"]
        self.assertEqual(len(commune), 1)
        self.assertFalse([k for k in self.regions if k[0] == "delete" and k[2] in (102, 107)])

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
        # Route 999 : coupée à x = 20, et son ancienne coupure à x = 19
        # fusionnée (300 prolongé jusqu'à la nouvelle limite, 301 supprimé).
        # Rue Principale : coupée à x = 20.
        for route in (300, 310):
            fin = self.regions[("modify", "way", route)]["nodes"][-1]
            self.assertEqual(noeuds[fin]["lon"], P(20, 0)[0])
        self.assertIn(("delete", "way", 301), self.regions)
        neufs = {i for i, o in self.crees(self.regions, "way").items() if "highway" in o["tags"]}
        self.assertEqual(len(neufs), 2)
        membres = [r for _, r, _ in self.regions[("modify", "relation", 700)]["members"]]
        self.assertEqual(membres[0], 300)
        self.assertIn(membres[1], neufs)        # le nouveau segment suit l'ancien
        self.assertEqual(len(membres), 2)
        self.assertEqual(self.regions[("modify", "relation", 700)]["tags"]["ref"], "999")

    def test_regions_7_fusion_des_coupures_inutiles(self):
        # Chemin du Lac : coupé sur l'ancienne limite, loin de la nouvelle.
        self.assertEqual(self.regions[("modify", "way", 320)]["nodes"][-1], self.noeud(3, 18))
        self.assertIn(("delete", "way", 328), self.regions)
        # Allée du Témoin : le sentier de motoneige ne suit qu'un bout.
        self.assertFalse([k for k in self.regions if k[2] in (332, 333, 703)])
        self.assertIn("way 332 et way 333 (Allée du Témoin) : fusion refusée, relations différentes",
                      self.rapport("regions.md"))

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
        # Pas encore certifiée, ou sans clé de jumelage avec le réseau
        # routier : signalée comme exclue, jamais créée.
        for num, raison in (("80", "non certifiée"), ("90", "sans clé de jumelage avec le réseau routier")):
            self.assertEqual((self.ligne(num)["statut"], self.ligne(num)["detail"]), ("exclu", raison))
            self.assertIsNone(self.adresse(num))

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
