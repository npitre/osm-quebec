# Rapports de révision en Markdown (lisibles sur GitHub) et GeoJSON
# allégés (GitHub les affiche sur une carte), dans rapports/.

import os
import re
from collections import Counter, defaultdict

COULEURS = {"nouveau": "#2ca02c", "corrigé": "#ff7f0e", "existant": "#7f7f7f",
            "à revoir": "#d62728", "exclu": "#9467bd", "modifié": "#ff7f0e",
            "supprimé": "#000000"}


def tableau(entetes, lignes):
    s = "| " + " | ".join(entetes) + " |\n|" + "|".join("---" for _ in entetes) + "|\n"
    for l in lignes:
        s += "| " + " | ".join(str(x).replace("|", "\\|") for x in l) + " |\n"
    return s


def geojson_allege(complet):
    """Garde l'essentiel des propriétés et ajoute la couleur des points
    (convention simplestyle, reconnue par GitHub)."""
    f = []
    for e in complet["features"]:
        p = e["properties"]
        statut = p.get("statut", "")
        q = {k: p[k] for k in ("statut", "numero", "rue", "code_postal", "qualite", "position",
                               "detail", "objet", "changements", "raisons") if k in p and p[k] not in ("", None, [])}
        if e["geometry"]["type"] == "Point":
            q["marker-color"] = COULEURS.get(statut, "#7f7f7f")
            q["marker-size"] = "small"
        else:
            q["stroke"] = COULEURS.get(statut, "#7f7f7f")
        f.append({"type": "Feature", "geometry": e["geometry"], "properties": q})
    return {"type": "FeatureCollection", "features": f}


def _num(v):
    m = re.match(r"\d*", v)
    return (int(m.group() or 0), v)


def adresses(lieu, conf, plan, version):
    """Rapport Markdown d'un import d'adresses."""
    nom = conf.get("nom", lieu)
    stat = Counter(l.statut for l in plan.rapport)
    pos = Counter(l.position for l in plan.rapport)
    s = "# Adresses : %s\n\n" % nom
    if conf.get("_source_osm"):
        s += "Données OSM : %s.\n\n" % conf["_source_osm"]
    s += ("Source : Référentiel québécois des adresses (MRNF), %s. Règles : voir le "
          "[README](../../README.md#adresses). Carte : [adresses.geojson](adresses.geojson). "
          "Commentaires : [README](README.md).\n\n" % version)
    s += "## Résumé\n\n"
    s += tableau(["Résultat", "Nombre"], [
        ["Nouvelles adresses", stat["nouveau"]],
        ["Déjà dans OSM, corrigées", stat["corrigé"]],
        ["Déjà dans OSM, inchangées", stat["existant"]],
        ["À revoir (non créées)", stat["à revoir"]],
        ["Exclues", stat["exclu"]],
        ["Logements douteux écartés", len(plan.douteux)],
        ["Objets OSM modifiés", len(plan.modifier)],
        ["Lignes d'interpolation supprimées", len(plan.supprimer_chemins)],
        ["Nœuds d'interpolation supprimés", len(plan.supprimer_noeuds)],
    ])
    s += "\nSource des positions : %s.\n\n" % ", ".join("%s %d" % kv for kv in pos.most_common())

    # Adresses à revoir, regroupées par cause et par rue.
    rues = defaultdict(Counter)
    for l in plan.rapport:
        if l.statut != "à revoir":
            continue
        m = re.search(r"rue écrite « ([^»]*) » dans OSM", l.detail)
        if m:
            rues["Nom écrit autrement dans OSM"][(l.rue, m.group(1))] += 1
        elif "aucune rue" in l.detail:
            rues["Rue absente ou sans nom dans OSM"][(l.rue, "")] += 1
        else:
            rues["Autre"][(l.rue, l.detail)] += 1
    if rues:
        s += "## À revoir\n\nCes adresses ne sont pas créées tant que la rue n'est pas réglée dans OSM.\n\n"
        for cause in ("Nom écrit autrement dans OSM", "Rue absente ou sans nom dans OSM", "Autre"):
            if cause not in rues:
                continue
            s += "### %s (%d adresses)\n\n" % (cause, sum(rues[cause].values()))
            if cause == "Nom écrit autrement dans OSM":
                s += tableau(["Nom officiel (RQA)", "Dans OSM", "Adresses"],
                             [[a, b, n] for (a, b), n in rues[cause].most_common()])
            elif cause == "Rue absente ou sans nom dans OSM":
                s += tableau(["Nom officiel (RQA)", "Adresses"],
                             [[a, n] for (a, _), n in rues[cause].most_common()])
            else:
                s += tableau(["Rue", "Détail", "Adresses"],
                             [[a, b, n] for (a, b), n in rues[cause].most_common()])
            s += "\n"

    if plan.douteux:
        s += "## Logements douteux\n\n"
        s += ("Logements du RQA sans lot ni matricule, sur une adresse qui n'a qu'un logement "
              "selon le rôle d'évaluation : ils ne sont pas mis dans addr:unit. Liste à "
              "signaler au MRNF (géoboutique). Voir le [README](../../README.md#logements-douteux-du-rqa).\n\n")
        s += tableau(["Municipalité", "Adresse", "Créé le", "Identifiant RQA"], [
            [x.nom_municipalite, "%s-%s %s" % (x.logement, x.numero, x.rue),
             "%s-%s-%s" % (x.date_creation[:4], x.date_creation[4:6], x.date_creation[6:8]), x.ident]
            for x, _ in sorted(plan.douteux, key=lambda d: (d[0].nom_municipalite, d[0].rue.casefold(),
                                                            _num(d[0].numero), _num(d[0].logement)))])
        s += "\n"
    if plan.modifier:
        s += "## Objets OSM modifiés\n\n"
        s += tableau(["Objet", "Changements", "Raison"], [
            ["[%s/%d](https://www.openstreetmap.org/%s/%d)" % (g, i, g, i),
             ", ".join("%s=%s" % kv for kv in t.items()), "; ".join(plan.raisons.get((g, i), []))]
            for (g, i), t in sorted(plan.modifier.items())])
        s += "\n"
    if plan.supprimer_chemins:
        s += "## Lignes d'interpolation supprimées\n\n"
        s += ", ".join("[%d](https://www.openstreetmap.org/way/%d)" % (w, w) for w in plan.supprimer_chemins)
        s += "\n"
    return s


