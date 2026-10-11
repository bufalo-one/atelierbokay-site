#!/usr/bin/env python3
"""Prépare index.html pour Google : langue française, titre et description
placés dans <head>, adresse canonique et aperçu de partage.
Usage : python3 scripts/seo.py index.html  (modifie le fichier sur place, ré-exécutable sans risque)"""
import re, sys
p = sys.argv[1]
s = open(p, encoding='utf-8').read()
m0 = re.search(r'<html([^>]*)>', s)
if m0 and 'lang=' not in m0.group(1):
    s = s[:m0.start()] + '<html lang="fr"' + m0.group(1) + '>' + s[m0.end():]
head_end = s.index('</head>')
moved = []
for pat in (r'<title>.*?</title>', r'<meta name="description"[^>]*>'):
    m = re.search(pat, s[head_end:], re.S)
    if m:
        a, b = head_end + m.start(), head_end + m.end()
        moved.append(s[a:b]); s = s[:a] + s[b:]
desc = ''
for t in moved:
    d = re.search(r'content="([^"]*)"', t)
    if t.startswith('<meta') and d: desc = d.group(1)
title = next((re.sub(r'</?title>', '', t) for t in moved if t.startswith('<title>')), 'AtelierBokay')
extra = [
    '<link rel="canonical" href="https://atelierbokay.com/">',
    '<meta property="og:type" content="website">',
    '<meta property="og:url" content="https://atelierbokay.com/">',
    '<meta property="og:title" content="%s">' % title.replace('"', '&quot;'),
    '<meta property="og:locale" content="fr_FR">',
]
if desc: extra.append('<meta property="og:description" content="%s">' % desc)
if 'rel="canonical"' in s: extra = []
block = ''.join(moved) + ''.join(extra)
if block:
    i = s.index('</head>')
    s = s[:i] + block + s[i:]
open(p, 'w', encoding='utf-8').write(s)
print('ok', len(s), 'moved:', len(moved))
