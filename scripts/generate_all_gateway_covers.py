import os
from PIL import Image, ImageDraw, ImageFont

ASSETS_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge/assets/images"
FONT_ZH_BOLD = "/System/Library/Fonts/STHeiti Medium.ttc"
FONT_ZH_LIGHT = "/System/Library/Fonts/STHeiti Light.ttc"
FONT_EN = "/System/Library/Fonts/HelveticaNeue.ttc"

def get_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()

def draw_diamond(draw, center_x, center_y, size, fill, outline=None):
    points = [
        (center_x, center_y - size),
        (center_x + size, center_y),
        (center_x, center_y + size),
        (center_x - size, center_y),
    ]
    draw.polygon(points, fill=fill, outline=outline)

# Definition of the 5 Parts Metadata
PARTS = [
    {
        "index": "01",
        "tag": "HOME-LAB 实战 · 01 选型篇",
        "en_tag": "AI AGGREGATOR GATEWAY · PART 01",
        "title": "再也不用多账号切换了！",
        "en_title": "Stop Multi-Account Switching",
        "sub": "搭建个人专属全能 AI 聚合网关",
        "xhs_h1": "告别多账号切换！",
        "xhs_h2": "全能 AI 聚合网关搭建指南",
        "topic": "【第 01 篇 选型篇】Kong vs APISIX 终极抉择",
        "x_topic": "选型篇：Kong vs APISIX Standalone 深度抉择",
        "base_img": "gateway-01-selection-cover.jpg",
        "primary_col": (56, 189, 248),     # Cyan
        "accent_col": (245, 158, 11),      # Amber
        "pill_bg": (14, 116, 144, 210),
        "pill_border": (56, 189, 248, 255),
        "bullets": [
            ("单入口收敛：", "Codex / Claude / Gemini / Antigravity 零心智接入"),
            ("架构深抉择：", "为什么选 APISIX Standalone 彻底弃用 Kong？"),
            ("极简轻量化：", "0 外部数据库与 etcd · 纯 GitOps 文件驱动交付"),
        ],
        "badges": ["双层鉴权", "单 Token 解耦", "统一 HTTPS 路由"],
        "x_badges": ["GitOps Declarative", "Zero-DB Runtime", "Multi-Account CPA", "Open Multi-Model"],
        "xhs_features": [
            ("01", "统一入口 · 零心智接入", "单一 HTTPS 域名 + 单网关 Token，CLI、IDE 与 SDK 彻底免折腾", (56, 189, 248)),
            ("02", "选型断舍离 · 极简架构", "彻底摒弃庞大 DB 与 etcd，APISIX Standalone 纯 GitOps 文件驱动", (245, 158, 11)),
            ("03", "开源自由 · 无商业枷锁", "内置开源 ai-proxy-multi，多账号与官方 Key 智能分流探活", (139, 92, 246)),
        ],
        "xhs_card_tag": "网关流量中枢 · 聚合 OpenAI / Claude / Gemini / Antigravity",
    },
    {
        "index": "02",
        "tag": "HOME-LAB 实战 · 02 架构篇",
        "en_tag": "AI AGGREGATOR GATEWAY · PART 02",
        "title": "双层分流与安全契约！",
        "en_title": "Two-Tier Traffic Splitting",
        "sub": "从 Caddy 到 APISIX 的流量中枢设计",
        "xhs_h1": "双层分流与安全契约！",
        "xhs_h2": "Caddy 到 APISIX 流量中枢设计",
        "topic": "【第 02 篇 架构篇】边缘 TLS 终止与内部零信任分流",
        "x_topic": "架构篇：边缘 TLS 终止与内部零信任安全分流",
        "base_img": "gateway-02-architecture-cover.jpg",
        "primary_col": (16, 185, 129),     # Emerald Green
        "accent_col": (56, 189, 248),      # Cyan
        "pill_bg": (6, 95, 70, 210),
        "pill_border": (16, 185, 129, 255),
        "bullets": [
            ("边缘分工明确：", "Caddy 负责外部 TLS 自动 ACME 与内部回环安全转发"),
            ("单 Token 解耦：", "外层 apikey 网关校验，内层 Authorization 业务透传"),
            ("上游平级解耦：", "New API 聚合 CPA 渠道，LiteLLM 承载官方商业 API"),
        ],
        "badges": ["Caddy 边缘 TLS", "APISIX 流量中枢", "New API & LiteLLM 并列"],
        "x_badges": ["Edge TLS Caddy", "Real-IP Trust", "Decoupled Auth", "Parallel Upstreams"],
        "xhs_features": [
            ("01", "职责严格分层", "Caddy 终结公网 HTTPS，APISIX 专职内网安全流控与分流", (16, 185, 129)),
            ("02", "凭据双层解耦", "网关校验 apikey，业务上游透传 Authorization，互不干扰", (56, 189, 248)),
            ("03", "上游平级无嵌套", "New API 与 LiteLLM 平级并列，杜绝双重代理风暴与额外延迟", (245, 158, 11)),
        ],
        "xhs_card_tag": "双层架构 · Caddy (TLS) + APISIX (Auth/ACL) + AI Upstreams",
    },
    {
        "index": "03",
        "tag": "HOME-LAB 实战 · 03 凭据篇",
        "en_tag": "AI AGGREGATOR GATEWAY · PART 03",
        "title": "账号矩阵与凭据防线！",
        "en_title": "CPA Matrix & Vault Secrets",
        "sub": "CPA 矩阵隔离与 Vault 敏感凭据动态注入",
        "xhs_h1": "账号矩阵与凭据防线！",
        "xhs_h2": "CPA 矩阵隔离与 Vault 凭据注入",
        "topic": "【第 03 篇 凭据篇】单账号 OAuth 隔离与内存级零泄露",
        "x_topic": "凭据篇：单账号 OAuth 隔离与 Vault 动态注入落地",
        "base_img": "gateway-03-credentials-cover.jpg",
        "primary_col": (244, 63, 94),      # Rose/Red
        "accent_col": (245, 158, 11),      # Amber
        "pill_bg": (159, 18, 57, 210),
        "pill_border": (244, 63, 94, 255),
        "bullets": [
            ("单账号单实例：", "独立 Unix 用户 + 0700 鉴权目录，彻底防止跨账号污染"),
            ("动态凭据注入：", "Vault KV 集中托管，服务启动时动态注入内存 tmpfs"),
            ("绝对零落地原则：", "严禁 OAuth 材料入 Git、DB 明文、CI Artifact 与日志"),
        ],
        "badges": ["单账号单实例", "Vault 内存注入", "0700 鉴权防护"],
        "x_badges": ["Unix Isolation", "Tmpfs Injection", "Vault KV AppRole", "Zero-Leakage Guarantee"],
        "xhs_features": [
            ("01", "实例严格物理隔离", "每 CPA 实例独立系统用户、端口与目录，权限锁定 0700", (244, 63, 94)),
            ("02", "敏感信息绝不落地", "Token 与 API Key 仅保存在内存 tmpfs，随服务启停消亡", (245, 158, 11)),
            ("03", "Vault 动态注入闭环", "AppRole 凭据轮转，Git 仓库仅保留占位符，彻底防泄漏", (56, 189, 248)),
        ],
        "xhs_card_tag": "安全边界 · Vault 加密机 + 内存 tmpfs + CPA 账号矩阵隔离",
    },
    {
        "index": "04",
        "tag": "HOME-LAB 实战 · 04 实战篇",
        "en_tag": "AI AGGREGATOR GATEWAY · PART 04",
        "title": "全客户端零心智接入！",
        "en_title": "Zero-Friction Client & GitOps",
        "sub": "统一客户端零心智接入与 GitOps 自动化编排",
        "xhs_h1": "全客户端零心智接入！",
        "xhs_h2": "统一客户端接入与 GitOps 编排",
        "topic": "【第 04 篇 实战篇】终端 CLI、IDE 插件与自动化配置交付",
        "x_topic": "实战篇：全工具链对接规范与 GitOps 自动化编排交付",
        "base_img": "gateway-04-integration-cover.jpg",
        "primary_col": (139, 92, 246),     # Violet/Purple
        "accent_col": (56, 189, 248),      # Cyan
        "pill_bg": (109, 40, 217, 210),
        "pill_border": (139, 92, 246, 255),
        "bullets": [
            ("全工具链纳管：", "Claude Code / Codex / Cursor / VS Code / Antigravity 一键收敛"),
            ("声明式 GitOps：", "Ansible 对账 + Standalone YAML 自动下发热重载"),
            ("极速平滑更新：", "配置变更秒级热加载生效，长连接推理调用不断流"),
        ],
        "badges": ["CLI & IDE 统一", "Ansible 声明式对账", "秒级热重载不断流"],
        "x_badges": ["Unified Client Config", "Ansible Orchestration", "Hot-Reload Zero-Downtime", "Declarative YAML"],
        "xhs_features": [
            ("01", "全开发工具链纳管", "Codex / Claude Code / Cursor / VS Code 统一指向单一网关", (139, 92, 246)),
            ("02", "GitOps 自动化对账", "一处提交 YAML，Ansible 自动渲染、对账并下发全套配置", (56, 189, 248)),
            ("03", "热重载零业务中断", "网关路由与租户更新即时生效，长文本推理不断连", (16, 185, 129)),
        ],
        "xhs_card_tag": "开发实战 · 客户端无缝对接 + 自动化 GitOps 交付流水线",
    },
    {
        "index": "05",
        "tag": "HOME-LAB 实战 · 05 排障篇",
        "en_tag": "AI AGGREGATOR GATEWAY · PART 05",
        "title": "真实推理避坑与复盘！",
        "en_title": "Inference Gotchas & Operations",
        "sub": "真实推理避坑实测与 Home-Lab 运维巡检复盘",
        "xhs_h1": "真实推理避坑实测！",
        "xhs_h2": "全链路排障实战与运维复盘",
        "topic": "【第 05 篇 排障篇】流式截断、429 熔断与可观测性实测",
        "x_topic": "排障篇：真实推理避坑实测与 Home-Lab 巡检运维复盘",
        "base_img": "gateway-05-troubleshooting-cover.jpg",
        "primary_col": (249, 115, 22),     # Orange
        "accent_col": (239, 68, 68),       # Red
        "pill_bg": (194, 65, 12, 210),
        "pill_border": (249, 115, 22, 255),
        "bullets": [
            ("流式推理防截断：", "SSE 长连接响应防缓冲截断、OpenResty 缓存与超时深度调优"),
            ("全链路熔断降级：", "主动健康探活、动态权重重试与模型异常自动故障转移"),
            ("Home-Lab 巡检护航：", "内存碎片治理、日志轮转与单节点高可用压测准则"),
        ],
        "badges": ["SSE 流式防截断", "动态健康探活与熔断", "Home-Lab 巡检基线"],
        "x_badges": ["SSE Streaming Optimization", "429 Fallback Routing", "Health Checks", "Home-Lab Runbooks"],
        "xhs_features": [
            ("01", "流式长连接避坑", "彻底解决 SSE 流式输出缓冲卡死、中途截断与超时报错", (249, 115, 22)),
            ("02", "智能探活与故障转移", "429 限流毫秒级切换备用账号，商业 API 自动兜底", (239, 68, 68)),
            ("03", "Home-Lab 巡检实操", "日志轮转、内存水位监控、单节点故障自愈脚本全公开", (56, 189, 248)),
        ],
        "xhs_card_tag": "运维看板 · 实时推理延迟监控 + 故障自愈 + Home-Lab 稳定护航",
    },
]

