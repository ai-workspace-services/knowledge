#!/usr/bin/env python3
"""自检：
  1) 各章 chapter.md 引用的图片是否都存在、是否重复引用；
  2) images/ 里有没有未被引用的图片；
  3) 所有文字在 Noto Sans CJK SC 中是否都有字形（防方框字）；
  4) 若给出 --pdf（或 dist/ 下已有当前版本 PDF）：抽查目录链接与书签是否一致、页脚页码、PDF 文字有无缺字。
退出码：0 通过；1 有错误。"""
import os, sys, re, argparse, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_book, load_chapter, images_on_disk, read_md
import fonts as F
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--pdf'); ap.add_argument('--no-pdf', action='store_true'); a = ap.parse_args()
    cfg = load_book(); err = []; warn = []; n_img = 0; text = ''
    for d in cfg['chapters']:
        if not os.path.exists(os.path.join(ROOT, 'chapters', d, 'chapter.md')): err.append('缺少 chapters/%s/chapter.md' % d); continue
        c = load_chapter(d); refs = [b for b in c['blocks'] if b[0] == 'img']; n_img += len(refs)
        for k in ('title',):
            if not c['meta'].get(k): err.append('%s: front matter 缺少 %s' % (d, k))
        seen = set()
        for _, cap, p, rel in refs:
            if not os.path.exists(p): err.append('%s: 图片不存在 %s' % (d, rel))
            if p in seen: warn.append('%s: 重复引用 %s' % (d, rel))
            if not cap: warn.append('%s: 图片缺少图注 %s' % (d, rel))
            seen.add(p)
        for p in images_on_disk(d):
            if p not in seen: warn.append('%s: images/ 中未被引用 %s' % (d, os.path.basename(p)))
        text += str(c['meta']) + ''.join(b[1] for b in c['blocks'])
    for f in glob.glob(os.path.join(ROOT, 'front', '*.md')) + glob.glob(os.path.join(ROOT, 'appendix', '*.md')):
        fm, body = read_md(f); text += str(fm) + body
    text += open(os.path.join(ROOT, 'book.yml'), encoding='utf-8').read()
    # 字形检查（book 渲染时 κέρας 会替换为 keras）
    from fontTools.ttLib import TTFont
    cache = os.path.join(ROOT, 'dist', '.cache'); os.makedirs(cache, exist_ok=True)
    cm = set(TTFont(F.sc_face(F.find('regular', cfg.get('fonts', {}).get('regular')), cache)).getBestCmap())
    miss = sorted({ch for ch in text.replace('κέρας', 'keras') if ord(ch) > 31 and ord(ch) not in cm and ch not in '\n\t'})
    if miss: err.append('字体缺字（会显示为方框）：%s' % ''.join(miss))
    print('图片引用：%d 张，章数：%d' % (n_img, len(cfg['chapters'])))
    pdf = a.pdf or os.path.join(ROOT, 'dist', cfg['output'].format(version=cfg['version']))
    if not a.no_pdf and os.path.exists(pdf):
        import pymupdf as fitz
        doc = fitz.open(pdf); toc = doc.get_toc(); tocp = {p for _, _, p in toc}
        norm = lambda s: re.sub(r'\s', '', s.replace('\u2011', '-'))
        bad = [t for lv, t, p in toc if t.startswith('图 ') and norm(t.split('\u3000')[0]) not in norm(doc[p - 1].get_text())]
        links = [l['page'] + 1 for i in range(min(len(doc), 20)) for l in doc[i].get_links() if l['kind'] == fitz.LINK_GOTO]
        foot = [i + 1 for i in range(1, len(doc) - 1) if doc[i].get_text(clip=fitz.Rect(200, 800, 400, 842)).strip() != str(i + 1)]
        nul = [i + 1 for i, p in enumerate(doc) if '\x00' in p.get_text()]
        print('PDF：%s　%d 页　书签 %d 条　目录链接 %d 条' % (os.path.basename(pdf), len(doc), len(toc), len(links)))
        if bad: err.append('书签指向页没有对应图号：%s' % bad[:5])
        if set(links) - tocp: err.append('目录链接指向非书签页：%s' % sorted(set(links) - tocp)[:5])
        if len(links) != len(toc) - 3: warn.append('目录链接数 %d 与书签数 %d（不含封面/总目录/封底）不同' % (len(links), len(toc) - 3))
        if foot: err.append('页脚页码不符：%s' % foot[:5])
        if nul: err.append('PDF 中有缺字页：%s' % nul[:5])
    for w in warn: print('警告：' + w)
    for e in err: print('错误：' + e)
    print('结果：%s（错误 %d，警告 %d）' % ('通过' if not err else '未通过', len(err), len(warn)))
    sys.exit(1 if err else 0)
if __name__ == '__main__': main()
