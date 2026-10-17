# Positions plus précises des adresses, par exemple les portes d'entrée
# placées à la main sur l'imagerie (données de la Chaire Mobilité). Deux
# formats :
#
#   GeoJSON de points (.geojson, .json), relié au RQA par une propriété;
#   CSV du rôle d'évaluation corrigé par la Chaire Mobilité (.csv), celui
#   que charge references/update_property_registry_geometry.sql de son
#   outil address_integrator : id_provinc, geog,
#   geog_changed_entrance_aligned, geog_approximate, is_ignored, etc.
#
# Chaque point est relié à une adresse du RQA par une clé, au choix :
#   matricule   matricule de l'unité d'évaluation (rôle foncier)
#   id_provinc  code de municipalité (5 chiffres) suivi du matricule : la
#               clé du rôle d'évaluation, celle du CSV
#   lot         numéro de lot
#   ident       identifiant_unique_adresse du RQA
#   adresse     « numéro|nom de rue|code municipalité »
# Sans correspondance, ou si une même unité d'évaluation porte plusieurs
# numéros (une porte ne dit pas lequel), on garde le point du MRNF. Un
# point d'un GeoJSON trop loin de celui du RQA (ce qui trahit une erreur
# d'appariement) est aussi ignoré. Une porte du CSV, elle, a été vérifiée
# à la main : elle est gardée même loin du RQA (dont les points sont
# parfois décalés d'un terrain), avec une remarque dans le rapport.
# Les unités d'un même numéro (101-1234, 102-1234) partagent la porte.

import csv
import json
import re
import struct
from collections import defaultdict

from . import geo
from .adresses import cle_nom


def cle_rqa(a, champ):
    if champ == "matricule":
        return a.matricule
    if champ == "id_provinc":
        return a.municipalite.zfill(5) + a.matricule if a.matricule else ""
    if champ == "lot":
        return a.lot.split(",")[0] if a.lot else ""
    if champ == "ident":
        return a.ident
    if champ == "adresse":
        return "%s|%s|%s" % (a.numero, cle_nom(a.rue), a.municipalite)
    raise ValueError("clé inconnue : %s" % champ)


def point_texte(s):
    """Point (lon, lat) d'une géométrie PostGIS sous forme de texte :
    (E)WKT « SRID=4326;POINT(-61.8 47.4) » ou (E)WKB en hexadécimal."""
    s = (s or "").strip()
    m = re.match(r"(?i)(?:SRID=\d+;)?POINT\s*\(\s*(\S+)\s+(\S+)\s*\)$", s)
    if m:
        return float(m.group(1)), float(m.group(2))
    if not re.fullmatch(r"[0-9A-Fa-f]+", s):
        raise ValueError("géométrie illisible : %r" % s[:40])
    b = bytes.fromhex(s)
    ordre = "<" if b[0] == 1 else ">"
    genre = struct.unpack(ordre + "I", b[1:5])[0]
    if (genre & 0x0FFFFFFF) % 1000 != 1:
        raise ValueError("géométrie WKB qui n'est pas un point")
    o = 5 + (4 if genre & 0x20000000 else 0)       # SRID de l'EWKB
    return struct.unpack(ordre + "dd", b[o:o + 16])


def vrai(v):
    return str(v).strip().lower() in ("t", "true", "1", "oui", "yes")


def lire_csv(fichier):
    """Points du CSV de la Chaire Mobilité : {id_provinc: point}, et le
    nombre de points écartés par raison. Seuls les points placés sur la
    porte (geog_changed_entrance_aligned), ni approximatifs ni ignorés,
    sont gardés."""
    points, ecartes = {}, defaultdict(int)
    with open(fichier, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            cle = (r.get("id_provinc") or "").strip()
            if not cle:
                continue
            if vrai(r.get("is_ignored", "")):
                ecartes["ignoré"] += 1
            elif not vrai(r.get("geog_changed_entrance_aligned", "")):
                ecartes["pas sur la porte"] += 1
            elif vrai(r.get("geog_approximate", "")):
                ecartes["approximatif"] += 1
            elif r.get("geog"):
                points[cle] = point_texte(r["geog"])
            elif r.get("longitude") and r.get("latitude"):
                points[cle] = (float(r["longitude"]), float(r["latitude"]))
    return points, dict(ecartes)


def lire_geojson(fichier, prop):
    points = {}
    with open(fichier, encoding="utf-8") as fh:
        for f in json.load(fh)["features"]:
            g = f.get("geometry") or {}
            if g.get("type") != "Point":
                continue
            v = f.get("properties", {}).get(prop)
            if v not in (None, ""):
                points.setdefault(str(v).strip(), tuple(g["coordinates"][:2]))
    return points


class Positions:
    def __init__(self, conf):
        """conf : section [positions] du lieu (fichier, propriete, cle_rqa,
        ecart_max_m, nom). Pour un CSV, la clé est id_provinc par défaut,
        et ses portes vérifiées ne sont pas soumises à ecart_max_m."""
        en_csv = conf["fichier"].lower().endswith(".csv")
        self.champ = conf.get("cle_rqa", "id_provinc" if en_csv else "matricule")
        self.ecart_max = conf.get("ecart_max_m", 150)
        self.verifiees = en_csv
        self.nom = conf.get("nom", "portes")
        self.ecartes = {}
        if en_csv:
            self.points, self.ecartes = lire_csv(conf["fichier"])
        else:
            self.points = lire_geojson(conf["fichier"], conf["propriete"])
        self.partages = {}

    def associer(self, adresses):
        """Repère les unités d'évaluation qui portent plusieurs numéros."""
        numeros = defaultdict(set)
        for a in adresses:
            cle = cle_rqa(a, self.champ)
            if cle in self.points:
                numeros[cle].add((a.rue, a.numero))
        self.partages = {c: len(n) for c, n in numeros.items() if len(n) > 1}

    def position(self, a):
        """(point, source, remarque) pour une adresse du RQA."""
        cle = cle_rqa(a, self.champ)
        p = self.points.get(cle) if cle else None
        if p is None:
            return a.point, "RQA", ""
        if cle in self.partages:
            return a.point, "RQA", "point %s ignoré : %d numéros pour la même unité d'évaluation" % (
                self.nom, self.partages[cle])
        d = geo.distance(p, a.point)
        if d > self.ecart_max and self.verifiees:
            return p, self.nom, "point %s vérifié, à %.0f m du point RQA" % (self.nom, d)
        if d > self.ecart_max:
            return a.point, "RQA", "point %s ignoré, à %.0f m du RQA" % (self.nom, d)
        return p, self.nom, "%.0f m du point RQA" % d if d >= 1 else ""


class Aucune:
    """Pas de source de positions : toujours le point du MRNF."""

    def position(self, a):
        return a.point, "RQA", ""