# -------------------------------------------------------------
# Generator Functions
# -------------------------------------------------------------
def generate_wechat(part):
    width, height = 1200, 510
    im = Image.new("RGBA", (width, height), (10, 14, 24, 255))
    base_path = os.path.join(ASSETS_DIR, part["base_img"])
    
    if os.path.exists(base_path):
        base = Image.open(base_path).convert("RGBA")
        bw, bh = base.size
        crop_box = (int(bw * 0.16), 0, bw, bh)
        cropped = base.crop(crop_box)
        target_h = height
        target_w = int(cropped.width * (target_h / cropped.height))
        resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        im.paste(resized, (width - target_w, 0))
        
        # Smooth alpha gradient overlay
        grad = Image.new("L", (width, height), 0)
        grad_draw = ImageDraw.Draw(grad)
        for x in range(width):
            if x < 500:
                alpha = 255
            elif x < 820:
                alpha = int(255 * (1.0 - (x - 500) / 320))
            else:
                alpha = 0
            grad_draw.line([(x, 0), (x, height)], fill=alpha)
        
        overlay = Image.new("RGBA", (width, height), (10, 14, 24, 255))
        im = Image.composite(overlay, im, grad)

    draw = ImageDraw.Draw(im)
    
    # Category Pill
    f_pill = get_font(FONT_ZH_BOLD, 17)
    draw.rounded_rectangle([52, 44, 350, 78], radius=8, fill=part["pill_bg"], outline=part["pill_border"], width=1)
    draw.text((68, 50), part["tag"], font=f_pill, fill=(224, 242, 254, 255))
    
    # Main Title
    f_title = get_font(FONT_ZH_BOLD, 42)
    draw.text((52, 98), part["title"], font=f_title, fill=(255, 255, 255, 255))
    
    # Subtitle
    f_sub = get_font(FONT_ZH_BOLD, 32)
    draw.text((52, 154), part["sub"], font=f_sub, fill=part["primary_col"] + (255,))
    
    # Glowing divider line
    draw.line([(52, 208), (560, 208)], fill=part["primary_col"] + (220,), width=2)
    draw.line([(560, 208), (620, 208)], fill=part["accent_col"] + (120,), width=1)
    
    # Bullet points with custom glowing diamond icons
    f_body = get_font(FONT_ZH_LIGHT, 20)
    f_bold_item = get_font(FONT_ZH_BOLD, 20)
    
    y = 232
    for prefix, text in part["bullets"]:
        draw_diamond(draw, 62, y + 11, 6, fill=part["accent_col"] + (255,), outline=part["accent_col"] + (255,))
        draw.text((80, y), prefix, font=f_bold_item, fill=part["accent_col"] + (255,))
        bbox = draw.textbbox((80, y), prefix, font=f_bold_item)
        draw.text((bbox[2] + 4, y), text, font=f_body, fill=(226, 232, 240, 255))
        y += 42
        
    # Bottom specs card
    draw.rounded_rectangle([52, 386, 560, 448], radius=8, fill=(15, 23, 42, 230), outline=(51, 65, 85, 200), width=1)
    f_footer = get_font(FONT_ZH_LIGHT, 17)
    
    # Draw mini indicator dots
    bx = 70
    colors = [part["primary_col"], (139, 92, 246), part["accent_col"]]
    for i, badge_text in enumerate(part["badges"]):
        draw.ellipse([bx, 413, bx + 8, 421], fill=colors[i % len(colors)] + (255,))
        draw.text((bx + 16, 407), badge_text, font=f_footer, fill=(226, 232, 240, 255))
        w = draw.textbbox((0, 0), badge_text, font=f_footer)[2]
        bx += w + 36
    
    out_path = os.path.join(ASSETS_DIR, f"gateway-{part['index']}-wechat-cover.png")
    im.convert("RGB").save(out_path, "PNG", quality=95)
    print(f"Generated WeChat [{part['index']}]: {out_path}")

