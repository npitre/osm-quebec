# Un test (au moins) par règle du README, nommé d'après elle :
# test_regions_1, test_rues_2, test_adresses_7, etc. Petits exemples
# construits à la main, sans données ni accès réseau.

import os
import struct
import tempfile
import unittest
import xml.etree.ElementTree as ET
from unittest import mock

from osmqc import adresses, envoi, geo, osm, osmchange, positions, regions, rqa, rues

LON, LAT = -75.0, 46.0


def P(dx, dy):
    """Point à dx, dy millièmes de degré du point de référence."""
    return (round(LON + dx / 1000, 7), round(LAT + dy / 1000, 7))


def carre(x0, y0, x1, y1):
    return [P(x0, y0), P(x1, y0), P(x1, y1), P(x0, y1), P(x0, y0)]


def index(noeuds, chemins, relations=()):
    elems = [{"type": "node", "id": n, "lon": P(*xy)[0], "lat": P(*xy)[1], "version": 1,
              "tags": t} for n, (xy, t) in noeuds.items()]
    elems += [{"type": "way", "id": w, "nodes": ns, "tags": t, "version": 2} for w, ns, t in chemins]
    elems += list(relations)
    return osm.Index(elems)


class Rel:
    """Relation de limite minimale, comme regions.Relation."""

    def __init__(self, ident, chemins=(), autres=(), tags=None):
        self.id = ident
        self.chemins = list(chemins)
        self.tags = tags or {}
        self.rel = {"type": "relation", "id": ident, "version": 5, "tags": self.tags,
                    "members": list(autres) + [{"type": "way", "ref": w, "role": "outer"} for w in chemins]}


def adr(numero, rue="Chemin du Tour-du-Lac", dx=1, dy=0.3, suffixe="", unite="", fin="",
        municipalite="80135", categorie="RESI", nom_municipalite="Duhamel", matricule="",
        lot="", logements=""):
    p = P(dx, dy)
    return rqa.Adresse(ident="x", municipalite=municipalite, nom_municipalite=nom_municipalite,
                       odonyme="1", rue=rue, numero=numero, suffixe=suffixe, unite=unite,
                       code_postal="J0V 1G0", lon=p[0], lat=p[1], qualite="Bâtiment",
                       lot=lot, matricule=matricule, date_creation="20211211", fin=fin,
                       categorie=categorie, nombre_unite=logements)


def rue_osm(nom="Chemin du Tour-du-Lac"):
    """Une rue est-ouest le long de y = 0, de x = 0 à x = 10."""
    return index({1: ((0, 0), {}), 2: ((5, 0), {}), 3: ((10, 0), {})},
                 [(10, [1, 2], {"highway": "residential", "name": nom}),
                  (11, [2, 3], {"highway": "residential", "name": nom})])


# Régions

