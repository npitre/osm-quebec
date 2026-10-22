# Géométrie élémentaire en coordonnées géographiques (lon, lat).
#
# Les distances utilisent une projection locale équirectangulaire,
# largement suffisante à l'échelle d'une rue ou d'une municipalité.

import math
import struct

R_TERRE = 6371008.8


def distance(a, b):
    """Distance en mètres entre deux points (lon, lat)."""
    lat = math.radians((a[1] + b[1]) / 2)
    dx = math.radians(b[0] - a[0]) * math.cos(lat)
    dy = math.radians(b[1] - a[1])
    return R_TERRE * math.hypot(dx, dy)


def distance_segment(p, a, b):
    """Distance en mètres du point p au segment [a, b]."""
    kx = math.radians(1) * R_TERRE * math.cos(math.radians(p[1]))
    ky = math.radians(1) * R_TERRE
    px, py = p[0] * kx, p[1] * ky
    ax, ay = a[0] * kx, a[1] * ky
    bx, by = b[0] * kx, b[1] * ky
    dx, dy = bx - ax, by - ay
    t = ((px - ax) * dx + (py - ay) * dy) / ((dx * dx + dy * dy) or 1)
    t = max(0.0, min(1.0, t))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def distance_ligne(p, ligne):
    """Distance en mètres du point p à une polyligne."""
    return min(distance_segment(p, a, b) for a, b in zip(ligne, ligne[1:]))


def boite(points):
    """Rectangle englobant (ouest, sud, est, nord)."""
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return (min(xs), min(ys), max(xs), max(ys)) if xs else (0, 0, -1, -1)


def dans_boite(p, b):
    return b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3]


def dedans(p, anneaux):
    """Vrai si p est dans le polygone formé par les anneaux (règle de
    parité : les anneaux intérieurs font des trous)."""
    x, y = p
    c = False
    for anneau in anneaux:
        for (x1, y1), (x2, y2) in zip(anneau, anneau[1:]):
            if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
                c = not c
    return c


def assembler(segments):
    """Assemble des segments (listes de clés de nœuds) en anneaux, en
    les retournant au besoin. Renvoie (anneaux, nombre d'anneaux restés
    ouverts)."""
    restes = [list(s) for s in segments]
    anneaux = []
    ouverts = 0
    while restes:
        cur = restes.pop()
        trouve = True
        while cur[0] != cur[-1] and trouve:
            trouve = False
            for i, s in enumerate(restes):
                if s[0] == cur[-1]:
                    cur += s[1:]
                elif s[-1] == cur[-1]:
                    cur += s[::-1][1:]
                elif s[-1] == cur[0]:
                    cur = s[:-1] + cur
                elif s[0] == cur[0]:
                    cur = s[::-1][:-1] + cur
                else:
                    continue
                restes.pop(i)
                trouve = True
                break
        if cur[0] != cur[-1]:
            ouverts += 1
        anneaux.append(cur)
    return anneaux, ouverts


def wkb_gpkg(blob):
    """Décode la géométrie d'un GeoPackage. Renvoie une liste de
    polygones, chacun une liste d'anneaux de points (lon, lat). Seuls
    les polygones et multipolygones sont gérés."""
    enveloppe = (blob[3] >> 1) & 7
    debut = 8 + [0, 32, 48, 48, 64][enveloppe]
    polys, _ = _wkb(blob, debut)
    return polys


def wkb_gpkg_lignes(blob):
    """Décode une géométrie linéaire d'un GeoPackage (LineString ou
    MultiLineString). Renvoie une liste de polylignes (lon, lat)."""
    enveloppe = (blob[3] >> 1) & 7
    return _wkb_lignes(blob, 8 + [0, 32, 48, 48, 64][enveloppe])[0]


