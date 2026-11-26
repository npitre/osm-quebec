# Comparaison des adresses du RQA avec celles déjà dans OSM, pour un lieu
# où quelqu'un a déjà importé ou validé les adresses à la main (les Îles,
# par Pierre-Léo Bourbonnais). Ne prépare rien à envoyer : écrit un
# rapport des différences, rapports/LIEU/comparaison.md, avec sa carte
# rapports/LIEU/comparaison.geojson.
#
# Il reprend les étapes de « adresses preparer » sur donnees/LIEU/osm.json
# (« adresses osm ») et donnees/LIEU/rqa.csv (« adresses extraire »).
#
# Usage, depuis la racine du dépôt :
#   python3 outils/comparer.py lieux/LIEU.toml

import json
import os
import sys
import tomllib
from collections import Counter, defaultdict

DEPOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, DEPOT)

from osmqc import adresses, geo, osm, rqa, rues  # noqa: E402

RUE_PROCHE_M = 300      # rue d'OSM cherchée autour d'une adresse « à revoir »


def appliquer(index, c):
    for m in c.get("modifier", []):
        objets = {"node": index.noeuds, "way": index.chemins, "relation": index.relations}[m["type"]]
        if m["id"] in objets:
            objets[m["id"]].setdefault("tags", {}).update(m["tags"])


def carte(lon, lat):
    return "[carte](https://www.openstreetmap.org/?mlat=%.6f&mlon=%.6f#map=19/%.6f/%.6f)" % (lat, lon, lat, lon)


def objet(genre, ident):
    return "[%s/%d](https://www.openstreetmap.org/%s/%d)" % (genre, ident, genre, ident)


def objet_du_detail(detail):
    """(genre, id) de l'objet OSM retrouvé, d'après le détail du rapport
    (« déjà dans OSM (node 123) », « node 123 corrigé (...) »)."""
    for mot in ("node", "way", "relation"):
        i = detail.find(mot + " ")
        if i >= 0:
            chiffres = ""
            for c in detail[i + len(mot) + 1:]:
                if not c.isdigit():
                    break
                chiffres += c
            if chiffres:
                return mot, int(chiffres)
    return None


def cellule(v):
    return (v or "").replace("|", "\\|")