class Regions(unittest.TestCase):
    def setUp(self):
        # Deux municipalités voisines, A à gauche, B à droite.
        self.officiel = {"A": [[carre(0, 0, 10, 10)]], "B": [[carre(10, 0, 20, 10)]]}
        self.rels = {"A": Rel(100, [500]), "B": Rel(200, [501])}

    def test_regions_1_trace_du_mrnf(self):
        plan = regions.preparer(self.officiel, self.rels)
        sommets = {p for poly in self.officiel.values() for a in poly[0] for p in a}
        self.assertEqual(set(plan["noeuds"]), sommets)

    def test_regions_2_chemins_propres(self):
        plan = regions.preparer(self.officiel, self.rels)
        # Tous les nœuds des chemins de limite sont neufs.
        self.assertTrue(all(n < 0 for _, ids, _ in plan["chemins"] for n in ids))
        racine = osmchange.osc_regions(plan, {c: r.rel for c, r in self.rels.items()}, [], [], osm.Index([]))
        for w in racine.find("create").iter("way"):
            self.assertEqual({t.get("k") for t in w.iter("tag")}, {"boundary", "admin_level"})

    def test_regions_3_limite_commune(self):
        plan = regions.preparer(self.officiel, self.rels)
        a = {m["ref"] for m in plan["membres"]["A"]}
        b = {m["ref"] for m in plan["membres"]["B"]}
        self.assertEqual(len(a & b), 1)       # le côté commun, un seul chemin

    def test_regions_4_contour_ferme_reutilise(self):
        # Une seule municipalité, une île : son contour fermé reprend le
        # chemin de la relation parente.
        officiel = {"A": [[carre(0, 0, 10, 10)]]}
        parent = Rel(900, [800])
        parent.index = index({1: ((0, 0), {}), 2: ((10, 0), {}), 3: ((10, 10), {}), 4: ((0, 10), {})},
                             [(800, [1, 2, 3, 4, 1], {"boundary": "administrative", "admin_level": "6"})])
        plan = regions.preparer(officiel, {"A": Rel(100, [500])}, parent)
        self.assertEqual(plan["chemins"], [])
        self.assertEqual([m["ref"] for m in plan["membres"]["A"]], [800])

    def test_regions_4_contour_ouvert_trace(self):
        # Avec deux municipalités, le contour extérieur est fait d'arcs
        # ouverts : tracés d'après le MRNF, même avec une relation parente.
        parent = Rel(900, [800])
        parent.index = index({1: ((0, 0), {}), 2: ((20, 0), {})}, [(800, [1, 2], {})])
        plan = regions.preparer(self.officiel, self.rels, parent)
        self.assertNotIn(800, {m["ref"] for lst in plan["membres"].values() for m in lst})

    def _retires(self):
        noeuds = {n: ((n, 0), {}) for n in range(1, 11)}
        chemins = [(600, [1, 2], {"boundary": "administrative"}),
                   (601, [3, 4], {"natural": "coastline"}),
                   (602, [5, 6], {"boundary": "administrative", "note": "à vérifier"}),
                   (603, [7, 8], {"boundary": "administrative", "admin_level": "4"}),
                   (604, [9, 10], {"boundary": "administrative", "disputed_by": "NL"})]
        return index(noeuds, chemins)

    @mock.patch.object(regions, "_usages_api", lambda nids: ({n: set() for n in nids}, set()))
    @mock.patch.object(regions, "relations_du_chemin", lambda w: [100])
    def test_regions_5_ce_qui_sort(self):
        idx = self._retires()
        chemins, noeuds = regions.supprimables([600, 601, 602, 603, 604], idx, [100])
        self.assertEqual(chemins, [600])      # la ligne de limite seule
        self.assertEqual(noeuds, [1, 2])      # littoral, note, frontière et disputed_by restent

    def test_regions_5_chemins_proteges(self):
        for t in ({"note": "x"}, {"fixme": "x"}, {"description": "x"}, {"disputed_by": "NL"},
                  {"disputed": "yes"}):
            self.assertTrue(regions.protege(dict(t, boundary="administrative")), t)
        self.assertFalse(regions.protege({"boundary": "administrative", "admin_level": "8"}))
        self.assertTrue(regions.frontiere({"admin_level": "4"}))
        self.assertTrue(regions.frontiere({"admin_level": "2"}))
        self.assertFalse(regions.frontiere({"admin_level": "6"}))

    def test_regions_5_note_reportee(self):
        idx = self._retires()
        plan = regions.preparer(self.officiel, self.rels)
        res = regions.reporter_notes([602], idx, plan)
        self.assertEqual(res[0][2], {"note": "à vérifier"})
        self.assertEqual(plan["etiquettes"][res[0][1]], {"note": "à vérifier"})

    def test_regions_5_etiquettes_des_relations(self):
        plan = regions.preparer(self.officiel, self.rels)
        self.rels["A"].rel["tags"] = {"name": "A", "boundary": "administrative"}
        racine = osmchange.osc_regions(plan, {"A": self.rels["A"].rel}, [], [], osm.Index([]))
        rel = racine.find("modify").find("relation")
        self.assertEqual({t.get("k"): t.get("v") for t in rel.iter("tag")},
                         {"name": "A", "boundary": "administrative"})

    def test_regions_6_verification(self):
        a = adr("1", dx=15, dy=5, municipalite="B")
        compte, ecarts = regions.comparer([a], {c: p for c, p in self.officiel.items()},
                                          {"A": [carre(0, 0, 20, 10)]})
        self.assertEqual(compte[("MRNF", True)], 1)
        self.assertEqual(compte[("OSM", False)], 1)
        self.assertEqual(ecarts[0][1:], ("B", "A"))

    def test_regions_7_coupure(self):
        # Une route est-ouest traverse la limite x = 5 sans y être coupée.
        idx = index({1: ((0, 0), {}), 2: ((8, 0), {})},
                    [(10, [1, 2], {"highway": "secondary", "name": "Route 315"})])
        limite = [P(5, -10), P(5, 10)]
        c = regions.coupures(idx, [limite], [])
        self.assertEqual(c[0][0], "coupure à ajouter")
        route = {"type": "relation", "id": 70, "version": 1, "tags": {"type": "route"},
                 "members": [{"type": "way", "ref": 10, "role": ""}]}
        d = regions.decouper(idx, c, {70: route}, -100, -100)
        (nid, p), = d["noeuds"].items()
        self.assertAlmostEqual(p[0], LON + 0.005, places=7)      # sur la limite, sur la route
        self.assertEqual(d["modifies"][10], [1, nid])
        (wid, (ns, tags)), = d["chemins"].items()
        self.assertEqual(ns, [nid, 2])
        self.assertEqual(tags["name"], "Route 315")
        self.assertEqual([m["ref"] for m in d["relations"][70]], [10, wid])

    def test_regions_7_fusion(self):
        # Deux segments d'une rue, coupés au nœud 2 sur l'ancienne limite.
        def essai(n10, n11, tags10, tags11=None, rels=None):
            idx = index({1: ((0, 0), {}), 2: ((5, 0), {}), 3: ((10, 0), {})},
                        [(10, n10, tags10), (11, n11, tags11 or tags10)])
            rels = rels or {}
            d = {"modifies": {}, "relations": {}}
            regions.fusionner(idx, [(2, 10, 11)], d, {w: set(r) for w, r in rels.items()},
                              {70: {"members": [{"type": "way", "ref": 11, "role": ""}]}})
            return d
        rue = {"highway": "residential", "name": "Rue A"}
        d = essai([1, 2], [2, 3], rue)
        self.assertEqual((d["modifies"], d["supprimes"]), ({10: [1, 2, 3]}, [11]))
        d = essai([1, 2], [3, 2], rue)                          # sens contraire : retourné
        self.assertEqual(d["modifies"], {10: [1, 2, 3]})
        d = essai([1, 2], [3, 2], dict(rue, oneway="yes"))      # sens unique : refusé
        self.assertEqual(d["supprimes"], [])
        self.assertIn("sens unique", d["fusions"][0])
        d = essai([1, 2], [2, 3], rue, dict(rue, bridge="yes"))  # un pont : refusé
        self.assertIn("étiquettes différentes", d["fusions"][0])
        d = essai([1, 2], [2, 3], rue, rels={11: [70]})          # autobus d'un seul côté
        self.assertIn("relations différentes", d["fusions"][0])

    def test_regions_8_lien_lieu(self):
        idx = index({1: ((0, 0), {"place": "village", "name": "Duhamel"}),
                     2: ((0, 0), {"place": "village", "name": "Duhamel (village)"}),
                     3: ((0, 0), {})}, [])
        rel = lambda ref: {"tags": {"name": "Duhamel"},
                           "members": [{"type": "node", "ref": ref, "role": "label"}] if ref else []}
        self.assertEqual(regions.lien_lieu(rel(1), idx)[0], "lié")
        self.assertEqual(regions.lien_lieu(rel(2), idx)[0], "noms différents")
        self.assertEqual(regions.lien_lieu(rel(3), idx)[0], "lien sans place")
        self.assertEqual(regions.lien_lieu(rel(None), idx)[0], "sans lien")

    def test_regions_9_chemins_deja_conformes(self):
        # La limite commune existe déjà, exactement au tracé du MRNF.
        idx = index({1: ((10, 0), {}), 2: ((10, 10), {}), 3: ((9, 0), {}), 4: ((9, 10), {})},
                    [(600, [1, 2], {"boundary": "administrative", "admin_level": "8"}),
                     (601, [3, 4], {"boundary": "administrative", "admin_level": "8"})])
        rels = {"A": Rel(100, [600]), "B": Rel(200, [600, 601])}
        plan = regions.preparer(self.officiel, rels, None, idx)
        self.assertEqual([w for w, _, _ in plan["reutilises"]], [600])
        for code in ("A", "B"):
            self.assertIn({"type": "way", "ref": 600, "role": "outer"}, plan["membres"][code])
        self.assertEqual(plan["retires"], [601])        # décalé d'un millième : remplacé
        # Les chemins neufs se raccordent aux nœuds 1 et 2.
        bouts = {n for _, ids, _ in plan["chemins"] for n in (ids[0], ids[-1])}
        self.assertEqual(bouts, {1, 2})
        # Relancé avec tout déjà conforme : aucune relation à modifier.
        idx2 = index({n: (xy, {}) for n, xy in enumerate([(0, 0), (10, 0), (10, 10), (0, 10),
                                                          (20, 0), (20, 10)], 1)},
                     [(600, [2, 3], {"boundary": "administrative"}),
                      (602, [2, 1, 4, 3], {"boundary": "administrative"}),
                      (603, [2, 5, 6, 3], {"boundary": "administrative"})])
        rels2 = {"A": Rel(100, [600, 602]), "B": Rel(200, [600, 603])}
        plan = regions.preparer(self.officiel, rels2, None, idx2)
        self.assertEqual((plan["chemins"], plan["retires"], plan["modifiees"]), ([], [], []))

    def test_regions_10_voisine_hors_du_lot(self):
        # Lot : A seule. B, voisine, a son ancienne limite ouest à x = 11
        # (76 m de l'arc commun du MRNF, à x = 10).
        idx = index({1: ((11, 0), {}), 2: ((11, 5), {}), 3: ((11, 10), {}), 4: ((15, 10), {}),
                     5: ((20, 10), {}), 6: ((20, 0), {}), 7: ((0, 0), {}), 8: ((10, 0), {}),
                     9: ((10, 10), {}), 10: ((0, 10), {})},
                    [(700, [1, 2, 3, 4], {}), (701, [4, 5, 6, 1], {}),
                     (710, [8, 9, 10, 7, 8], {})])
        rels = {"A": Rel(100, [710])}
        b = Rel(200, [700, 701])
        b.tags = {"name": "B"}
        plan = regions.preparer({"A": self.officiel["A"]}, rels, None, idx,
                                {"B": self.officiel["B"]}, {"B": b}, lambda ws: {})
        commun = [w for w, ids, roles in plan["chemins"] if set(roles) == {"A", "B"}]
        self.assertEqual(len(commun), 1)
        membres = {m["ref"] for m in plan["membres"]["B"]}
        self.assertTrue(set(commun) <= membres)
        # 700 longe A en partie : raccourci à (11, 10)-(15, 10); 701 gardé.
        self.assertEqual(plan["voisines"]["modifies"], {700: [3, 4]})
        self.assertIn(701, membres)
        self.assertEqual(plan["voisines"]["liberes"], {1, 2})
        # Deux raccords, de l'arc commun (x = 10) à la partie gardée.
        raccords = [ids for w, ids, roles in plan["chemins"] if w in plan["provisoires"]]
        self.assertEqual(len(raccords), 2)
        self.assertEqual({n for r in raccords for n in r if n > 0}, {1, 3})
        self.assertIn("B", plan["modifiees"])