def _wkb_lignes(b, o):
    ordre = "<" if b[o] == 1 else ">"
    genre = struct.unpack(ordre + "I", b[o + 1:o + 5])[0] % 1000
    o += 5
    n = struct.unpack(ordre + "I", b[o:o + 4])[0]
    o += 4
    if genre == 2:
        return [[struct.unpack(ordre + "dd", b[o + 16 * i:o + 16 * i + 16]) for i in range(n)]], o + 16 * n
    if genre == 5:
        res = []
        for _ in range(n):
            l, o = _wkb_lignes(b, o)
            res += l
        return res, o
    raise ValueError("géométrie WKB de type %d non gérée" % genre)


def _wkb(b, o):
    ordre = "<" if b[o] == 1 else ">"
    genre = struct.unpack(ordre + "I", b[o + 1:o + 5])[0] % 1000
    o += 5
    if genre == 3:
        nb = struct.unpack(ordre + "I", b[o:o + 4])[0]
        o += 4
        anneaux = []
        for _ in range(nb):
            n = struct.unpack(ordre + "I", b[o:o + 4])[0]
            o += 4
            anneaux.append([struct.unpack(ordre + "dd", b[o + 16 * i:o + 16 * i + 16])
                            for i in range(n)])
            o += 16 * n
        return [anneaux], o
    if genre == 6:
        nb = struct.unpack(ordre + "I", b[o:o + 4])[0]
        o += 4
        polys = []
        for _ in range(nb):
            p, o = _wkb(b, o)
            polys += p
        return polys, o
    raise ValueError("géométrie WKB de type %d non gérée" % genre)


def intersection(a, b, c, d):
    """Point d'intersection des segments [a, b] et [c, d], ou None."""
    den = (b[0] - a[0]) * (d[1] - c[1]) - (b[1] - a[1]) * (d[0] - c[0])
    if den == 0:
        return None
    t = ((c[0] - a[0]) * (d[1] - c[1]) - (c[1] - a[1]) * (d[0] - c[0])) / den
    u = ((c[0] - a[0]) * (b[1] - a[1]) - (c[1] - a[1]) * (b[0] - a[0])) / den
    if 0 <= t <= 1 and 0 <= u <= 1:
        return (a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1]))
    return None


def croisements(ligne, autre):
    """Points où deux polylignes se croisent (recherche par rectangles
    englobants des segments)."""
    res = []
    bo = boite(autre)
    for a, b in zip(ligne, ligne[1:]):
        if max(a[0], b[0]) < bo[0] or min(a[0], b[0]) > bo[2] or \
           max(a[1], b[1]) < bo[1] or min(a[1], b[1]) > bo[3]:
            continue
        for c, d in zip(autre, autre[1:]):
            p = intersection(a, b, c, d)
            if p:
                res.append(p)
    return res


class Grille:
    """Index de segments par cases de « pas » degrés, pour trouver vite
    les croisements et les segments proches d'un point."""

    def __init__(self, lignes, pas=0.01):
        self.pas = pas
        self.cases = {}
        for ligne in lignes:
            for a, b in zip(ligne, ligne[1:]):
                for c in self._cases(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])):
                    self.cases.setdefault(c, []).append((a, b))

    def _cases(self, o, s, e, n):
        for i in range(int(o // self.pas), int(e // self.pas) + 1):
            for j in range(int(s // self.pas), int(n // self.pas) + 1):
                yield (i, j)

    def croisements(self, ligne):
        res = set()
        for a, b in zip(ligne, ligne[1:]):
            for c in self._cases(min(a[0], b[0]), min(a[1], b[1]), max(a[0], b[0]), max(a[1], b[1])):
                for s in self.cases.get(c, ()):
                    p = intersection(a, b, s[0], s[1])
                    if p:
                        res.add((round(p[0], 7), round(p[1], 7)))
        return sorted(res)

    def distance(self, p, rayon_deg=0.003):
        """Distance en mètres au segment le plus proche dans le rayon
        (None s'il n'y en a pas)."""
        meilleur = None
        for c in self._cases(p[0] - rayon_deg, p[1] - rayon_deg, p[0] + rayon_deg, p[1] + rayon_deg):
            for a, b in self.cases.get(c, ()):
                d = distance_segment(p, a, b)
                if meilleur is None or d < meilleur:
                    meilleur = d
        return meilleur