def regions(lieu, conf, officiel, rels, compte, ecarts, plan, supp):
    nom = conf.get("nom", lieu)
    s = "# Limites municipales : %s\n\n" % nom
    if conf.get("_source_osm"):
        s += "Données OSM : %s.\n\n" % conf["_source_osm"]
    s += ("Source : Découpages administratifs du MRNF (1/20 000). Règles : voir le "
          "[README](../../README.md#régions). Carte : [regions.geojson](regions.geojson) "
          "(propriété `source` : MRNF ou OSM actuel). Commentaires : [README](README.md).\n\n")
    s += "## Limites actuelles dans OSM\n\n"
    s += tableau(["Municipalité", "Relation", "Anneaux", "Chemins qui la forment"], [
        [r.tags.get("name", code), "[%d](https://www.openstreetmap.org/relation/%d)" % (r.id, r.id),
         len(r.anneaux), ", ".join("%s %d" % kv for kv in r.composition.most_common())]
        for code, r in sorted(rels.items())])
    s += "\n## Limites officielles (MRNF)\n\n"
    s += tableau(["Municipalité", "Code", "Version", "Polygones", "Trous", "Sommets"], [
        [n, code, ver, len(p), sum(len(x) - 1 for x in p), sum(len(a) for x in p for a in x)]
        for code, (n, ver, p) in sorted(officiel.items())])
    s += "\n## Adresses : municipalité selon chaque limite\n\n"
    lignes = [["MRNF", compte[("MRNF", True)], compte[("MRNF", False)]],
              ["OSM actuel", compte[("OSM", True)], compte[("OSM", False)]]]
    if plan and "verification" in plan:
        v = plan["verification"]
        lignes.append(["OSM après le remplacement proposé", v[("OSM", True)], v[("OSM", False)]])
    s += tableau(["Limite", "Bonne municipalité", "Autre ou aucune"], lignes)
    if ecarts:
        s += "\n" + tableau(["Adresse", "Municipalité (RQA)", "Selon le MRNF", "Selon OSM"], [
            ["%s %s" % (a.numero, a.rue), a.municipalite, m or "aucune", o or "aucune"]
            for a, m, o in ecarts])
    if plan:
        s += "\n## Remplacement proposé\n\n"
        s += tableau(["Élément", "Nombre"], [
            ["Nœuds créés", len(plan["noeuds"])],
            ["Chemins de limite créés", len(plan["chemins"])],
            ["Relations modifiées", len(plan["modifiees"])],
            ["Chemins retirés des relations", len(plan["retires"])],
            ["dont supprimés (simples lignes de limite inutilisées)", len(supp[0])],
            ["Nœuds supprimés", len(supp[1])],
        ])
        s += "\n" + "\n".join("- " + r for r in plan["rapport"]) + "\n"
        if supp[0]:
            s += "\nChemins supprimés : %s.\n" % ", ".join(
                "[%d](https://www.openstreetmap.org/way/%d)" % (w, w) for w in supp[0])
        s += ("\nLe littoral et les autres objets retirés des relations ne sont pas modifiés : "
              "seule leur appartenance aux limites change.\n")
    if plan and plan.get("decoupe"):
        d = plan["decoupe"]
        s += "\n## Routes coupées\n\n"
        s += ("%d routes coupées, %d nœuds de coupure ajoutés sur les routes, %d morceaux neufs, "
              "%d relations de route mises à jour.\n\n" % (
                  len(d.get("coupes", d["modifies"])), len(d["noeuds"]), len(d["chemins"]), len(d["relations"])))
        s += "\n".join("- " + r for r in d["rapport"]) + "\n"
        if d.get("fusions"):
            s += ("\n### Coupures inutiles fusionnées\n\n"
                  "Sur une ancienne limite, deux segments d'une même route aux étiquettes et aux "
                  "relations identiques sont réunis en un seul chemin.\n\n")
            s += "\n".join("- " + r for r in d["fusions"]) + "\n"
    if plan and plan.get("proteges"):
        s += "\n## Chemins protégés\n\n"
        s += ("Ces chemins portent une note, un fixme, une description ou une étiquette "
              "disputed* : ils sont retirés des relations mais jamais supprimés automatiquement. "
              "À traiter à la main.\n\n")
        s += tableau(["Chemin", "Étiquettes", "Note reportée sur"], [
            ["[%d](https://www.openstreetmap.org/way/%d)" % (w, w),
             ", ".join("%s=%s" % kv for kv in t.items()) or "(disputed*)",
             "chemin neuf %d" % n if n else ""] for w, n, t in plan["proteges"]])
    if plan and plan.get("liens"):
        s += "\n## Lien avec le nœud de lieu\n\n"
        s += ("OsmAnd n'utilise une limite que si sa relation a un membre label ou admin_centre "
              "vers un nœud place portant exactement le même nom. Les membres existants sont "
              "gardés; les cas à régler sont signalés.\n\n")
        s += tableau(["Municipalité", "Statut", "Détail"], [
            [rels[c].tags.get("name", c), st, det] for c, (st, det) in sorted(plan["liens"].items())])
    if plan and plan.get("coupures") is not None:
        c = plan["coupures"]
        n = Counter(x[0] for x in c)
        s += "\n## Routes qui traversent les limites\n\n"
        s += ("Une route nommée est coupée exactement là où elle traverse une limite "
              "municipale (à moins de %d m), même si ses étiquettes sont identiques des deux "
              "côtés : Nominatim et Photon rattachent chaque segment de rue à une seule "
              "municipalité. Les coupures « à ajouter » et « à déplacer » sont faites dans le "
              "fichier d'envoi; une coupure « devenue inutile », et l'ancienne coupure d'une "
              "coupure déplacée, sont fusionnées quand c'est possible (voir plus haut). Une "
              "« voie à cheval », qui croise la limite à moins de %d m d'un autre de ses "
              "croisements, la longe plutôt que de la traverser : elle n'est pas coupée, à "
              "revoir à la main.\n\n" % (25, 200))
        s += tableau(["Situation", "Nombre"], [[k, n[k]] for k in (
            "déjà coupée", "coupure à déplacer", "coupure à ajouter", "coupure devenue inutile",
            "voie à cheval")])
        autres = [x for x in c if x[0] != "déjà coupée"]
        if autres:
            s += "\n" + tableau(["Situation", "Rue", "Chemin", "Position", "Écart"], [
                [a, nom, "[%d](https://www.openstreetmap.org/way/%d)" % (w, w),
                 "%.5f, %.5f" % (p[1], p[0]), "%.0f m" % d if d is not None else ""]
                for a, nom, w, p, d, _ in sorted(autres, key=lambda x: x[:2])])
    return s