# Rues

class Rues(unittest.TestCase):
    def test_rues_1_nom_officiel(self):
        r = {"odonyme_recompose_normal": "Rue St-Julien (Papineauville)",
             "discriminant_odonyme": "Papineauville"}
        self.assertEqual(rqa.nom_rue(r), "Rue Saint-Julien")
        self.assertEqual(rqa.developper("Rue Hubert-St-Louis"), "Rue Hubert-Saint-Louis")
        self.assertEqual(rqa.developper("Rue Stewart"), "Rue Stewart")

    def test_rues_2_renommage_casse(self):
        tags = rues.etiquettes_renommage({"name": "Chemin de la Martinique"}, "Chemin de La Martinique")
        self.assertEqual(tags, {"name": "Chemin de La Martinique"})   # pas d'old_name

    def test_rues_2_abreviation_dans_osm(self):
        idx = rue_osm("Rue St. Andrew")
        r = rues.analyser([adr("5", "Rue Saint-Andrew")], idx)[0]
        self.assertEqual(r.statut, "à renommer")

    def test_rues_2_noms_conserves(self):
        # Renommage décidé à la main : l'ancien nom passe dans old_name,
        # sauf s'il est déjà gardé (alt_name).
        t = rues.etiquettes_renommage({"name": "Chemin Marconi"}, "Chemin du Marconi")
        self.assertEqual(t["old_name"], "Chemin Marconi")
        t = rues.etiquettes_renommage({"name": "Chemin du Gros-Cap"}, "Chemin de Gros-Cap",
                                      {"alt_name": "Chemin du Gros-Cap"})
        self.assertNotIn("old_name", t)
        t = rues.etiquettes_renommage({"name": "B", "old_name": "A"}, "C")
        self.assertEqual(t["old_name"], "A;B")

    def test_rues_3_autres_ecarts(self):
        idx = rue_osm("Chemin Cormier")
        r = rues.analyser([adr("5", "Chemin de la Promenade")], idx)[0]
        self.assertEqual(r.statut, "autre nom")
        self.assertEqual(r.renommer, [])

    def test_rues_4_adresses_apres_renommage(self):
        idx = rue_osm("Chemin du Tour du Lac")
        a = [adr("480")]
        avant = adresses.preparer(a, idx, {})
        self.assertEqual(avant.creer, [])
        plan, _ = rues.plan_renommage(rues.analyser(a, idx))
        rues.appliquer(idx, plan)
        apres = adresses.preparer(a, idx, {})
        self.assertEqual(len(apres.creer), 1)


