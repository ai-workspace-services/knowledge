# -*- coding: utf-8 -*-
import os
import re
import subprocess

BASE_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge-v5-runtime-blockers/content/03-observability/guance-data-ai"
ARTICLES_DIR = os.path.join(BASE_DIR, "articles")
PDF_DIR = os.path.join(BASE_DIR, "pdf_exports")
CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

def count_non_space(text):
    return len(re.sub(r'\s+', '', text))

def validate_text(name, wechat_text, xhs_text):
    wc_len = count_non_space(wechat_text)
    xhs_len = count_non_space(xhs_text)
    paragraphs = [p for p in wechat_text.strip().split('\n\n') if p.strip()]
    p_count = len(paragraphs)
    
    print(f"=== Validation: {name} ===")
    print(f"  WeChat Prose Length: {wc_len} (Target: <= 1500 chars) -> {'PASS' if wc_len <= 1500 else 'FAIL'}")
    print(f"  WeChat Paragraphs: {p_count} (Target: 3-5 paragraphs) -> {'PASS' if 3 <= p_count <= 5 else 'FAIL'}")
    print(f"  XHS Non-space Length: {xhs_len} (Target: 600-800 chars) -> {'PASS' if 600 <= xhs_len <= 800 else 'FAIL'}")
    
    if wc_len > 1500 or p_count < 3 or p_count > 5 or xhs_len < 600 or xhs_len > 800:
        raise ValueError(f"Validation failed for {name}!")

print("Validator helper ready.")