def ecrire(chemin, texte):
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as fh:
        fh.write(texte.rstrip("\n") + "\n")


def rues(lieu, conf, liste, changes, conflits):
    nom = conf.get("nom", lieu)
    stat = Counter(r.statut for r in liste)
    s = "# Noms de rue : %s\n\n" % nom
    if conf.get("_source_osm"):
        s += "Données OSM : %s.\n\n" % conf["_source_osm"]
    s += ("Noms d'OSM comparés aux odonymes officiels du RQA, autour des adresses. "
          "Règles : voir le [README](../../README.md#rues). Carte : [rues.geojson](rues.geojson). "
          "Commentaires : [README](README.md).\n\n")
    s += tableau(["Situation", "Rues", "Adresses"], [
        [k, stat[k], sum(r.adresses for r in liste if r.statut == k)]
        for k in ("conforme", "à renommer", "autre nom", "sans nom", "absente")])
    a_ren = [r for r in liste if r.statut == "à renommer"]
    if a_ren:
        s += "\n## À renommer (casse, accents, tirets ou espaces)\n\n"
        s += tableau(["Nom officiel", "Dans OSM", "Segments", "Adresses"], [
            [r.officiel, ", ".join("%s (%d)" % kv for kv in r.noms_osm.items() if kv[0] != r.officiel),
             len(r.renommer), r.adresses] for r in sorted(a_ren, key=lambda r: -r.adresses)])
    for statut, titre, texte in (
            ("autre nom", "Nom différent dans OSM",
             "La voie la plus proche des adresses porte un autre nom. À trancher à la main."),
            ("sans nom", "Voie sans nom dans OSM",
             "Les adresses longent une voie sans nom : candidate pour recevoir le nom officiel."),
            ("absente", "Rue absente d'OSM", "Aucune voie à moins de 60 m des adresses.")):
        lst = [r for r in liste if r.statut == statut]
        if not lst:
            continue
        s += "\n## %s\n\n%s\n\n" % (titre, texte)
        s += tableau(["Nom officiel", "Municipalité", "Adresses", "Voie(s) la plus proche"], [
            [r.officiel, r.municipalite, r.adresses, ", ".join(
                "[%d](https://www.openstreetmap.org/way/%d) %s%s (%d)" % (
                    c[0], c[0], c[1], " « %s »" % c[3] if c[3] else "", c[2]) for c in r.candidats[:3])]
            for r in sorted(lst, key=lambda r: -r.adresses)])
    if changes:
        s += "\n## Renommages proposés (%d chemins)\n\n" % len(changes)
        s += tableau(["Chemin", "Nom actuel", "Nouveau nom", "Raison"], [
            ["[%d](https://www.openstreetmap.org/way/%d)" % (w, w), a, b, r] for w, a, b, r in changes])
    if conflits:
        s += "\n## Conflits\n\n" + tableau(["Chemin", "Noms officiels possibles"], [
            [w, ", ".join(sorted(n))] for w, n in sorted(conflits.items())])
    return s