# Adresses

class Adresses(unittest.TestCase):
    def test_adresses_1_logements_et_suffixes(self):
        groupe = adresses.regrouper([adr("329"), adr("329", unite="2"), adr("329", suffixe="1"),
                                     adr("120"), adr("120", suffixe="A"),
                                     adr("120", suffixe="B", dx=2)])     # à 77 m : distinct
        base, autres = groupe[("80135", "1", "329")]
        self.assertEqual(adresses.numeros("329", base, autres), ("329", "1;2"))
        base, autres = groupe[("80135", "1", "120")]
        self.assertEqual(adresses.numeros("120", base, autres), ("120;120A", None))
        base, autres = groupe[("80135", "1", "120B")]
        self.assertEqual(adresses.numeros("120B", base, autres), ("120B", None))
        p = adresses.preparer([adr("120"), adr("120", suffixe="B", dx=2)], rue_osm(), {})
        self.assertEqual(sorted(t["addr:housenumber"] for t, _ in p.creer), ["120", "120B"])
        # Des suffixes sans numéro de base : pas de « 300 » inventé.
        groupe = adresses.regrouper([adr("300", suffixe="A"), adr("300", suffixe="B")])
        self.assertEqual(adresses.numeros("300", *groupe[("80135", "1", "300")]), ("300A;300B", None))

    def test_adresses_1_logements_douteux(self):
        # Logement 2, ni lot ni matricule, sur une maison d'un seul logement
        # au rôle : écarté de addr:unit et listé pour le MRNF.
        maison = adr("250", logements="1")
        p = adresses.preparer([maison, adr("250", unite="2")], rue_osm(), {})
        (tags, _), = p.creer
        self.assertNotIn("addr:unit", tags)
        self.assertEqual([(x.logement, b.numero) for x, b in p.douteux], [("2", "250")])
        self.assertIn("logement(s) douteux écarté(s) : 2", p.rapport[0].detail)
        # Gardés : logement avec matricule ou lot, immeuble de 6 logements,
        # nombre de logements inconnu, ou règle désactivée.
        for base, unite, conf in [(maison, adr("250", unite="2", matricule="1" * 18), {}),
                                  (maison, adr("250", unite="2", lot="1234567"), {}),
                                  (adr("250", logements="6"), adr("250", unite="2"), {}),
                                  (adr("250"), adr("250", unite="2"), {}),
                                  (maison, adr("250", unite="2"), {"ecarter_logements_douteux": False})]:
            p = adresses.preparer([base, unite], rue_osm(), conf)
            self.assertEqual(p.creer[0][0].get("addr:unit"), "2")
            self.assertEqual(p.douteux, [])

    def test_adresses_2_terminees(self):
        p = adresses.preparer([adr("480", fin="20250101")], rue_osm(), {})
        self.assertEqual(p.creer, [])
        self.assertEqual(p.rapport, [])

    def test_adresses_3_exclusions(self):
        conf = {"exclure": [{"municipalite": "80135", "rue": "Chemin du Tour-du-Lac",
                             "numero": "131", "raison": "absent du rôle"}]}
        p = adresses.preparer([adr("131"), adr("131", rue="Chemin du Geai-Bleu")], rue_osm(), conf)
        self.assertEqual([l.statut for l in p.rapport if l.rue == "Chemin du Tour-du-Lac"], ["exclu"])
        with self.assertRaises(SystemExit):
            adresses.preparer([], rue_osm(), {"exclure": [{"municipalite": "1", "numero": "1"}]})

    def test_adresses_4_rue_dans_osm(self):
        p = adresses.preparer([adr("480")], rue_osm("Chemin des Pins"), {})
        self.assertEqual(p.creer, [])
        self.assertEqual(p.rapport[0].statut, "à revoir")

    def test_adresses_5_doublons(self):
        idx = rue_osm()
        idx.noeuds[50] = {"type": "node", "id": 50, "lon": P(1, 0.4)[0], "lat": P(1, 0.4)[1],
                          "version": 3, "tags": {"addr:housenumber": "480", "addr:street": "Ch. Tour du Lac"}}
        p = adresses.preparer([adr("480")], idx, {})
        self.assertEqual(p.creer, [])
        self.assertEqual(p.modifier[("node", 50)], {"addr:street": "Chemin du Tour-du-Lac",
                                                   "addr:postcode": "J0V 1G0"})

    def test_adresses_6_etiquettes(self):
        p = adresses.preparer([adr("480")], rue_osm(), {})
        (tags, _), = p.creer
        self.assertEqual(set(tags), {"addr:housenumber", "addr:street", "addr:postcode"})

    def _interpolation(self, ville="Duhamel", dy=0.5, partage=False):
        idx = rue_osm()
        bout = {"addr:street": "Chemin du Tour-du-Lac", "addr:city": ville,
                "source": "NRCan-CanVec-7.0", "addr:housenumber": "400"}
        idx.noeuds[60] = {"type": "node", "id": 60, "lon": P(0, dy)[0], "lat": P(0, dy)[1], "version": 1, "tags": bout}
        idx.noeuds[61] = {"type": "node", "id": 61, "lon": P(9, dy)[0], "lat": P(9, dy)[1], "version": 1, "tags": bout}
        idx.chemins[70] = {"type": "way", "id": 70, "nodes": [60, 61], "version": 1,
                           "tags": {"addr:interpolation": "even"}}
        if partage:
            idx.chemins[71] = {"type": "way", "id": 71, "nodes": [61, 3], "version": 1, "tags": {"highway": "service"}}
        return adresses.preparer([adr("480")], idx, {}).supprimer_chemins

    def test_adresses_7_interpolations(self):
        self.assertEqual(self._interpolation(), [70])
        self.assertEqual(self._interpolation(dy=20), [])            # à plus de 300 m des adresses
        self.assertEqual(self._interpolation(ville="Lac-Simon"), [])  # autre municipalité
        self.assertEqual(self._interpolation(partage=True), [])      # nœud partagé

    def test_adresses_8_positions_et_entree(self):
        idx = rue_osm()
        # Un bâtiment dont le côté sud passe à y = 1.
        for n, xy in {80: (1, 1), 81: (2, 1), 82: (2, 2), 83: (1, 2)}.items():
            idx.noeuds[n] = {"type": "node", "id": n, "lon": P(*xy)[0], "lat": P(*xy)[1], "tags": {}}
        idx.chemins[90] = {"type": "way", "id": 90, "nodes": [80, 81, 82, 83, 80], "tags": {"building": "house"}}

        class Portes:
            def __init__(self, p):
                self.p = p

            def position(self, a):
                if geo.distance(self.p, a.point) > 150:
                    return a.point, "RQA", "point portes ignoré"
                return self.p, "portes", "%.0f m du point RQA" % geo.distance(self.p, a.point)
        p = adresses.preparer([adr("480")], idx, {}, Portes(P(1.5, 1)))
        (tags, pt), = p.creer
        self.assertEqual(pt, P(1.5, 1))
        self.assertEqual(tags["entrance"], "home")
        p = adresses.preparer([adr("480", categorie="COMM")], idx, {}, Portes(P(1.5, 1)))
        self.assertEqual(p.creer[0][0]["entrance"], "shop")
        p = adresses.preparer([adr("480")], idx, {}, Portes(P(1.5, 0.5)))   # pas sur le contour
        self.assertNotIn("entrance", p.creer[0][0])
        p = adresses.preparer([adr("480")], idx, {}, Portes(P(1.5, 30)))    # trop loin
        self.assertEqual(p.rapport[0].position, "RQA")

    def test_adresses_8_portes_chaire_mobilite(self):
        # Le CSV du rôle corrigé par la Chaire Mobilité, relié au RQA par
        # id_provinc (code de municipalité et matricule).
        porte = P(1.5, 1)
        ewkb = struct.pack("<BII", 1, 0x20000001, 4326).hex() + struct.pack("<dd", *porte).hex()
        lignes = ["id_provinc,geog,geog_changed_entrance_aligned,geog_approximate,is_ignored",
                  "80135%s,%s,true,false,false" % ("1" * 18, ewkb),
                  "80135%s,SRID=4326;POINT(%r %r),t,f,f" % ("2" * 18, *P(3, 1)),
                  "80135%s,SRID=4326;POINT(%r %r),false,false,false" % ("3" * 18, *P(4, 1)),
                  "80135%s,SRID=4326;POINT(%r %r),true,true,false" % ("4" * 18, *P(5, 1)),
                  "80135%s,SRID=4326;POINT(%r %r),true,false,true" % ("5" * 18, *P(6, 1)),
                  "80135%s,SRID=4326;POINT(%r %r),true,false,false" % ("6" * 18, *P(30, 1))]
        with tempfile.NamedTemporaryFile("w", suffix=".csv", delete=False) as fh:
            fh.write("\n".join(lignes) + "\n")
        self.addCleanup(os.unlink, fh.name)
        pos = positions.Positions({"fichier": fh.name})
        self.assertEqual(pos.champ, "id_provinc")
        self.assertEqual(set(pos.points), {"80135" + c * 18 for c in "126"})
        self.assertEqual(pos.ecartes, {"pas sur la porte": 1, "approximatif": 1, "ignoré": 1})
        a = [adr("480", matricule="1" * 18), adr("490", dx=3, matricule="2" * 18),
             adr("492", dx=3, matricule="2" * 18), adr("500", dx=4, matricule="3" * 18),
             adr("600", dx=6, matricule="6" * 18), adr("600", dx=6, unite="2", matricule="6" * 18)]
        p = adresses.preparer(a, rue_osm(), {}, pos)
        source = {l.numero: l.position for l in p.rapport}
        self.assertEqual(source, {"480": "portes", "490": "RQA", "492": "RQA", "500": "RQA",
                                  "600": "portes"})
        # Porte vérifiée à près de 2 km du RQA : gardée et signalée; les
        # logements du même numéro la partagent.
        (l600,) = [l for l in p.rapport if l.numero == "600"]
        self.assertIn("vérifié, à 1855 m", l600.detail)
        self.assertEqual(l600.statut, "nouveau")
        self.assertIn(porte, [pt for _, pt in p.creer])


# Groupe de modifications

class Groupe(unittest.TestCase):
    def test_groupe(self):
        g = {"comment": "Adresses", "source": "RQA", "discussion": "https://exemple/t/1"}
        t = envoi.etiquettes(g, "reel")
        self.assertEqual(t["import"], "yes")
        self.assertEqual(t["discussion"], "https://exemple/t/1")
        self.assertIn("Discussion : https://exemple/t/1", t["comment"])
        with self.assertRaises(SystemExit):
            envoi.etiquettes({"comment": "A", "source": "B"}, "reel")
        self.assertNotIn("discussion", envoi.etiquettes({"comment": "A", "source": "B"}, "test"))


if __name__ == "__main__":
    unittest.main()
