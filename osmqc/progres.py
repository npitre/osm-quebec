# Indicateur de progression des longues étapes, sur la sortie d'erreur :
# une ligne au début de chaque étape, avec le temps écoulé depuis le
# lancement, puis une ligne toutes les 30 secondes pendant une lecture de
# l'extrait, avec la part du fichier déjà lue. Des lignes ordinaires,
# lisibles en braille (pas de retour de chariot qui réécrit la ligne).
#
# OSMQC_SANS_PROGRES=1 les fait taire (tests).

import contextlib
import os
import sys
import threading
import time

DEBUT = time.monotonic()
INTERVALLE = 30         # secondes entre deux lignes pendant une lecture


def _actif():
    return os.environ.get("OSMQC_SANS_PROGRES") != "1"


def _temps():
    s = int(time.monotonic() - DEBUT)
    return "%d:%02d" % (s // 60, s % 60)


def etape(texte):
    """Annonce le début d'une étape."""
    if _actif():
        print("[%s] %s" % (_temps(), texte), file=sys.stderr, flush=True)


def position(fichier):
    """Part déjà lue du fichier, en pour cent, d'après la position de ses
    descripteurs ouverts dans ce processus (Linux : /proc/self/fdinfo).
    None si on ne la connaît pas."""
    try:
        vrai = os.path.realpath(fichier)
        taille = os.path.getsize(vrai)
        pos = None
        for fd in os.listdir("/proc/self/fd"):
            try:
                if os.path.realpath("/proc/self/fd/" + fd) != vrai:
                    continue
                with open("/proc/self/fdinfo/" + fd) as fh:
                    for ligne in fh:
                        if ligne.startswith("pos:"):
                            pos = max(pos or 0, int(ligne.split()[1]))
            except OSError:
                continue
        return None if pos is None or not taille else min(100, pos * 100 // taille)
    except OSError:
        return None


@contextlib.contextmanager
def lecture(fichier, quoi):
    """Lecture d'un fichier (l'extrait) : annoncée, puis suivie toutes
    les 30 secondes jusqu'à la fin; la durée est donnée si elle a
    dépassé 30 secondes."""
    etape("Lecture de l'extrait : %s" % quoi)
    if not _actif():
        yield
        return
    debut = time.monotonic()
    fini = threading.Event()

    def veiller():
        while not fini.wait(INTERVALLE):
            p = position(fichier)
            etape("  ... %s" % ("%d %% lu" % p if p is not None else "lecture en cours"))

    fil = threading.Thread(target=veiller, daemon=True)
    fil.start()
    try:
        yield
    finally:
        fini.set()
        fil.join()
        duree = time.monotonic() - debut
        if duree >= INTERVALLE:
            etape("  lu en %d:%02d" % (duree // 60, duree % 60))


def suivre(objets, fichier, quoi):
    """Les objets d'une lecture de fichier (un FileProcessor), avec son
    suivi (voir lecture)."""
    with lecture(fichier, quoi):
        yield from objets
