import os
import shutil

DESKTOP_DIR = "/Users/shenlan/Desktop/AI聚合网关-工程决策与图文发布包"
KNOWLEDGE_ROOT = "/Users/shenlan/workspaces/ai-workspace-service/knowledge"
ESSAYS_DIR = os.path.join(KNOWLEDGE_ROOT, "content/00-global/essays/ai-aggregator-gateway")
ASSETS_DIR = os.path.join(KNOWLEDGE_ROOT, "assets/images")

os.makedirs(DESKTOP_DIR, exist_ok=True)
images_target_dir = os.path.join(DESKTOP_DIR, "assets/images")
os.makedirs(images_target_dir, exist_ok=True)

# 1. Copy All Assets to assets/images/ in the desktop pack
print("Copying asset images...")
for f in os.listdir(ASSETS_DIR):
    if f.startswith("gateway-") or f.startswith("xconnect-"):
        src = os.path.join(ASSETS_DIR, f)
        dst = os.path.join(images_target_dir, f)
        shutil.copy2(src, dst)
        print(f"Copied asset: {f}")

# 2. Also create user-friendly named shortcuts/copies right in an "00-各平台精选配图" folder
covers_folder = os.path.join(DESKTOP_DIR, "各平台配图直取 (微信_小红书_X_工程画布)")
os.makedirs(covers_folder, exist_ok=True)

friendly_mapping = [
    # 5 Engineering Canvases
    ("gateway-canvas-01-selection.png", "01-工程决策画布-选型篇-Kong_vs_APISIX.png"),
    ("gateway-canvas-02-architecture.png", "02-工程决策画布-架构篇-双层分流与安全契约.png"),
    ("gateway-canvas-03-credentials.png", "03-工程决策画布-凭据篇-CPA矩阵与Vault注入.png"),
    ("gateway-canvas-04-integration.png", "04-工程决策画布-实战篇-客户端接入与GitOps.png"),
    ("gateway-canvas-05-troubleshooting.png", "05-工程决策画布-排障篇-真实推理避坑实测.png"),
    
    # WeChat covers
    ("gateway-01-wechat-cover.png", "01-微信公众号首图-选型篇.png"),
    ("gateway-02-wechat-cover.png", "02-微信公众号首图-架构篇.png"),
    ("gateway-03-wechat-cover.png", "03-微信公众号首图-凭据篇.png"),
    ("gateway-04-wechat-cover.png", "04-微信公众号首图-实战篇.png"),
    ("gateway-05-wechat-cover.png", "05-微信公众号首图-排障篇.png"),
    
    # Xiaohongshu covers
    ("gateway-01-xhs-cover.png", "01-小红书爆款海报-选型篇.png"),
    ("gateway-02-xhs-cover.png", "02-小红书爆款海报-架构篇.png"),
    ("gateway-03-xhs-cover.png", "03-小红书爆款海报-凭据篇.png"),
    ("gateway-04-xhs-cover.png", "04-小红书爆款海报-实战篇.png"),
    ("gateway-05-xhs-cover.png", "05-小红书爆款海报-排障篇.png"),
    
    # X / Twitter covers
    ("gateway-01-x-cover.png", "01-X文章封面-选型篇.png"),
    ("gateway-02-x-cover.png", "02-X文章封面-架构篇.png"),
    ("gateway-03-x-cover.png", "03-X文章封面-凭据篇.png"),
    ("gateway-04-x-cover.png", "04-X文章封面-实战篇.png"),
    ("gateway-05-x-cover.png", "05-X文章封面-排障篇.png"),
    
    # 3D Concept Artworks
    ("gateway-01-selection-cover.jpg", "01-3D概念原画-Kong_vs_APISIX.jpg"),
    ("gateway-02-architecture-cover.jpg", "02-3D概念原画-Caddy_APISIX架构.jpg"),
    ("gateway-03-credentials-cover.jpg", "03-3D概念原画-Vault凭据防线.jpg"),
    ("gateway-04-integration-cover.jpg", "04-3D概念原画-多客户端接入GitOps.jpg"),
    ("gateway-05-troubleshooting-cover.jpg", "05-3D概念原画-全链路排障监控.jpg"),
    ("xconnect-vault-migration-cover.png", "06-封面-XConnect零信任Vault跨云迁移.png"),
]

for src_name, target_name in friendly_mapping:
    src_file = os.path.join(ASSETS_DIR, src_name)
    if os.path.exists(src_file):
        shutil.copy2(src_file, os.path.join(covers_folder, target_name))

# 3. Copy Markdown articles and adjust relative image links
md_files = [
    ("README.md", "00-README-专栏总览与工程画布全览.md"),
    ("01-selection-kong-vs-apisix.zh.md", "01-选型篇-Kong_vs_APISIX深度抉择.zh.md"),
    ("01-selection-kong-vs-apisix.en.md", "01-selection-kong-vs-apisix.en.md"),
    ("02-architecture-and-traffic-routing.zh.md", "02-架构篇-双层分流与安全契约.zh.md"),
    ("02-architecture-and-traffic-routing.en.md", "02-architecture-and-traffic-routing.en.md"),
    ("03-cpa-matrix-and-vault-credentials.zh.md", "03-凭据篇-CPA矩阵与Vault动态注入.zh.md"),
    ("03-cpa-matrix-and-vault-credentials.en.md", "03-cpa-matrix-and-vault-credentials.en.md"),
    ("04-client-integration-and-gitops.zh.md", "04-实战篇-统一客户端接入与GitOps自动化.zh.md"),
    ("04-client-integration-and-gitops.en.md", "04-client-integration-and-gitops.en.md"),
    ("05-inference-troubleshooting-and-ops.zh.md", "05-排障篇-真实推理避坑实测与运维复盘.zh.md"),
    ("05-inference-troubleshooting-and-ops.en.md", "05-inference-troubleshooting-and-ops.en.md"),
]

# Companion case study
vault_case_zh = os.path.join(KNOWLEDGE_ROOT, "content/00-global/essays/2026-10-01-xconnect-zero-trust-vault-migration.zh.md")
vault_case_en = os.path.join(KNOWLEDGE_ROOT, "content/00-global/essays/2026-10-01-xconnect-zero-trust-vault-migration.en.md")
md_files.append((vault_case_zh, "06-进阶案例-XConnect零信任Vault跨云迁移实战.zh.md"))
md_files.append((vault_case_en, "06-xconnect-zero-trust-vault-migration.en.md"))

for src_item, target_name in md_files:
    if os.path.isabs(src_item):
        src_path = src_item
    else:
        src_path = os.path.join(ESSAYS_DIR, src_item)
    
    if os.path.exists(src_path):
        with open(src_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Replace absolute /assets/images/ with relative ./assets/images/ so offline preview works out of the box
        content = content.replace("(/assets/images/", "(./assets/images/")
        
        dst_path = os.path.join(DESKTOP_DIR, target_name)
        with open(dst_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Copied & processed MD: {target_name}")

print("\nAll files successfully copied to Desktop folder:")
print(DESKTOP_DIR)
