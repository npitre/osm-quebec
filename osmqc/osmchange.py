# Écriture du plan : fichier osmChange pour l'envoi, GeoJSON et CSV pour
# la révision.

import csv
import json
import xml.etree.ElementTree as ET
from dataclasses import asdict

from .regions import cles_membres


def element_xml(e, tags):
    """Objet OSM (dict de l'API JSON) en XML, avec ses étiquettes mises à jour."""
    el = ET.Element(e["type"], id=str(e["id"]), version=str(e["version"]))
    if e["type"] == "node":
        el.set("lat", "%.7f" % e["lat"])
        el.set("lon", "%.7f" % e["lon"])
    t = dict(e.get("tags", {}))
    t.update(tags)
    if e["type"] == "way":
        for n in e["nodes"]:
            ET.SubElement(el, "nd", ref=str(n))
    if e["type"] == "relation":
        for m in e["members"]:
            ET.SubElement(el, "member", type=m["type"], ref=str(m["ref"]), role=m["role"])
    for k in sorted(t):
        ET.SubElement(el, "tag", k=k, v=t[k])
    return el


def osc(plan, actuels, index):
    """actuels : versions fraîches des objets à modifier, {(type, id): objet}."""
    racine = ET.Element("osmChange", version="0.6", generator="osmqc")
    cree = ET.SubElement(racine, "create")
    for i, (tags, (lon, lat)) in enumerate(plan.creer, 1):
        n = ET.SubElement(cree, "node", id=str(-i), version="0",
                          lat="%.7f" % lat, lon="%.7f" % lon)
        for k, v in tags.items():
            ET.SubElement(n, "tag", k=k, v=v)
    modif = ET.SubElement(racine, "modify")
    for cle, tags in sorted(plan.modifier.items()):
        modif.append(element_xml(actuels[cle], tags))
    supp = ET.SubElement(racine, "delete")
    # Les chemins d'abord, puis leurs nœuds.
    for wid in plan.supprimer_chemins:
        ET.SubElement(supp, "way", id=str(wid), version=str(index.chemins[wid]["version"]))
    for nid in plan.supprimer_noeuds:
        n = index.noeuds[nid]
        ET.SubElement(supp, "node", id=str(nid), version=str(n["version"]),
                      lat="%.7f" % n["lat"], lon="%.7f" % n["lon"])
    ET.indent(racine)
    return racine


def ecrire_osc(racine, chemin):
    with open(chemin, "wb") as fh:
        ET.ElementTree(racine).write(fh, encoding="utf-8", xml_declaration=True)
        fh.write(b"\n")


def geojson(plan, actuels, index):
    """Une entité par ligne du rapport, plus les objets modifiés et les
    interpolations supprimées, pour voir l'import sur une carte."""
    f = []
    for l in plan.rapport:
        f.append({"type": "Feature",
                  "geometry": {"type": "Point", "coordinates": [l.lon, l.lat]},
                  "properties": asdict(l)})
    for (genre, ident), tags in sorted(plan.modifier.items()):
        e = actuels[(genre, ident)]
        if genre == "node":
            g = {"type": "Point", "coordinates": [e["lon"], e["lat"]]}
        else:
            g = {"type": "LineString", "coordinates": [list(p) for p in index.ligne(ident)]}
        f.append({"type": "Feature", "geometry": g, "properties": {
            "statut": "modifié", "objet": "%s/%d" % (genre, ident),
            "changements": tags, "raisons": plan.raisons.get((genre, ident), [])}})
    for wid in plan.supprimer_chemins:
        f.append({"type": "Feature",
                  "geometry": {"type": "LineString", "coordinates": [list(p) for p in index.ligne(wid)]},
                  "properties": {"statut": "supprimé", "objet": "way/%d" % wid,
                                 "etiquettes": index.chemins[wid].get("tags", {})}})
    return {"type": "FeatureCollection", "features": f}


def ecrire_geojson(donnees, chemin):
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(donnees, fh, ensure_ascii=False, indent=1)
        fh.write("\n")


def ecrire_rapport(plan, chemin):
    with open(chemin, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["municipalite", "rue", "numero", "code_postal", "lat", "lon",
                    "qualite", "position", "statut", "detail"])
        for l in plan.rapport:
            w.writerow([l.municipalite, l.rue, l.numero, l.code_postal, "%.7f" % l.lat,
                        "%.7f" % l.lon, l.qualite, l.position, l.statut, l.detail])