def generate_xhs(part):
    width, height = 1080, 1440
    im = Image.new("RGBA", (width, height), (9, 13, 22, 255))
    draw = ImageDraw.Draw(im)
    
    # Background subtle gradient
    for y in range(height):
        ratio = y / height
        r = int(9 + 15 * ratio)
        g = int(13 + 18 * ratio)
        b = int(22 + 35 * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
        
    # Top Tag Pill
    f_pill = get_font(FONT_ZH_BOLD, 24)
    pill_w = 440
    pill_x = (width - pill_w) // 2
    draw.rounded_rectangle([pill_x, 50, pill_x + pill_w, 102], radius=26, fill=part["pill_bg"], outline=part["pill_border"], width=2)
    draw.text((pill_x + 36, 62), f"★ 开发者必备 · HOME-LAB 实战", font=f_pill, fill=(254, 243, 199, 255))
    
    # Big Main Headline
    f_h1 = get_font(FONT_ZH_BOLD, 68)
    draw.text(((width - draw.textbbox((0, 0), part["xhs_h1"], font=f_h1)[2]) // 2, 132), part["xhs_h1"], font=f_h1, fill=(255, 255, 255, 255))
    
    f_h2 = get_font(FONT_ZH_BOLD, 58)
    draw.text(((width - draw.textbbox((0, 0), part["xhs_h2"], font=f_h2)[2]) // 2, 220), part["xhs_h2"], font=f_h2, fill=part["primary_col"] + (255,))
    
    # Subhead pill
    f_sub = get_font(FONT_ZH_BOLD, 28)
    sub_text = part["topic"]
    sub_w = draw.textbbox((0, 0), sub_text, font=f_sub)[2] + 48
    sub_x = (width - sub_w) // 2
    draw.rounded_rectangle([sub_x, 308, sub_x + sub_w, 366], radius=12, fill=(30, 41, 59, 230), outline=(139, 92, 246, 255), width=2)
    draw.text((sub_x + 24, 320), sub_text, font=f_sub, fill=(216, 180, 254, 255))
    
    # Center Image Box (Glassmorphism Card)
    card_x, card_y, card_w, card_h = 48, 396, 984, 520
    draw.rounded_rectangle([card_x - 3, card_y - 3, card_x + card_w + 3, card_y + card_h + 3], radius=20, fill=None, outline=part["primary_col"] + (200,), width=2)
    
    base_path = os.path.join(ASSETS_DIR, part["base_img"])
    if os.path.exists(base_path):
        base = Image.open(base_path).convert("RGBA")
        bw, bh = base.size
        crop_box = (int(bw * 0.05), int(bh * 0.05), int(bw * 0.95), int(bh * 0.95))
        base_cropped = base.crop(crop_box).resize((card_w, card_h), Image.Resampling.LANCZOS)
        
        mask = Image.new("L", (card_w, card_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, card_w, card_h], radius=18, fill=255)
        
        im.paste(base_cropped, (card_x, card_y), mask)
        
    # Card mini title badge
    f_card_badge = get_font(FONT_ZH_BOLD, 20)
    badge_title = part["xhs_card_tag"]
    badge_w = draw.textbbox((0, 0), badge_title, font=f_card_badge)[2] + 36
    badge_x = (width - badge_w) // 2
    draw.rounded_rectangle([badge_x, card_y + card_h - 48, badge_x + badge_w, card_y + card_h - 12], radius=10, fill=(15, 23, 42, 240), outline=part["primary_col"] + (220,), width=1)
    draw.text((badge_x + 18, card_y + card_h - 43), badge_title, font=f_card_badge, fill=(224, 242, 254, 255))
    
    # Bottom 3 Feature Cards
    f_num = get_font(FONT_EN, 24)
    f_ft_title = get_font(FONT_ZH_BOLD, 26)
    f_ft_desc = get_font(FONT_ZH_LIGHT, 20)
    
    fy = 948
    c_h = 108
    for num, title, desc, col in part["xhs_features"]:
        draw.rounded_rectangle([card_x, fy, card_x + card_w, fy + c_h], radius=16, fill=(17, 24, 39, 235), outline=(51, 65, 85, 200), width=1)
        draw.rounded_rectangle([card_x, fy, card_x + 8, fy + c_h], radius=4, fill=col)
        draw.rounded_rectangle([card_x + 28, fy + 24, card_x + 72, fy + 68], radius=8, fill=(30, 41, 59, 255), outline=col, width=1)
        draw.text((card_x + 36, fy + 32), num, font=f_num, fill=col)
        draw.text((card_x + 92, fy + 20), title, font=f_ft_title, fill=(255, 255, 255, 255))
        draw.text((card_x + 92, fy + 60), desc, font=f_ft_desc, fill=(156, 163, 175, 255))
        fy += 124
        
    # Footer
    f_tags = get_font(FONT_ZH_LIGHT, 20)
    tags_text = "#大模型开发  #HomeLab  #APISIX  #AI网关  #架构实战"
    draw.text(((width - draw.textbbox((0, 0), tags_text, font=f_tags)[2]) // 2, 1370), tags_text, font=f_tags, fill=(107, 114, 128, 255))
    
    out_path = os.path.join(ASSETS_DIR, f"gateway-{part['index']}-xhs-cover.png")
    im.convert("RGB").save(out_path, "PNG", quality=95)
    print(f"Generated XHS [{part['index']}]: {out_path}")

def generate_x(part):
    width, height = 1200, 675
    im = Image.new("RGBA", (width, height), (10, 15, 26, 255))
    base_path = os.path.join(ASSETS_DIR, part["base_img"])
    
    if os.path.exists(base_path):
        base = Image.open(base_path).convert("RGBA")
        bw, bh = base.size
        crop_box = (int(bw * 0.12), 0, bw, bh)
        cropped = base.crop(crop_box)
        target_h = height
        target_w = int(cropped.width * (target_h / cropped.height))
        resized = cropped.resize((target_w, target_h), Image.Resampling.LANCZOS)
        
        im.paste(resized, (width - target_w, 0))
        
        grad = Image.new("L", (width, height), 0)
        grad_draw = ImageDraw.Draw(grad)
        for x in range(width):
            if x < 550:
                alpha = 255
            elif x < 880:
                alpha = int(255 * (1.0 - (x - 550) / 330))
            else:
                alpha = 0
            grad_draw.line([(x, 0), (x, height)], fill=alpha)
        
        overlay = Image.new("RGBA", (width, height), (10, 15, 26, 255))
        im = Image.composite(overlay, im, grad)

    draw = ImageDraw.Draw(im)
    
    # English series pill
    f_pill = get_font(FONT_EN, 17)
    draw.rounded_rectangle([60, 56, 400, 94], radius=8, fill=part["pill_bg"], outline=part["pill_border"], width=1)
    draw.text((78, 64), part["en_tag"], font=f_pill, fill=(224, 242, 254, 255))
    
    # Main Title
    f_title = get_font(FONT_ZH_BOLD, 46)
    draw.text((60, 120), part["title"].rstrip("！"), font=f_title, fill=(255, 255, 255, 255))
    
    f_sub = get_font(FONT_ZH_BOLD, 36)
    draw.text((60, 184), part["sub"], font=f_sub, fill=part["primary_col"] + (255,))
    
    f_topic = get_font(FONT_ZH_BOLD, 24)
    draw.text((60, 244), part["x_topic"], font=f_topic, fill=part["accent_col"] + (255,))
    
    draw.line([(60, 296), (620, 296)], fill=part["primary_col"] + (200,), width=2)
    
    # Features List
    f_body = get_font(FONT_ZH_LIGHT, 21)
    f_bold_tag = get_font(FONT_ZH_BOLD, 21)
    
    y = 328
    for prefix, text in part["bullets"]:
        draw_diamond(draw, 72, y + 12, 7, fill=part["primary_col"] + (255,), outline=(224, 242, 254, 255))
        draw.text((92, y), prefix, font=f_bold_tag, fill=part["primary_col"] + (255,))
        w = draw.textbbox((92, y), prefix, font=f_bold_tag)[2]
        draw.text((w, y), text, font=f_body, fill=(226, 232, 240, 255))
        y += 48
        
    # Badges row
    f_badge = get_font(FONT_EN, 15)
    bx = 60
    by = 520
    for b in part["x_badges"]:
        bw = draw.textbbox((0, 0), b, font=f_badge)[2] + 24
        draw.rounded_rectangle([bx, by, bx + bw, by + 36], radius=6, fill=(15, 23, 42, 220), outline=(51, 65, 85, 255), width=1)
        draw.text((bx + 12, by + 9), b, font=f_badge, fill=(148, 163, 184, 255))
        bx += bw + 14
        
    # Footer Author
    f_foot = get_font(FONT_ZH_LIGHT, 16)
    draw.text((60, 592), "Cloud-Neutral Radar · haitao pan (@shenlan)", font=f_foot, fill=(100, 116, 139, 255))
    
    out_path = os.path.join(ASSETS_DIR, f"gateway-{part['index']}-x-cover.png")
    im.convert("RGB").save(out_path, "PNG", quality=95)
    print(f"Generated X [{part['index']}]: {out_path}")

def main():
    for part in PARTS:
        print(f"\n=== Generating covers for Part {part['index']} ===")
        generate_wechat(part)
        generate_xhs(part)
        generate_x(part)
    print("\nAll 15 cover images generated successfully!")

if __name__ == "__main__":
    main()
