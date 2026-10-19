"""共用：读取 book.yml、front/appendix/chapter Markdown，解析图片列表。"""
import os, re, glob, yaml
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG_RE = re.compile(r'^!\[([^\]]*)\]\(([^)]+)\)\s*$')
IMG_EXT = ('.png', '.jpg', '.jpeg', '.webp', '.gif')

def read_md(path):
    """返回 (front_matter: dict, body: str)"""
    t = open(path, encoding='utf-8').read()
    if t.startswith('---\n'):
        end = t.index('\n---', 4)
        return yaml.safe_load(t[4:end]) or {}, t[end + 4:].lstrip('\n')
    return {}, t

def load_book():
    return yaml.safe_load(open(os.path.join(ROOT, 'book.yml'), encoding='utf-8'))

def load_chapter(d):
    """chapters/<d>/chapter.md -> dict(meta, blocks)；blocks 依次为 ('img',cap,abs_path,rel) 或 ('text',md)"""
    base = os.path.join(ROOT, 'chapters', d)
    fm, body = read_md(os.path.join(base, 'chapter.md'))
    blocks, buf = [], []
    for line in body.split('\n'):
        m = IMG_RE.match(line.strip())
        if m:
            if ''.join(buf).strip(): blocks.append(('text', '\n'.join(buf).strip()))
            buf = []
            blocks.append(('img', m.group(1).strip(), os.path.normpath(os.path.join(base, m.group(2))), m.group(2)))
        else:
            buf.append(line)
    if ''.join(buf).strip(): blocks.append(('text', '\n'.join(buf).strip()))
    fm.setdefault('ch', d.split('-')[0]); fm['dir'] = d; fm['base'] = base
    return dict(meta=fm, blocks=blocks)

def images_on_disk(d):
    base = os.path.join(ROOT, 'chapters', d, 'images')
    return sorted(p for p in glob.glob(os.path.join(base, '*')) if p.lower().endswith(IMG_EXT))

def placeholder_mode():
    """环境变量 BOOK_PLACEHOLDER_IMAGES=1：缺图时用灰色占位页（CI 冒烟构建用；本地默认关闭）"""
    return os.environ.get('BOOK_PLACEHOLDER_IMAGES', '').strip().lower() in ('1', 'true', 'yes')
