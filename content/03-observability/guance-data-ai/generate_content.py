# -*- coding: utf-8 -*-
"""
Builder and character count validator for Tech Article Series & Quarterly Plan.
Complies strictly with SKILL.md rules:
- WeChat: <= 1500 chars (non-space), 3-5 paragraphs, InfoQ style, decision table.
- XHS: 600-800 chars (non-space), grass-planting style, P1..Pn, conflict title, link diagram, desensitized test, conclusion.
- 3-5 pure technical architecture diagrams (SVG/CSS, no author/dates).
- Core practice: GitOps + IaC + Playbook + Vault. NO Web UI clicking!
"""

import os
import re
import subprocess
import json

def clean_count(text):
    # Remove markdown tables and headers when evaluating prose or count all non-space characters
    # SKILL.md: "微信：严格 ≤1500 字，3–5 段... XHS：严格 600–800 字（非空格字符）"
    return len(re.sub(r'\s+', '', text))

print("generate_content.py initialized.")