def osc_regions(plan, actuelles, supp_chemins, supp_noeuds, index, admin_level="8"):
    """osmChange du remplacement des limites. actuelles : versions
    fraîches des relations, {code: objet}; index : objets OSM pour les
    versions des chemins et nœuds supprimés."""
    racine = ET.Element("osmChange", version="0.6", generator="osmqc")
    cree = ET.SubElement(racine, "create")
    for (lon, lat), nid in sorted(plan["noeuds"].items(), key=lambda kv: -kv[1]):
        ET.SubElement(cree, "node", id=str(nid), version="0", lat="%.7f" % lat, lon="%.7f" % lon)
    for wid, ids, roles in plan["chemins"]:
        w = ET.SubElement(cree, "way", id=str(wid), version="0")
        for n in ids:
            ET.SubElement(w, "nd", ref=str(n))
        tags = {"admin_level": admin_level, "boundary": "administrative"}
        tags.update(plan.get("etiquettes", {}).get(wid, {}))
        for k in sorted(tags):
            ET.SubElement(w, "tag", k=k, v=tags[k])
    # Chemins de limite des voisines coupés en deux : morceaux neufs.
    v = plan.get("voisines") or {}
    for wid, (ids, tags) in sorted(v.get("neufs", {}).items(), reverse=True):
        w = ET.SubElement(cree, "way", id=str(wid), version="0")
        for n in ids:
            ET.SubElement(w, "nd", ref=str(n))
        for k in sorted(tags):
            ET.SubElement(w, "tag", k=k, v=tags[k])
    # Routes coupées aux limites : nœuds et morceaux neufs.
    d = plan.get("decoupe") or {}
    for nid, (lon, lat) in sorted(d.get("noeuds", {}).items(), reverse=True):
        ET.SubElement(cree, "node", id=str(nid), version="0", lat="%.7f" % lat, lon="%.7f" % lon)
    for wid, (ids, tags) in sorted(d.get("chemins", {}).items(), reverse=True):
        w = ET.SubElement(cree, "way", id=str(wid), version="0")
        for n in ids:
            ET.SubElement(w, "nd", ref=str(n))
        for k in sorted(tags):
            ET.SubElement(w, "tag", k=k, v=tags[k])
    modif = ET.SubElement(racine, "modify")
    # Les étiquettes des relations ne changent jamais : seulement leurs
    # membres. Une relation dont les membres ne changent pas (à l'ordre
    # près) n'est pas envoyée.
    for code, rel in sorted(actuelles.items()):
        if cles_membres(rel["members"]) == cles_membres(plan["membres"][code]):
            continue
        r = dict(rel)
        r["members"] = plan["membres"][code]
        modif.append(element_xml(r, {}))
    for wid, ids in sorted(v.get("modifies", {}).items()):
        w = dict(v["actuels"][wid])
        w["nodes"] = ids
        modif.append(element_xml(w, {}))
    for rid, membres in sorted(v.get("membres_relations", {}).items()):
        r = dict(v["rels_actuelles"][rid])
        r["members"] = membres
        modif.append(element_xml(r, {}))
    for wid, ids in sorted(d.get("modifies", {}).items()):
        w = dict(d["actuels"][wid])
        w["nodes"] = ids
        modif.append(element_xml(w, {}))
    for rid, membres in sorted(d.get("relations", {}).items()):
        r = dict(d["rels_actuelles"][rid])
        r["members"] = membres
        modif.append(element_xml(r, {}))
    supp = ET.SubElement(racine, "delete")
    for wid in supp_chemins:
        ET.SubElement(supp, "way", id=str(wid), version=str(index.chemins[wid]["version"]))
    for nid in supp_noeuds:
        n = index.noeuds[nid]
        ET.SubElement(supp, "node", id=str(nid), version=str(n["version"]),
                      lat="%.7f" % n["lat"], lon="%.7f" % n["lon"])
    # Garde-fou : jamais deux fois le même objet dans un envoi.
    vus = set()
    for bloc in racine:
        for e in bloc:
            cle = (e.tag, e.get("id"))
            if cle in vus:
                raise ValueError("%s %s deux fois dans le fichier d'envoi" % cle)
            vus.add(cle)
    # Ni aucun objet supprimé encore utilisé par un autre.
    supprimes = {(e.tag, e.get("id")) for e in supp}
    for bloc in (cree, modif):
        for e in bloc:
            refs = [("node", n.get("ref")) for n in e.iter("nd")]
            refs += [(m.get("type"), m.get("ref")) for m in e.iter("member")]
            for r in refs:
                if r in supprimes:
                    raise ValueError("%s %s supprimé mais encore utilisé par %s %s" % (r + (e.tag, e.get("id"))))
    ET.indent(racine)
    return racine
