#!/usr/bin/env python3
"""Sort les photos intégrées dans index.html (data:image en base64) vers page/img/,
pour qu'elles reçoivent le filigrane comme les autres photos.

Usage : python3 scripts/photos_page.py index.html  (appelé aussi par seo.py ; ré-exécutable sans risque)
Le logo (class logo-img) et le QR code (alt contenant « QR ») restent intégrés, sans filigrane.
Chaque photo est nommée d'après son contenu : la même photo garde le même fichier d'une publication
à l'autre et n'est donc filigranée qu'une fois. Les fichiers qui ne servent plus sont supprimés.
"""
import base64, hashlib, io, os, re, sys
from PIL import Image

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(RACINE, "page", "img")
IMG = re.compile(r'<img\b[^>]*>', re.I)
SRC = re.compile(r'src="data:image/(png|jpe?g|webp|gif);base64,([A-Za-z0-9+/=\s]+)"', re.I)


def garder(tag):
    if re.search(r'class="[^"]*\blogo-img\b', tag):
        return True
    alt = re.search(r'alt="([^"]*)"', tag)
    return bool(alt and "qr" in alt.group(1).lower())


def main(chemin):
    s = open(chemin, encoding="utf-8").read()
    os.makedirs(DOSSIER, exist_ok=True)
    utilises, sorties = set(), 0

    def remplacer(m):
        nonlocal sorties
        tag = m.group(0)
        src = SRC.search(tag)
        if not src or garder(tag):
            return tag
        brut = base64.b64decode(re.sub(r"\s", "", src.group(2)))
        nom = hashlib.sha1(brut).hexdigest()[:20] + ".jpg"
        utilises.add(nom)
        fichier = os.path.join(DOSSIER, nom)
        if not os.path.exists(fichier):
            im = Image.open(io.BytesIO(brut))
            if im.mode in ("RGBA", "LA", "P"):
                im = im.convert("RGBA")
                fond = Image.new("RGB", im.size, (255, 253, 248))
                fond.paste(im, mask=im.split()[-1])
                im = fond
            im.convert("RGB").save(fichier, "JPEG", quality=88, optimize=True)
        sorties += 1
        return tag[:src.start()] + 'src="page/img/%s"' % nom + tag[src.end():]

    s = IMG.sub(remplacer, s)
    # Photos déjà sorties lors d'une publication précédente (src="page/img/...")
    utilises |= set(re.findall(r'page/img/([0-9a-f]{20}\.jpg)', s))
    for f in os.listdir(DOSSIER):
        if f.endswith(".jpg") and f not in utilises:
            os.remove(os.path.join(DOSSIER, f))
    open(chemin, "w", encoding="utf-8").write(s)
    return sorties


if __name__ == "__main__":
    print("ok", main(sys.argv[1]))