def rues_geojson(liste, changes, index):
    f = []
    ren = {w: (a, b) for w, a, b, _ in changes}
    for w, (a, b) in ren.items():
        f.append({"type": "Feature", "geometry": {"type": "LineString",
                  "coordinates": [list(p) for p in index.ligne(w)]} if w in index.chemins else None,
                  "properties": {"statut": "renommé", "objet": "way/%d" % w, "avant": a, "apres": b,
                                 "stroke": "#ff7f0e", "stroke-width": 4}})
    for r in liste:
        if r.statut in ("autre nom", "sans nom"):
            for c in r.candidats[:1]:
                if c[0] in index.chemins:
                    f.append({"type": "Feature", "geometry": {"type": "LineString",
                              "coordinates": [list(p) for p in index.ligne(c[0])]},
                              "properties": {"statut": r.statut, "officiel": r.officiel,
                                             "objet": "way/%d" % c[0], "nom_osm": c[3],
                                             "stroke": "#d62728", "stroke-width": 4}})
    return {"type": "FeatureCollection", "features": [x for x in f if x["geometry"]]}


def _arrondir(c):
    if isinstance(c, (int, float)):
        return round(c, 7)
    return [_arrondir(x) for x in c]


def ecrire_geojson_compact(donnees, chemin):
    """GeoJSON de publication : coordonnées à 7 décimales (1 cm), sans
    indentation, pour rester sous la taille que GitHub affiche."""
    import json
    for f in donnees["features"]:
        if f.get("geometry"):
            f["geometry"]["coordinates"] = _arrondir(f["geometry"]["coordinates"])
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as fh:
        json.dump(donnees, fh, ensure_ascii=False, separators=(",", ":"))
        fh.write("\n")
