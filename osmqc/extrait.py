# Lecture des données d'OSM dans un extrait local (.osm.pbf), au lieu
# de les demander à l'API d'OSM par tuiles : les règles d'usage de l'API
# découragent les téléchargements en masse.
#
# Extrait : par exemple celui du Québec chez Geofabrik,
#   https://download.geofabrik.de/north-america/canada/quebec-latest.osm.pbf
# mis à jour sur place avant chaque préparation :
#   pyosmium-up-to-date donnees/quebec-latest.osm.pbf
#
# Les objets sont rendus dans le même format que l'API JSON d'OSM
# (dictionnaires « type », « id », « version », « tags », « nodes »,
# « lat », « lon », « members »), pour que le reste du code ne voie pas
# la différence.

import datetime
import os
import tempfile
import xml.etree.ElementTree as ET

import osmium

TYPES = {"n": "node", "w": "way", "r": "relation"}


def chemin():
    return os.environ.get("OSMQC_PBF", os.path.join("donnees", "quebec-latest.osm.pbf"))


def date(pbf):
    """Date des données de l'extrait (horodatage de réplication), ou None."""
    r = osmium.io.Reader(pbf, osmium.osm.NOTHING)
    try:
        h = r.header()
        t = h.get("osmosis_replication_timestamp", "") or h.get("timestamp", "")
    finally:
        r.close()
    if not t:
        return None
    return datetime.datetime.fromisoformat(t.replace("Z", "+00:00"))


def verifier_fraicheur(pbf, jours=2):
    d = date(pbf)
    if d is None:
        print("Attention : date de l'extrait inconnue (%s)." % pbf)
        return None
    age = datetime.datetime.now(datetime.timezone.utc) - d
    print("Extrait OSM du %s." % d.strftime("%Y-%m-%d %H:%M UTC"))
    if age.days >= jours:
        print("Attention : extrait vieux de %d jours. Mettez-le à jour : "
              "pyosmium-up-to-date %s" % (age.days, pbf))
    return d


