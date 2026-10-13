#!/usr/bin/env python3
"""Ajoute le filigrane « AtelierBokay » sur les photos des réalisations.

Usage : python3 scripts/filigrane.py
Traite chaque realisations/img/*.jpg qui n'est pas encore listé dans
realisations/img/filigrane.txt, puis met cette liste à jour (une seule fois par photo).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER = os.path.join(RACINE, "realisations", "img")
LISTE = os.path.join(DOSSIER, "filigrane.txt")
POLICE = os.path.join(RACINE, "scripts", "fonts", "DejaVuSerif.ttf")
TEXTE = "© AtelierBokay"

def filigraner(chemin):
    im = ImageOps.exif_transpose(Image.open(chemin)).convert("RGB")
    w, h = im.size
    taille = max(14, int(min(w, h) * 0.045))
    police = ImageFont.truetype(POLICE, taille)
    calque = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(calque)
    x0, y0, x1, y1 = d.textbbox((0, 0), TEXTE, font=police)
    marge = int(taille * 0.9)
    x, y = w - (x1 - x0) - marge, h - (y1 - y0) - marge - y0
    ombre = Image.new("RGBA", im.size, (0, 0, 0, 0))
    ImageDraw.Draw(ombre).text((x + 1, y + 1), TEXTE, font=police, fill=(0, 0, 0, 110))
    ombre = ombre.filter(ImageFilter.GaussianBlur(max(1, taille // 12)))
    d.text((x, y), TEXTE, font=police, fill=(255, 255, 255, 175))
    out = Image.alpha_composite(Image.alpha_composite(im.convert("RGBA"), ombre), calque).convert("RGB")
    out.save(chemin, "JPEG", quality=88, optimize=True)

def main():
    if not os.path.isdir(DOSSIER):
        print("ok 0"); return
    deja = set()
    if os.path.exists(LISTE):
        deja = {l.strip() for l in open(LISTE, encoding="utf-8") if l.strip()}
    photos = sorted(f for f in os.listdir(DOSSIER) if f.lower().endswith(".jpg"))
    n = 0
    for f in photos:
        if f in deja: continue
        try:
            filigraner(os.path.join(DOSSIER, f)); n += 1
        except Exception as e:
            print("erreur", f, e, file=sys.stderr); sys.exit(1)
    with open(LISTE, "w", encoding="utf-8") as fh:
        fh.write("\n".join(f for f in photos) + ("\n" if photos else ""))
    print("ok", n)

if __name__ == "__main__":
    main()
