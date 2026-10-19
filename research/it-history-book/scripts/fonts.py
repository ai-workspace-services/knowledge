"""查找 Noto Sans CJK SC（macOS / Linux），必要时从 .ttc 拆出 SC 字形，并按用到的字做子集。"""
import os, glob, hashlib
CANDS = {
 'regular': ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc',
             '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Regular.ttc', '~/Library/Fonts/NotoSansCJKsc-Regular.otf',
             '/Library/Fonts/NotoSansCJKsc-Regular.otf', '~/Library/Fonts/NotoSansSC-Regular.otf', '/opt/homebrew/share/fonts/NotoSansCJK-Regular.ttc'],
 'bold':    ['/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc', '/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc',
             '/usr/share/fonts/google-noto-cjk/NotoSansCJK-Bold.ttc', '~/Library/Fonts/NotoSansCJKsc-Bold.otf',
             '/Library/Fonts/NotoSansCJKsc-Bold.otf', '~/Library/Fonts/NotoSansSC-Bold.otf', '/opt/homebrew/share/fonts/NotoSansCJK-Bold.ttc'],
}
def find(kind, configured='auto'):
    paths = [configured] if configured and configured != 'auto' else CANDS[kind]
    for p in paths:
        p = os.path.expanduser(p)
        if os.path.exists(p): return p
    # 兜底：fc-list / 常见目录 glob
    for g in ['/usr/share/fonts/**/NotoSansCJK*%s*' % kind.capitalize(), os.path.expanduser('~/Library/Fonts/NotoSans*CJK*%s*' % kind.capitalize())]:
        r = glob.glob(g, recursive=True)
        if r: return r[0]
    raise SystemExit('找不到 Noto Sans CJK %s 字体，请按 README 安装，或在 book.yml 的 fonts 里写明路径' % kind)

def sc_face(path, cache):
    """.ttc -> 抽出 'Noto Sans CJK SC' 一面为 otf"""
    if not path.lower().endswith('.ttc'): return path
    from fontTools.ttLib import TTCollection
    out = os.path.join(cache, os.path.basename(path).replace('.ttc', '-SC.otf'))
    if not os.path.exists(out):
        c = TTCollection(path)
        f = next((f for f in c.fonts if f['name'].getDebugName(1) == 'Noto Sans CJK SC'), c.fonts[0])
        f.save(out)
    return out

def subset(path, chars, cache):
    from fontTools import subset as S
    chars = ''.join(sorted(set(chars) | set(chr(c) for c in range(32, 127)) | set('　…•·（）：，。、')))
    h = hashlib.md5((path + chars + 'g1').encode()).hexdigest()[:10]
    out = os.path.join(cache, 'sub-%s-%s.otf' % (os.path.basename(path).split('.')[0], h))
    if not os.path.exists(out):
        opt = S.Options(); opt.layout_features = ['*']; opt.retain_gids = True  # PyMuPDF 按原 GID 写字形，必须保留 GID，否则 MuPDF 系阅读器显示空白
        f = S.load_font(path, opt); sub = S.Subsetter(opt); sub.populate(text=chars); sub.subset(f); S.save_font(f, out, opt)
    return out
