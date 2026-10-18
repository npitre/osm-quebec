# Lecture des données d'OpenStreetMap par l'API 0.6 (lecture seule,
# sans authentification).

import json
import os
import time
import urllib.error
import urllib.request

API = "https://api.openstreetmap.org/api/0.6"
AGENT = "osmqc (https://github.com/npitre/osm-quebec)"


def lire(url, essais=4):
    if hors_ligne():
        raise RuntimeError("mode hors ligne : %s n'est pas demandé à l'API" % url)
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    for i in range(essais):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (400, 404, 410):
                raise
            err = e
        except OSError as e:
            err = e
        time.sleep(5 * (i + 1))
    raise err


def carte(ouest, sud, est, nord):
    """Tous les objets d'un rectangle. Un rectangle trop chargé (plus
    de 50 000 nœuds) est refusé par l'API : on le coupe en quatre."""
    url = "%s/map.json?bbox=%.6f,%.6f,%.6f,%.6f" % (API, ouest, sud, est, nord)
    try:
        return json.loads(lire(url))["elements"]
    except urllib.error.HTTPError as e:
        if e.code != 400:
            raise
    mx, my = (ouest + est) / 2, (sud + nord) / 2
    elems = []
    for o, s, e_, n in ((ouest, sud, mx, my), (mx, sud, est, my),
                        (ouest, my, mx, nord), (mx, my, est, nord)):
        elems += carte(o, s, e_, n)
    return elems


def carte_autour(points, marge=0.003, pas=0.05):
    """Télécharge, par tuiles de « pas » degrés, seulement les tuiles qui
    contiennent un des points (avec une marge en degrés). Renvoie les
    objets sans doublons."""
    tuiles = set()
    for lon, lat in points:
        for dx in (-marge, 0, marge):
            for dy in (-marge, 0, marge):
                tuiles.add((int((lon + dx) // pas), int((lat + dy) // pas)))
    vus = {}
    for i, (tx, ty) in enumerate(sorted(tuiles), 1):
        print("  tuile %d/%d" % (i, len(tuiles)), flush=True)
        for e in carte(tx * pas, ty * pas, (tx + 1) * pas, (ty + 1) * pas):
            vus[(e["type"], e["id"])] = e
    return list(vus.values())


def hors_ligne():
    """Mode hors ligne (OSMQC_HORS_LIGNE=1) : l'API n'est jamais
    appelée, l'extrait local fait foi. Sert aux tests de bout en bout."""
    return bool(os.environ.get("OSMQC_HORS_LIGNE"))


def objets(genre, ids):
    """Version actuelle d'objets (node, way, relation), par lots de 100.
    Hors ligne, lue dans l'extrait local."""
    ids = list(ids)
    if hors_ligne():
        from . import extrait
        return extrait.objets(extrait.chemin(), genre, ids)
    res = []
    for i in range(0, len(ids), 100):
        url = "%s/%ss.json?%ss=%s" % (API, genre, genre, ",".join(map(str, ids[i:i + 100])))
        res += json.loads(lire(url))["elements"]
    return res


def complet(genre, ident):
    """Un objet avec tous ses membres et nœuds (way ou relation)."""
    return json.loads(lire("%s/%s/%d/full.json" % (API, genre, ident)))["elements"]


class Index:
    """Accès rapide aux objets téléchargés."""

    def __init__(self, elements):
        self.noeuds = {e["id"]: e for e in elements if e["type"] == "node"}
        self.chemins = {e["id"]: e for e in elements if e["type"] == "way"}
        self.relations = {e["id"]: e for e in elements if e["type"] == "relation"}

    def point(self, nid):
        n = self.noeuds[nid]
        return (n["lon"], n["lat"])

    def ligne(self, wid):
        return [self.point(n) for n in self.chemins[wid]["nodes"] if n in self.noeuds]

    def tous(self):
        yield from self.noeuds.values()
        yield from self.chemins.values()
        yield from self.relations.values()