def ordre(l):
    return (l.rue, adresses._ordre(l.numero))


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage : python3 outils/comparer.py lieux/LIEU.toml")
    chemin = sys.argv[1]
    lieu = os.path.splitext(os.path.basename(chemin))[0]
    with open(chemin, "rb") as fh:
        conf = tomllib.load(fh)
    with open(os.path.join("donnees", lieu, "osm.json")) as fh:
        index = osm.Index(json.load(fh))
    ad = rqa.lire_extrait(os.path.join("donnees", lieu, "rqa.csv"))
    with open(os.path.join("donnees", lieu, "rqa.csv"), encoding="utf-8") as fh:
        version = "AQ" + next(iter(__import__("csv").DictReader(fh)))["date_diffusion_version"]
    appliquer(index, conf.get("rues", {}))
    plan_rues, _ = rues.plan_renommage(rues.analyser(ad, index))
    rues.appliquer(index, plan_rues)
    ca = conf.get("adresses", {})
    appliquer(index, ca)
    plan = adresses.preparer(ad, index, ca, None)

    # Deux rues du même nom (dans deux localités d'une municipalité
    # fusionnée) donnent la même clé : on garde toutes les adresses, et
    # on prend celle au point de la ligne du rapport.
    par_cle = defaultdict(list)
    for (mun, odo, num), (a, autres) in adresses.regrouper(ad).items():
        par_cle[(a.municipalite, a.rue, num)].append((a, autres))

    def groupe(l):
        lst = par_cle.get((l.municipalite, l.rue, l.numero))
        if not lst:
            return None, []
        return min(lst, key=lambda x: geo.distance(x[0].point, (l.lon, l.lat)))

    def tags_de(ref):
        genre, ident = ref
        o = {"node": index.noeuds, "way": index.chemins, "relation": index.relations}[genre].get(ident)
        return (o or {}).get("tags", {})

    # Adresses retrouvées dans OSM : localité et code postal.
    retrouvees = []      # (Ligne, (genre, id), tags, Adresse)
    for l in plan.rapport:
        if l.statut not in ("existant", "corrigé"):
            continue
        ref = objet_du_detail(l.detail)
        if not ref:
            continue
        a = groupe(l)[0]
        retrouvees.append((l, ref, tags_de(ref), a))
    # addr:city : sur une rue sans discriminant, une localité déjà inscrite
    # est gardée (adresses ajoutées avant la règle du wiki); sur une rue
    # avec discriminant, addr:city devrait être ce discriminant.
    localites = Counter()
    hors_discriminant = []   # (Ligne, ref, tags, Adresse)
    sans_ville = 0
    for l, ref, t, a in retrouvees:
        if not t.get("addr:city"):
            sans_ville += 1
        elif not a or t["addr:city"] == a.ville:
            continue
        elif a.discriminant:
            hors_discriminant.append((l, ref, t, a))
        else:
            localites[t["addr:city"]] += 1
    connues = {a.ville for a in ad} | {v for v in localites} - {
        v for v in localites if any(v != w and v.lower() == w.lower() for w in localites)}
    casse = sorted({t["addr:city"] for l, ref, t, a in retrouvees if t.get("addr:city")
                    and t["addr:city"] not in connues
                    and any(t["addr:city"].lower() == w.lower() for w in connues)})
    avec_cp = sum(1 for l, ref, t, a in retrouvees if t.get("addr:postcode"))
    cp_differents = sum(1 for l, ref, t, a in retrouvees
                        if t.get("addr:postcode") and t["addr:postcode"] != l.code_postal)

    # Corrections de rue (les ajouts de addr:city et addr:postcode mis à part).
    corr_rues = sorted((ref, ch) for ref, ch in plan.modifier.items() if "addr:street" in ch)

    nouveaux = sorted((l for l in plan.rapport if l.statut == "nouveau"), key=ordre)
    a_revoir = sorted((l for l in plan.rapport if l.statut == "à revoir"), key=ordre)
    exclus = sorted((l for l in plan.rapport if l.statut == "exclu"), key=ordre)
    logements = sorted(((l, ref, t) for l, ref, t, a in retrouvees if "logements :" in l.detail),
                       key=lambda x: ordre(x[0]))

    # Rue d'OSM la plus proche d'une adresse « à revoir ».
    routes = [(w["tags"]["name"], [index.point(n) for n in w["nodes"] if index.point(n)])
              for w in index.chemins.values() if "highway" in w.get("tags", {}) and w["tags"].get("name")]

    def rue_proche(p):
        meilleur = None
        for nom, pts in routes:
            if len(pts) < 2:
                continue
            d = geo.distance_ligne(p, pts)
            if d < RUE_PROCHE_M and (meilleur is None or d < meilleur[1]):
                meilleur = (nom, d)
        return meilleur

    def logements_attendus(l):
        a, autres = groupe(l)
        if not a:
            return ""
        autres = [x for x in autres if not adresses.logement_douteux(a, x)]
        return ";".join(adresses.numeros(l.numero, a, autres)[1])

    nom = conf.get("nom", lieu)
    r = ["# Adresses : %s, comparaison avec OSM" % nom, ""]
    r.append("Données OSM : %s. Source : Référentiel québécois des adresses (MRNF), version %s." % (
        "extrait du " + date_extrait(), version))
    r.append("")
    r.append("Comparaison faite selon la [méthode de validation des noms de rues et des adresses]"
             "(https://wiki.openstreetmap.org/wiki/FR:Qu%C3%A9bec/Validation_des_noms_de_rues_et_des_adresses) "
             "et les [règles d'osmqc](../../README.md#adresses). Une adresse du RQA est retrouvée dans "
             "OSM par un objet au même numéro à moins de 30 m, ou par le bâtiment ou le terrain qui "
             "contient son point, ou au même numéro sur la même rue à moins de 300 m. Un objet à "
             "plusieurs numéros (`47;49`) est retrouvé par chacun. Rien n'est envoyé : ce rapport "
             "sert à repérer les différences. Carte de toutes les lignes : "
             "[comparaison.geojson](comparaison.geojson).")
    r += ["", "## Résumé", "", "| Résultat | Nombre |", "|---|---|"]
    total = len(plan.rapport)
    lignes_resume = [
        ("Adresses du RQA (après regroupement des logements)", total),
        ("Retrouvées dans OSM", len(retrouvees)),
        ("Retrouvées, nom de rue différent dans OSM", len(corr_rues)),
        ("Retrouvées, logements différents", len(logements)),
        ("Absentes d'OSM, rue présente", len(nouveaux)),
        ("Absentes d'OSM, rue introuvable sous ce nom", len(a_revoir)),
        ("Non certifiées au RQA (ignorées)", len(exclus)),
        ("Adresses d'OSM sans pendant au RQA", len(plan.seules_osm)),
    ]
    r += ["| %s | %d |" % kv for kv in lignes_resume]

    r += ["", "## Questions", "", "### addr:city", ""]
    r.append("Selon la [méthode du wiki](https://wiki.openstreetmap.org/wiki/FR:Qu%%C3%%A9bec/"
             "Validation_des_noms_de_rues_et_des_adresses), `addr:city` est le nom de la "
             "municipalité, ou le discriminant de la rue au RQA; les adresses ajoutées avant "
             "cette règle gardent leur nom de localité (l'ancienne municipalité). Pour les %d "
             "adresses retrouvées : %d portent une localité sur une rue sans discriminant "
             "(gardée, rien à faire), %d portent autre chose que le discriminant de leur rue, "
             "%d n'ont pas de `addr:city`." % (len(retrouvees), sum(localites.values()),
                                                len(hors_discriminant), sans_ville))
    if localites:
        r += ["", "Localités sur les rues sans discriminant : %s." % ", ".join(
            "%s %d" % kv for kv in localites.most_common())]
    if casse:
        r += ["", "Écrites autrement que la forme habituelle (casse) : %s." % ", ".join(
            "« %s »" % v for v in casse)]
    if hors_discriminant:
        r += ["", "Rues avec discriminant au RQA, `addr:city` différent dans OSM : à corriger, "
              "ou le discriminant du RQA est-il à revoir?", "",
              "| Selon le RQA | Dans OSM | Adresses |", "|---|---|---|"]
        r += ["| %s | %s | %d |" % (cellule(a), cellule(b), n) for (a, b), n in Counter(
            (a.ville, t["addr:city"]) for l, ref, t, a in hors_discriminant).most_common()]
        r += ["", "| Adresse | Objet | Discriminant (RQA) | addr:city (OSM) |", "|---|---|---|---|"]
        r += ["| %s %s | %s | %s | %s |" % (cellule(l.numero), cellule(l.rue), objet(*ref),
                                            cellule(a.discriminant), cellule(t["addr:city"]))
              for l, ref, t, a in sorted(hors_discriminant, key=lambda x: ordre(x[0]))]
    r += ["", "### addr:postcode", ""]
    r.append("%d des %d adresses retrouvées ont un `addr:postcode` dans OSM (%d différent du RQA). "
             "Le RQA donne un code postal pour chaque adresse, sous sa propre licence. "
             "Est-ce voulu de ne pas l'ajouter?" % (avec_cp, len(retrouvees), cp_differents))

    r += ["", "## Retrouvées, nom de rue différent dans OSM (%d)" % len(corr_rues), ""]
    if corr_rues:
        r += ["| Objet | Dans OSM | Nom officiel (RQA) | Numéro |", "|---|---|---|---|"]
        for ref, ch in corr_rues:
            t = tags_de(ref)
            r.append("| %s | %s | %s | %s |" % (objet(*ref), cellule(t.get("addr:street")),
                                                 cellule(ch["addr:street"]), cellule(t.get("addr:housenumber"))))

    r += ["", "## Retrouvées, logements différents (%d)" % len(logements), ""]
    r.append("Logements selon le RQA (sans les logements douteux : ni lot ni matricule, sur une "
             "adresse que le rôle d'évaluation dit à un seul logement) et dans OSM "
             "(`addr:flats`, sinon `addr:unit`).")
    r += ["", "| Adresse | Objet | RQA | OSM | Écart |", "|---|---|---|---|---|"]
    for l, ref, t in logements:
        ecart = l.detail.split("logements : ")[1].split(";")[0]
        r.append("| %s %s | %s | %s | %s | %s |" % (
            cellule(l.numero), cellule(l.rue), objet(*ref), cellule(logements_attendus(l)),
            cellule(t.get("addr:flats") or t.get("addr:unit")), ecart))

    r += ["", "## Absentes d'OSM, rue présente (%d)" % len(nouveaux), ""]
    r.append("Par qualité de la position au RQA : %s." % ", ".join(
        "%s %d" % kv for kv in Counter(l.qualite for l in nouveaux).most_common()))
    r += ["", "| Adresse | Qualité | Logements | Position |", "|---|---|---|---|"]
    for l in nouveaux:
        r.append("| %s %s | %s | %s | %s |" % (cellule(l.numero), cellule(l.rue), l.qualite,
                                              cellule(logements_attendus(l)), carte(l.lon, l.lat)))

    r += ["", "## Absentes d'OSM, rue introuvable sous ce nom (%d)" % len(a_revoir), ""]
    r.append("Aucune rue d'OSM de ce nom à moins de 300 m. La rue nommée la plus proche est "
             "indiquée, si elle existe.")
    r += ["", "| Adresse | Rue d'OSM la plus proche | Distance | Adresse déjà dans OSM | Position |",
          "|---|---|---|---|---|"]
    for l in a_revoir:
        proche = rue_proche((l.lon, l.lat))
        ref = objet_du_detail(l.detail)
        r.append("| %s %s | %s | %s | %s | %s |" % (
            cellule(l.numero), cellule(l.rue), cellule(proche[0]) if proche else "",
            "%d m" % proche[1] if proche else "", objet(*ref) if ref else "", carte(l.lon, l.lat)))

    r += ["", "## Adresses d'OSM sans pendant au RQA (%d)" % len(plan.seules_osm), ""]
    r.append("Adresses d'OSM près du lieu qu'aucune adresse du RQA ne retrouve : ajoutées d'une "
             "autre source, ou au numéro ou à la rue écrits autrement.")
    r += ["", "| Objet | Numéro | Rue | addr:city |", "|---|---|---|---|"]
    for genre, ident, num, rue, ville, p in sorted(plan.seules_osm,
                                                    key=lambda x: (x[3] or "", adresses._ordre(x[2] or ""))):
        r.append("| %s | %s | %s | %s |" % (objet(genre, ident), cellule(num), cellule(rue), cellule(ville)))

    if exclus:
        r += ["", "## Non certifiées au RQA (%d)" % len(exclus), ""]
        r += ["- %s %s : %s" % (l.numero, l.rue, l.detail) for l in exclus]

    sortie = os.path.join("rapports", lieu)
    os.makedirs(sortie, exist_ok=True)
    with open(os.path.join(sortie, "comparaison.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(r) + "\n")

    # Carte : une entité par ligne des sections ci-dessus.
    ents = []
    def ent(lon, lat, categorie, **props):
        ents.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [round(lon, 7), round(lat, 7)]},
                     "properties": dict(categorie=categorie, **props)})
    for l in nouveaux:
        ent(l.lon, l.lat, "absente d'OSM", adresse="%s %s" % (l.numero, l.rue), qualite=l.qualite)
    for l in a_revoir:
        ent(l.lon, l.lat, "rue introuvable", adresse="%s %s" % (l.numero, l.rue), qualite=l.qualite)
    for l, ref, t in logements:
        ent(l.lon, l.lat, "logements différents", adresse="%s %s" % (l.numero, l.rue),
            osm="%s/%d" % ref, rqa=logements_attendus(l), dans_osm=t.get("addr:flats") or t.get("addr:unit") or "")
    for genre, ident, num, rue, ville, p in plan.seules_osm:
        ent(p[0], p[1], "sans pendant au RQA", adresse="%s %s" % (num, rue or ""), osm="%s/%d" % (genre, ident))
    with open(os.path.join(sortie, "comparaison.geojson"), "w", encoding="utf-8") as fh:
        json.dump({"type": "FeatureCollection", "features": ents}, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
    print("Rapport : %s/comparaison.md (%d entités sur la carte)" % (sortie, len(ents)))


def date_extrait():
    """Date de l'extrait d'OSM (horodatage de réplication du .pbf)."""
    pbf = os.environ.get("OSMQC_PBF", os.path.join("donnees", "quebec-latest.osm.pbf"))
    try:
        import osmium
        h = osmium.io.Reader(pbf, osmium.osm.osm_entity_bits.NOTHING).header()
        d = h.get("osmosis_replication_timestamp")
        return d[:10] if d else "?"
    except Exception:
        return "?"


main()
