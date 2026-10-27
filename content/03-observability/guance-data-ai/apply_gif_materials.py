# -*- coding: utf-8 -*-
import os
import shutil
import subprocess

GDRIVE_ROOT = "/Users/shenlan/Library/CloudStorage/GoogleDrive-haitaopanhq@gmail.com/我的云端硬盘/观测云合作稿 2026-10-27"
GIF_V2_DIR = os.path.join(GDRIVE_ROOT, "GIF 动图 v2（纯架构图）")
V4_ROOT = os.path.join(GDRIVE_ROOT, "观测云首季计划 v4")
BASE_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge-v5-runtime-blockers/content/03-observability/guance-data-ai"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
ARTIFACT_DIR = "/Users/shenlan/.gemini/antigravity/brain/16698aac-3268-4a79-9f85-da84dbd894ee"
ART_GIF_DIR = os.path.join(ARTIFACT_DIR, "assets_gif")
os.makedirs(ART_GIF_DIR, exist_ok=True)

# 1. Copy GIF v2 for Article 1 and Article 2
a1_assets = os.path.join(ARTICLES_DIR, "01-free-tier-for-indie-saas", "assets")
a2_assets = os.path.join(ARTICLES_DIR, "02-observability-migration-with-rollback", "assets")
a3_assets = os.path.join(ARTICLES_DIR, "03-real-user-experience-rum", "assets")
a4_assets = os.path.join(ARTICLES_DIR, "04-cross-cloud-distributed-tracing", "assets")

print("[1/5] Copying GIF v2 animated files for Article 1 & 2...")
for f in os.listdir(GIF_V2_DIR):
    if f.startswith("a1-") and f.endswith(".gif"):
        src = os.path.join(GIF_V2_DIR, f)
        shutil.copy2(src, os.path.join(a1_assets, f))
        shutil.copy2(src, os.path.join(ART_GIF_DIR, f))
        print(f"  Copied A1 GIF: {f}")
    elif f.startswith("a2-") and f.endswith(".gif"):
        src = os.path.join(GIF_V2_DIR, f)
        shutil.copy2(src, os.path.join(a2_assets, f))
        shutil.copy2(src, os.path.join(ART_GIF_DIR, f))
        print(f"  Copied A2 GIF: {f}")

print("[2/5] Copying GIF animated files for Article 3 & 4...")
a3_src_dir = os.path.join(V4_ROOT, "03-rum-ai-page-slow")
for f in os.listdir(a3_src_dir):
    if f.endswith(".gif"):
        src = os.path.join(a3_src_dir, f)
        shutil.copy2(src, os.path.join(a3_assets, f))
        shutil.copy2(src, os.path.join(ART_GIF_DIR, f))
        print(f"  Copied A3 GIF: {f}")

a4_src_dir = os.path.join(V4_ROOT, "04-login-trace-across-clouds")
for f in os.listdir(a4_src_dir):
    if f.endswith(".gif"):
        src = os.path.join(a4_src_dir, f)
        shutil.copy2(src, os.path.join(a4_assets, f))
        shutil.copy2(src, os.path.join(ART_GIF_DIR, f))
        print(f"  Copied A4 GIF: {f}")

print("GIF files successfully copied.")
