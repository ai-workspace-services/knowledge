#!/usr/bin/env python3
"""打包 book-src：python3 scripts/pack.py [--no-images] [--out dist/book-src.zip]（不含 dist/、缓存）"""
import os, sys, zipfile, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT
ap = argparse.ArgumentParser(); ap.add_argument('--no-images', action='store_true'); ap.add_argument('--out'); a = ap.parse_args()
out = a.out or os.path.join(ROOT, 'dist', 'book-src%s.zip' % ('-noimages' if a.no_images else ''))
os.makedirs(os.path.dirname(out), exist_ok=True); n = 0
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for dp, dns, fns in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        dns[:] = [d for d in dns if not (rel == '.' and d == 'dist') and d != '__pycache__' and not (a.no_images and d == 'images')]
        for f in fns:
            if f == '.DS_Store': continue
            p = os.path.join(dp, f); z.write(p, os.path.join('book-src', os.path.relpath(p, ROOT))); n += 1
print('%s　%d 个文件　%.1f MB' % (out, n, os.path.getsize(out) / 1e6))
