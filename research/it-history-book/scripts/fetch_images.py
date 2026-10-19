#!/usr/bin/env python3
"""按 images.lock.tsv（章目录、文件名、MD5、字节数）把图片从任意下载目录放回 chapters/*/images/。

Git 里不含图片。CI 的 full-pdf 任务先用 rclone 把 Drive「图解IT简史-整理版」（book.yml drive.folder_id）
只读拷到一个临时目录，再运行本脚本：递归扫描该目录，按 MD5 匹配锁文件条目，复制成书稿需要的文件名。
匹配只看内容，不依赖 Drive 上的文件夹名或文件名。

用法：
  python3 scripts/fetch_images.py --from /tmp/drive-mirror [--allow-missing] [--dry-run]
  python3 scripts/fetch_images.py --write-lock      # 用本地已有图片重新生成 images.lock.tsv（加图/换图后运行并提交）
"""
import os, sys, glob, shutil, hashlib, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_book, load_chapter, IMG_EXT
LOCK = os.path.join(ROOT, 'images.lock.tsv')

def md5(p):
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def refs():
    for d in load_book()['chapters']:
        for b in load_chapter(d)['blocks']:
            if b[0] == 'img': yield d, b[3], b[2]

def write_lock():
    rows, miss = [], []
    for d, rel, p in refs():
        if os.path.exists(p): rows.append((d, rel, md5(p), str(os.path.getsize(p))))
        else: miss.append('%s/%s' % (d, rel))
    if miss: raise SystemExit('本地缺图，无法生成锁文件：%s' % miss[:5])
    with open(LOCK, 'w', encoding='utf-8') as f:
        f.write('# chapter\tpath\tmd5\tbytes  (scripts/fetch_images.py --write-lock 生成)\n')
        for r in rows: f.write('\t'.join(r) + '\n')
    print('写入 %s：%d 条' % (os.path.relpath(LOCK, ROOT), len(rows)))

def read_lock():
    out = []
    for ln in open(LOCK, encoding='utf-8'):
        if ln.startswith('#') or not ln.strip(): continue
        d, rel, h, n = ln.rstrip('\n').split('\t'); out.append((d, rel, h, int(n)))
    return out

def fetch(src, allow_missing, dry):
    if not os.path.isdir(src): raise SystemExit('目录不存在：%s' % src)
    lock = read_lock(); want_sizes = {n for _, _, _, n in lock}; pool = {}
    for p in glob.glob(os.path.join(src, '**', '*'), recursive=True):
        if os.path.isfile(p) and p.lower().endswith(IMG_EXT) and os.path.getsize(p) in want_sizes:
            pool.setdefault(md5(p), p)
    placed = have = 0; miss = []
    for d, rel, h, _ in lock:
        dst = os.path.normpath(os.path.join(ROOT, 'chapters', d, rel))
        if os.path.exists(dst) and md5(dst) == h: have += 1; continue
        if h not in pool: miss.append('%s/%s' % (d, rel)); continue
        if not dry: os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(pool[h], dst)
        placed += 1
    print('锁文件 %d 张：已存在 %d，新放置 %d，缺失 %d%s' % (len(lock), have, placed, len(miss), '（演练）' if dry else ''))
    for m in miss[:50]: print('缺失：' + m)
    # 锁文件之外 chapter.md 新引用的图
    locked = {(d, rel) for d, rel, _, _ in lock}
    extra = [(d, rel) for d, rel, _ in refs() if (d, rel) not in locked]
    if extra: print('提示：%d 张图在 chapter.md 中引用但不在锁文件里，请本地 make lock 后提交' % len(extra))
    if miss and not allow_missing: sys.exit(1)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--from', dest='src'); ap.add_argument('--write-lock', action='store_true')
    ap.add_argument('--allow-missing', action='store_true'); ap.add_argument('--dry-run', action='store_true')
    a = ap.parse_args()
    if a.write_lock: write_lock()
    elif a.src: fetch(a.src, a.allow_missing, a.dry_run)
    else: ap.error('需要 --from DIR 或 --write-lock')
if __name__ == '__main__': main()