def tuiles(points, marge=0.003, pas=0.02):
    """Cases de « pas » degrés qui contiennent un des points, avec une
    marge en degrés."""
    res = set()
    for lon, lat in points:
        for dx in (-marge, 0, marge):
            for dy in (-marge, 0, marge):
                res.add((int((lon + dx) // pas), int((lat + dy) // pas)))
    return res


def _noeud(o):
    return {"type": "node", "id": o.id, "version": o.version,
            "lat": o.location.lat, "lon": o.location.lon, "tags": dict(o.tags)}


# Ce qui sert aux adresses et aux rues : nœuds d'adresse, et chemins de
# rue, de bâtiment, d'adresse ou d'interpolation. Le filtre est appliqué
# par pyosmium, avant Python : c'est ce qui rend la lecture rapide.
CLES_NOEUDS = ("addr:housenumber", "addr:street", "addr:interpolation")
CLES_CHEMINS = ("highway", "building", "addr:housenumber", "addr:interpolation")


def zone(pbf, cases, pas=0.02, cles_noeuds=CLES_NOEUDS, cles_chemins=CLES_CHEMINS):
    """Objets d'OSM autour d'une zone faite de cases (voir tuiles) :
    les nœuds qui portent une des cles_noeuds dans la zone, et les
    chemins qui portent une des cles_chemins dont un nœud est dans la
    zone, avec la position de tous leurs nœuds. Les nœuds sans étiquette
    n'ont pas de version (voir completer_versions)."""
    def dedans(lon, lat):
        return (int(lon // pas), int(lat // pas)) in cases

    noeuds = {}
    chemins = []
    fn = osmium.filter.KeyFilter(*cles_noeuds)
    fn.enable_for(osmium.osm.NODE)
    fw = osmium.filter.KeyFilter(*cles_chemins)
    fw.enable_for(osmium.osm.WAY)
    fp = (osmium.FileProcessor(pbf, osmium.osm.NODE | osmium.osm.WAY)
          .with_locations().with_filter(fn).with_filter(fw))
    for o in fp:
        if o.is_node():
            if o.location.valid() and dedans(o.location.lon, o.location.lat):
                noeuds[o.id] = _noeud(o)
            continue
        pts = [(n.ref, n.lon, n.lat) for n in o.nodes if n.location.valid()]
        if not any(dedans(lon, lat) for _, lon, lat in pts):
            continue
        chemins.append({"type": "way", "id": o.id, "version": o.version,
                        "nodes": [n.ref for n in o.nodes], "tags": dict(o.tags)})
        for ref, lon, lat in pts:
            if ref not in noeuds:
                noeuds[ref] = {"type": "node", "id": ref, "version": None,
                               "lat": lat, "lon": lon, "tags": {}}
    return list(noeuds.values()) + chemins


def chemins_nommes(pbf, noms):
    """Toutes les voies (highway) qui portent un de ces noms, avec la
    position de leurs nœuds, pour suivre une rue d'un bout à l'autre."""
    noms = set(noms)
    noeuds = {}
    chemins = []
    fw = osmium.filter.KeyFilter("highway")
    fw.enable_for(osmium.osm.WAY)
    fn = osmium.filter.KeyFilter("osmqc-aucun")   # les nœuds ne servent qu'aux positions
    fn.enable_for(osmium.osm.NODE)
    fp = (osmium.FileProcessor(pbf, osmium.osm.NODE | osmium.osm.WAY)
          .with_locations().with_filter(fn).with_filter(fw))
    for o in fp:
        if not o.is_way() or o.tags.get("name") not in noms:
            continue
        chemins.append({"type": "way", "id": o.id, "version": o.version,
                        "nodes": [n.ref for n in o.nodes], "tags": dict(o.tags)})
        for n in o.nodes:
            if n.location.valid() and n.ref not in noeuds:
                noeuds[n.ref] = {"type": "node", "id": n.ref, "version": None,
                                 "lat": n.lat, "lon": n.lon, "tags": {}}
    return list(noeuds.values()) + chemins


def completer_versions(pbf, elements, ids):
    """Remplit la version (et les étiquettes) des nœuds donnés, lus dans
    l'extrait. elements : liste d'objets, modifiée sur place."""
    manquants = {e["id"]: e for e in elements
                 if e["type"] == "node" and e["id"] in ids and e.get("version") is None}
    if not manquants:
        return
    for o in osmium.FileProcessor(pbf, osmium.osm.NODE).with_filter(osmium.filter.IdFilter(list(manquants))):
        manquants[o.id].update(_noeud(o))


def relations(pbf, ids):
    """Relations complètes : la relation, ses chemins avec leurs nœuds
    (position, version, étiquettes). Renvoie une liste d'objets."""
    rels = []
    chemins_voulus = set()
    for o in osmium.FileProcessor(pbf, osmium.osm.RELATION).with_filter(osmium.filter.IdFilter(list(ids))):
        membres = [{"type": TYPES[m.type], "ref": m.ref, "role": m.role} for m in o.members]
        rels.append({"type": "relation", "id": o.id, "version": o.version,
                     "members": membres, "tags": dict(o.tags)})
        chemins_voulus.update(m["ref"] for m in membres if m["type"] == "way")
    chemins = []
    noeuds_voulus = set()
    filtre = osmium.filter.IdFilter(list(chemins_voulus))
    filtre.enable_for(osmium.osm.WAY)
    for o in osmium.FileProcessor(pbf, osmium.osm.WAY).with_filter(filtre):
        chemins.append({"type": "way", "id": o.id, "version": o.version,
                        "nodes": [n.ref for n in o.nodes], "tags": dict(o.tags)})
        noeuds_voulus.update(n.ref for n in o.nodes)
    # Et les nœuds membres des relations (label, admin_centre).
    noeuds_voulus.update(m["ref"] for r in rels for m in r["members"] if m["type"] == "node")
    noeuds = [_noeud(o) for o in osmium.FileProcessor(pbf, osmium.osm.NODE)
              .with_filter(osmium.filter.IdFilter(list(noeuds_voulus)))]
    return rels + chemins + noeuds


def objets(pbf, genre, ids):
    """Objets donnés (node, way ou relation), lus dans l'extrait, au
    format de l'API : pour le mode hors ligne (voir osm.objets)."""
    ids = list(ids)
    if not ids:
        return []
    entite = {"node": osmium.osm.NODE, "way": osmium.osm.WAY, "relation": osmium.osm.RELATION}[genre]
    filtre = osmium.filter.IdFilter(ids)
    filtre.enable_for(entite)
    res = []
    for o in osmium.FileProcessor(pbf, entite).with_filter(filtre):
        if genre == "node":
            res.append(_noeud(o))
        elif genre == "way":
            res.append({"type": "way", "id": o.id, "version": o.version,
                        "nodes": [n.ref for n in o.nodes], "tags": dict(o.tags)})
        else:
            res.append({"type": "relation", "id": o.id, "version": o.version, "tags": dict(o.tags),
                        "members": [{"type": TYPES[m.type], "ref": m.ref, "role": m.role}
                                    for m in o.members]})
    return res


def appliquer(pbf, osc, sortie, resultat=None):
    """Écrit dans « sortie » l'extrait « pbf » auquel on applique le
    fichier osmChange « osc » (chemin ou élément XML), comme si OSM
    l'avait accepté. resultat : correspondances renvoyées par l'API après
    l'envoi, {(type, ancien id): (nouvel id, nouvelle version)}; sans
    elles (simulation, tests), les objets créés reçoivent des identifiants
    libres et les versions sont augmentées de 1. Renvoie les
    correspondances utilisées."""
    racine = ET.parse(osc).getroot() if isinstance(osc, str) else osc
    racine = ET.fromstring(ET.tostring(racine))
    if resultat is None:
        resultat = {}
        maxi = {"node": 0, "way": 0, "relation": 0}
        for o in osmium.FileProcessor(pbf):
            g = TYPES[o.type_str()]
            maxi[g] = max(maxi[g], o.id)
        for bloc in racine:
            for e in bloc:
                ident, version = int(e.get("id")), int(e.get("version") or 0)
                if ident < 0:
                    maxi[e.tag] += 1
                    resultat[(e.tag, ident)] = (maxi[e.tag], 1)
                else:
                    resultat[(e.tag, ident)] = (ident, version + 1)
    for bloc in racine:
        for e in bloc:
            nouveau, version = resultat[(e.tag, int(e.get("id")))]
            e.set("id", str(nouveau))
            e.set("version", str(version))
            if bloc.tag == "delete":
                e.set("visible", "false")
            for r in e.iter("nd"):
                r.set("ref", str(resultat.get(("node", int(r.get("ref"))), (int(r.get("ref")),))[0]))
            for m in e.iter("member"):
                ref = int(m.get("ref"))
                m.set("ref", str(resultat.get((m.get("type"), ref), (ref,))[0]))
    with tempfile.NamedTemporaryFile("wb", suffix=".osc", delete=False) as fh:
        fh.write(ET.tostring(racine, encoding="utf-8"))
    try:
        lecteur = osmium.io.Reader(pbf)
        entete = lecteur.header()
        if os.path.exists(sortie):
            os.unlink(sortie)
        ecrivain = osmium.io.Writer(sortie, entete)
        fusion = osmium.MergeInputReader()
        fusion.add_file(fh.name)
        fusion.apply_to_reader(lecteur, ecrivain, False)
        ecrivain.close()
        lecteur.close()
    finally:
        os.unlink(fh.name)
    return resultat


def relation_quebec(pbf):
    """Relation de la province de Québec (niveau 4) dans l'extrait, ou None."""
    for o in osmium.FileProcessor(pbf, osmium.osm.RELATION).with_filter(
            osmium.filter.TagFilter(("admin_level", "4"))):
        if o.tags.get("ISO3166-2") == "CA-QC" or o.tags.get("name") in ("Québec", "Quebec"):
            return o.id
    return None


def limites_admin(pbf):
    """Relations boundary=administrative qui ont un code ref:qc :
    {code: (id, nom, admin_level)}."""
    res = {}
    filtre = osmium.filter.TagFilter(("boundary", "administrative"))
    for o in osmium.FileProcessor(pbf, osmium.osm.RELATION).with_filter(filtre):
        code = o.tags.get("ref:qc")
        if code:
            res.setdefault(code, (o.id, o.tags.get("name", ""), o.tags.get("admin_level", "")))
    return res


def usages(pbf, nids, wids=()):
    """Usage d'objets dans tout l'extrait : pour chaque nœud donné, les
    chemins qui l'utilisent; les nœuds membres d'une relation; pour chaque
    chemin donné, les relations dont il est membre.
    Renvoie ({nœud: {chemins}}, {nœuds membres}, {chemin: {relations}})."""
    nids = set(nids)
    wids = set(wids)
    chemins = {n: set() for n in nids}
    membres = set()
    rels = {w: set() for w in wids}
    for o in osmium.FileProcessor(pbf, osmium.osm.WAY | osmium.osm.RELATION):
        if o.is_way():
            if nids:
                for n in o.nodes:
                    if n.ref in nids:
                        chemins[n.ref].add(o.id)
        else:
            for m in o.members:
                if m.type == "n" and m.ref in nids:
                    membres.add(m.ref)
                elif m.type == "w" and m.ref in wids:
                    rels[m.ref].add(o.id)
    return chemins, membres, rels
