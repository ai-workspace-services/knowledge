# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

GDRIVE_ROOT = "/Users/shenlan/Library/CloudStorage/GoogleDrive-haitaopanhq@gmail.com/我的云端硬盘/观测云合作稿 2026-10-27"
V4_ROOT = os.path.join(GDRIVE_ROOT, "观测云首季计划 v4")
BASE_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge-v5-runtime-blockers/content/03-observability/guance-data-ai"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Destination assets directories
a1_assets = os.path.join(ARTICLES_DIR, "01-free-tier-for-indie-saas", "assets")
a2_assets = os.path.join(ARTICLES_DIR, "02-observability-migration-with-rollback", "assets")
a3_assets = os.path.join(ARTICLES_DIR, "03-real-user-experience-rum", "assets")
a4_assets = os.path.join(ARTICLES_DIR, "04-cross-cloud-distributed-tracing", "assets")

for d in [a1_assets, a2_assets, a3_assets, a4_assets]:
    os.makedirs(d, exist_ok=True)

print("Copying Article 1 images from Google Drive...")
for f in [
    'a1-01-stack-blindspots-wechat.png', 'a1-01-stack-blindspots-xhs.png',
    'a1-02-free-boundary-wechat.png', 'a1-02-free-boundary-xhs.png',
    'a1-03-automation-path-wechat.png', 'a1-03-automation-path-xhs.png',
    'a1-04-evidence-chain-wechat.png', 'a1-04-evidence-chain-xhs.png',
    'a1-05-saas-or-selfhost-wechat.png', 'a1-05-saas-or-selfhost-xhs.png'
]:
    src = os.path.join(GDRIVE_ROOT, f)
    dst = os.path.join(a1_assets, f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  Copied {f}")

print("Copying Article 2 images from Google Drive...")
for f in [
    'a2-01-migration-funnel-wechat.png', 'a2-01-migration-funnel-xhs.png',
    'a2-02-query-traps-wechat.png', 'a2-02-query-traps-xhs.png',
    'a2-03-gitops-hcl-wechat.png', 'a2-03-gitops-hcl-xhs.png',
    'a2-04-side-by-side-rollback-wechat.png', 'a2-04-side-by-side-rollback-xhs.png'
]:
    src = os.path.join(GDRIVE_ROOT, f)
    dst = os.path.join(a2_assets, f)
    if os.path.exists(src):
        shutil.copy2(src, dst)
        print(f"  Copied {f}")

print("Copying Article 3 images from Google Drive v4...")
a3_v4 = os.path.join(V4_ROOT, "03-rum-ai-page-slow")
for f in os.listdir(a3_v4):
    if f.endswith('.gif') or f.endswith('.png'):
        src = os.path.join(a3_v4, f)
        dst = os.path.join(a3_assets, f)
        shutil.copy2(src, dst)
        print(f"  Copied {f}")
        # If it's a gif, convert to png as well
        if f.endswith('.gif'):
            png_name = f.replace('.gif', '.png')
            subprocess.run(['sips', '-s', 'format', 'png', src, '--out', os.path.join(a3_assets, png_name)], stdout=subprocess.DEVNULL)

print("Copying Article 4 images from Google Drive v4...")
a4_v4 = os.path.join(V4_ROOT, "04-login-trace-across-clouds")
for f in os.listdir(a4_v4):
    if f.endswith('.gif') or f.endswith('.png'):
        src = os.path.join(a4_v4, f)
        dst = os.path.join(a4_assets, f)
        shutil.copy2(src, dst)
        print(f"  Copied {f}")
        if f.endswith('.gif'):
            png_name = f.replace('.gif', '.png')
            subprocess.run(['sips', '-s', 'format', 'png', src, '--out', os.path.join(a4_assets, png_name)], stdout=subprocess.DEVNULL)

print("\nAll Google Drive source images and gifs copied and converted.")
