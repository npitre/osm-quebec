# Envoi d'un fichier osmChange à OpenStreetMap en un seul groupe de
# modifications (changeset), avec une authentification OAuth 2.0 (PKCE).
#
# Préalable, une seule fois : créer une application OAuth 2 sur
#   https://www.openstreetmap.org/oauth2/applications/new
#   (https://master.apis.dev.openstreetmap.org/... pour le serveur de test)
#   - URI de redirection : urn:ietf:wg:oauth:2.0:oob (OSM affiche le code)
#   - Permission : « Modifier la carte » (write_api)
# puis inscrire son identifiant dans ~/.config/osmqc/application.toml :
#   client_id = "..."
#   client_secret = "..."     # seulement si OSM en a fourni un
#
# Le jeton obtenu est gardé dans ~/.config/osmqc/jeton (ou jeton-test),
# lisible par vous seul. Rien de tout cela n'est dans le dépôt.

import base64
import hashlib
import json
import os
import secrets
import sys
import tomllib
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

CONFIG = os.path.expanduser("~/.config/osmqc")
SITES = {
    "reel": ("https://www.openstreetmap.org", "https://api.openstreetmap.org/api/0.6"),
    "test": ("https://master.apis.dev.openstreetmap.org",
             "https://master.apis.dev.openstreetmap.org/api/0.6"),
}
REDIRECTION = "urn:ietf:wg:oauth:2.0:oob"


def requete(url, data=None, methode="GET", jeton=None, type_contenu=None):
    req = urllib.request.Request(url, data=data, method=methode)
    if jeton:
        req.add_header("Authorization", "Bearer " + jeton)
    if type_contenu:
        req.add_header("Content-Type", type_contenu)
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            return r.read()
    except urllib.error.HTTPError as e:
        sys.exit("Erreur %d sur %s : %s" % (e.code, url, e.read().decode(errors="replace")))


def application():
    chemin = os.path.join(CONFIG, "application.toml")
    if not os.path.exists(chemin):
        sys.exit("Inscrivez l'identifiant de votre application OAuth dans %s "
                 "(voir l'en-tête de osmqc/envoi.py)." % chemin)
    with open(chemin, "rb") as fh:
        return tomllib.load(fh)


def jeton(mode):
    fichier = os.path.join(CONFIG, "jeton-test" if mode == "test" else "jeton")
    if os.path.exists(fichier):
        return open(fichier).read().strip()
    app = application()
    site = SITES[mode][0]
    verif = secrets.token_urlsafe(48)
    defi = base64.urlsafe_b64encode(hashlib.sha256(verif.encode()).digest()).rstrip(b"=").decode()
    url = site + "/oauth2/authorize?" + urllib.parse.urlencode({
        "response_type": "code", "client_id": app["client_id"], "redirect_uri": REDIRECTION,
        "scope": "write_api", "code_challenge": defi, "code_challenge_method": "S256"})
    print("Ouvrez cette adresse, connectez-vous et autorisez l'application :")
    print(url)
    code = input("Code affiché par OSM : ").strip()
    params = {"grant_type": "authorization_code", "code": code, "redirect_uri": REDIRECTION,
              "client_id": app["client_id"], "code_verifier": verif}
    if app.get("client_secret"):
        params["client_secret"] = app["client_secret"]
    rep = requete(site + "/oauth2/token", urllib.parse.urlencode(params).encode(), "POST",
                  type_contenu="application/x-www-form-urlencoded")
    j = json.loads(rep)["access_token"]
    os.makedirs(CONFIG, mode=0o700, exist_ok=True)
    ancien = os.umask(0o077)
    with open(fichier, "w") as fh:
        fh.write(j + "\n")
    os.umask(ancien)
    return j


def etiquettes(groupe, mode, section=""):
    """Étiquettes du groupe de modifications : import=yes, source,
    commentaire et lien de la discussion publique. L'envoi réel est refusé
    sans discussion."""
    tags = {"comment": groupe["comment"], "source": groupe["source"], "import": "yes",
            "created_by": "osmqc"}
    if groupe.get("discussion"):
        tags["discussion"] = groupe["discussion"]
        tags["comment"] += ". Discussion : " + groupe["discussion"]
    elif mode == "reel":
        sys.exit("Pas de discussion inscrite dans [%s.groupe] : un import doit d'abord être "
                 "annoncé." % section)
    return tags


def envoyer(osc, etiquettes, mode, resultat=None, confirmer=input):
    """osc : élément XML osmChange. etiquettes : celles du groupe de
    modifications. mode : « test » ou « reel ». resultat : fichier où
    garder la réponse de l'API (identifiants définitifs et nouvelles
    versions, pour tenir l'extrait local à jour). Un envoi réel est
    résumé, puis confirmé par confirmer (« oui »). Si l'API refuse
    l'envoi, le groupe de modifications est fermé aussitôt; l'envoi est
    tout ou rien, rien n'a changé dans OSM."""
    api = SITES[mode][1]
    if mode == "test":
        # Les objets existants n'existent pas sur le serveur de test.
        for bloc in osc.findall("modify") + osc.findall("delete"):
            osc.remove(bloc)
        print("Mode test : seules les créations sont envoyées.")
    compte = {b.tag: len(b) for b in osc}
    print("Envoi à %s : %s objets (créés %d, modifiés %d, supprimés %d)." % (
        SITES[mode][0], sum(compte.values()), compte.get("create", 0), compte.get("modify", 0),
        compte.get("delete", 0)))
    for k, v in etiquettes.items():
        print("  %s = %s" % (k, v))
    if mode == "reel" and confirmer("Envoyer à OpenStreetMap? (oui/non) ").strip().lower() != "oui":
        sys.exit("Rien n'a été envoyé.")
    j = jeton(mode)
    cs = ET.Element("osm")
    c = ET.SubElement(cs, "changeset")
    for k, v in etiquettes.items():
        ET.SubElement(c, "tag", k=k, v=v)
    cid = requete(api + "/changeset/create", ET.tostring(cs), "PUT", j, "text/xml").decode().strip()
    print("Groupe de modifications %s ouvert." % cid)
    for el in osc.iter():
        if el.tag in ("node", "way", "relation"):
            el.set("changeset", cid)
    try:
        reponse = requete(api + "/changeset/%s/upload" % cid, ET.tostring(osc), "POST", j, "text/xml")
    except SystemExit:
        requete(api + "/changeset/%s/close" % cid, None, "PUT", j)
        print("Groupe de modifications %s fermé : l'envoi a été refusé, rien n'a changé dans OSM." % cid)
        raise
    if resultat:
        with open(resultat, "wb") as fh:
            fh.write(reponse)
    requete(api + "/changeset/%s/close" % cid, None, "PUT", j)
    print("Envoyé et fermé : %s/changeset/%s" % (SITES[mode][0], cid))
    if resultat:
        print("Réponse de l'API (identifiants et versions) : %s" % resultat)
    return cid


def correspondances(resultat):
    """La réponse de l'API à un envoi (diffResult) : {(type, ancien id):
    (nouvel id, nouvelle version)}, pour extrait.appliquer. Un objet
    supprimé garde son identifiant."""
    res = {}
    for e in ET.parse(resultat).getroot():
        ancien = int(e.get("old_id"))
        nouveau = int(e.get("new_id")) if e.get("new_id") else ancien
        version = int(e.get("new_version")) if e.get("new_version") else 0
        res[(e.tag, ancien)] = (nouveau, version)
    return res
