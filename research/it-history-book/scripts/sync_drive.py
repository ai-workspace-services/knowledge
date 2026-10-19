#!/usr/bin/env python3
"""把本地 Google Drive 同步目录里「图解IT简史-整理版」新增的图拷到对应章的 images/，并追加到 chapter.md 末尾。
只新增、不删除、不覆盖。按内容（MD5）去重：images/ 里已有相同内容的图会跳过。

用法：python3 scripts/sync_drive.py --drive-dir "<Google Drive>/我的云端硬盘/自媒体/图解IT简史-整理版" [--dry-run]
DRIVE_DIR 下的子文件夹按前缀匹配章：00-…、01-…、07x-… 对应 chapters/00-*、chapters/01-*、chapters/07x-*。"""
import os, sys, re, glob, shutil, hashlib, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, load_book, images_on_disk, IMG_EXT
def md5(p): return hashlib.md5(open(p, 'rb').read()).hexdigest()
def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--drive-dir', required=True); ap.add_argument('--dry-run', action='store_true'); a = ap.parse_args()
    if not os.path.isdir(a.drive_dir): raise SystemExit('目录不存在：%s' % a.drive_dir)
    cfg = load_book(); total = 0
    for d in cfg['chapters']:
        pre = d.split('-')[0]
        src = [p for p in glob.glob(os.path.join(a.drive_dir, pre + '-*')) if os.path.isdir(p)]
        if not src: continue
        have = {md5(p) for p in images_on_disk(d)}
        imgdir = os.path.join(ROOT, 'chapters', d, 'images'); n = len(images_on_disk(d)); add = []
        for f in sorted(glob.glob(os.path.join(src[0], '*'))):
            if not f.lower().endswith(IMG_EXT) or md5(f) in have: continue
            n += 1; name = '%03d-%s' % (n, re.sub(r'[\\/:*?"<>|\s]+', '_', os.path.basename(f)))
            cap = re.sub(r'\.(png|jpe?g|webp|gif)$', '', os.path.basename(f), flags=re.I)
            add.append((f, name, cap)); have.add(md5(f))
        for f, name, cap in add:
            print('[%s] + %s' % (d, name))
            if not a.dry_run:
                shutil.copy2(f, os.path.join(imgdir, name))
                with open(os.path.join(ROOT, 'chapters', d, 'chapter.md'), 'a', encoding='utf-8') as fh: fh.write('![%s](images/%s)\n\n' % (cap, name))
        total += len(add)
    print('新增 %d 张%s。请检查图注与顺序后运行 make check。' % (total, '（演练，未写入）' if a.dry_run else ''))
if __name__ == '__main__': main()
