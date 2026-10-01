import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ASSETS_DIR = "/Users/shenlan/workspaces/ai-workspace-service/knowledge/assets/images"
BASE_IMG_PATH = os.path.join(ASSETS_DIR, "gateway-01-selection-cover.jpg")
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

# -------------------------------------------------------------
# 1. WeChat Official Account Cover (1200 x 510, 2.35:1)
# -------------------------------------------------------------
def create_wechat_cover():
    width, height = 1200, 510
    im = Image.new("RGBA", (width, height), (10, 14, 24, 255))
    
    if os.path.exists(BASE_IMG_PATH):
        base = Image.open(BASE_IMG_PATH).convert("RGBA")
        bw, bh = base.size
        # Crop center-right portion focusing on glowing hub
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
    draw.rounded_rectangle([52, 44, 350, 78], radius=8, fill=(14, 116, 144, 210), outline=(56, 189, 248, 255), width=1)
    draw.text((68, 50), "HOME-LAB 实战 · 01 选型篇", font=f_pill, fill=(224, 242, 254, 255))
    
    # Main Title
    f_title = get_font(FONT_ZH_BOLD, 42)
    draw.text((52, 98), "再也不用多账号切换了！", font=f_title, fill=(255, 255, 255, 255))
    
    # Subtitle
    f_sub = get_font(FONT_ZH_BOLD, 32)
    draw.text((52, 154), "搭建个人专属全能 AI 聚合网关", font=f_sub, fill=(56, 189, 248, 255))
    
    # Glowing divider line
    draw.line([(52, 208), (560, 208)], fill=(56, 189, 248, 220), width=2)
    draw.line([(560, 208), (620, 208)], fill=(139, 92, 246, 120), width=1)
    
    # Bullet points with custom glowing diamond icons
    f_body = get_font(FONT_ZH_LIGHT, 20)
    f_bold_item = get_font(FONT_ZH_BOLD, 20)
    
    bullets = [
        ("单入口收敛：", "Codex / Claude / Gemini / Antigravity 零心智接入"),
        ("架构深抉择：", "为什么选 APISIX Standalone 彻底弃用 Kong？"),
        ("极简轻量化：", "0 外部数据库与 etcd · 纯 GitOps 文件驱动交付"),
    ]
    
    y = 232
    for prefix, text in bullets:
        draw_diamond(draw, 62, y + 11, 6, fill=(245, 158, 11, 255), outline=(251, 191, 36, 255))
        draw.text((80, y), prefix, font=f_bold_item, fill=(251, 191, 36, 255))
        bbox = draw.textbbox((80, y), prefix, font=f_bold_item)
        draw.text((bbox[2] + 4, y), text, font=f_body, fill=(226, 232, 240, 255))
        y += 42
        
    # Bottom specs card
    draw.rounded_rectangle([52, 386, 540, 448], radius=8, fill=(15, 23, 42, 230), outline=(51, 65, 85, 200), width=1)
    f_footer = get_font(FONT_ZH_LIGHT, 17)
    
    # Draw mini indicator dots
    draw.ellipse([70, 413, 78, 421], fill=(56, 189, 248, 255))
    draw.text((86, 407), "双层鉴权", font=f_footer, fill=(226, 232, 240, 255))
    
    draw.ellipse([190, 413, 198, 421], fill=(139, 92, 246, 255))
    draw.text((206, 407), "单 Token 解耦", font=f_footer, fill=(226, 232, 240, 255))
    
    draw.ellipse([345, 413, 353, 421], fill=(16, 185, 129, 255))
    draw.text((361, 407), "统一 HTTPS 路由", font=f_footer, fill=(226, 232, 240, 255))
    
    out_path = os.path.join(ASSETS_DIR, "gateway-01-wechat-cover.png")
    im.convert("RGB").save(out_path, "PNG", quality=95)
    print("Saved WeChat Cover:", out_path)

# -------------------------------------------------------------
# 2. Xiaohongshu Cover (1080 x 1440, 3:4)
# -------------------------------------------------------------
def create_xhs_cover():
    width, height = 1080, 1440
    im = Image.new("RGBA", (width, height), (9, 13, 22, 255))
    
    draw = ImageDraw.Draw(im)
    
    # Subtle background gradient/vignette
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
    draw.rounded_rectangle([pill_x, 50, pill_x + pill_w, 102], radius=26, fill=(180, 83, 9, 230), outline=(245, 158, 11, 255), width=2)
    draw.text((pill_x + 36, 62), "★ 开发者必备 · HOME-LAB 提效", font=f_pill, fill=(254, 243, 199, 255))
    
    # Big Main Headline
    f_h1 = get_font(FONT_ZH_BOLD, 68)
    draw.text(((width - draw.textbbox((0, 0), "告别多账号切换！", font=f_h1)[2]) // 2, 132), "告别多账号切换！", font=f_h1, fill=(255, 255, 255, 255))
    
    f_h2 = get_font(FONT_ZH_BOLD, 58)
    draw.text(((width - draw.textbbox((0, 0), "全能 AI 聚合网关搭建指南", font=f_h2)[2]) // 2, 220), "全能 AI 聚合网关搭建指南", font=f_h2, fill=(56, 189, 248, 255))
    
    # Subhead pill
    f_sub = get_font(FONT_ZH_BOLD, 28)
    sub_text = "【第 01 篇 选型篇】Kong vs APISIX 终极抉择"
    sub_w = draw.textbbox((0, 0), sub_text, font=f_sub)[2] + 48
    sub_x = (width - sub_w) // 2
    draw.rounded_rectangle([sub_x, 308, sub_x + sub_w, 366], radius=12, fill=(30, 41, 59, 230), outline=(139, 92, 246, 255), width=2)
    draw.text((sub_x + 24, 320), sub_text, font=f_sub, fill=(216, 180, 254, 255))
    
    # Center Image Box (Glassmorphism Card)
    card_x, card_y, card_w, card_h = 48, 396, 984, 520
    draw.rounded_rectangle([card_x - 3, card_y - 3, card_x + card_w + 3, card_y + card_h + 3], radius=20, fill=None, outline=(56, 189, 248, 200), width=2)
    
    if os.path.exists(BASE_IMG_PATH):
        base = Image.open(BASE_IMG_PATH).convert("RGBA")
        bw, bh = base.size
        # Crop balanced view
        crop_box = (int(bw * 0.05), int(bh * 0.05), int(bw * 0.95), int(bh * 0.95))
        base_cropped = base.crop(crop_box).resize((card_w, card_h), Image.Resampling.LANCZOS)
        
        # Round corner mask for the embedded picture
        mask = Image.new("L", (card_w, card_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([0, 0, card_w, card_h], radius=18, fill=255)
        
        im.paste(base_cropped, (card_x, card_y), mask)
        
    # Card mini title badge
    f_card_badge = get_font(FONT_ZH_BOLD, 20)
    badge_title = "网关流量中枢 · 聚合 OpenAI / Claude / Gemini / Antigravity"
    badge_w = draw.textbbox((0, 0), badge_title, font=f_card_badge)[2] + 36
    badge_x = (width - badge_w) // 2
    draw.rounded_rectangle([badge_x, card_y + card_h - 48, badge_x + badge_w, card_y + card_h - 12], radius=10, fill=(15, 23, 42, 240), outline=(56, 189, 248, 220), width=1)
    draw.text((badge_x + 18, card_y + card_h - 43), badge_title, font=f_card_badge, fill=(224, 242, 254, 255))
    
    # Bottom 3 Feature Cards
    features = [
        ("01", "统一入口 · 零心智接入", "单一 HTTPS 域名 + 单网关 Token，CLI、IDE 与 SDK 彻底免折腾", (56, 189, 248)),
        ("02", "选型断舍离 · 极简架构", "彻底摒弃庞大 DB 与 etcd，APISIX Standalone 纯 GitOps 文件驱动", (245, 158, 11)),
        ("03", "开源自由 · 无商业枷锁", "内置开源 ai-proxy-multi，多账号与官方 Key 智能分流探活", (139, 92, 246)),
    ]
    
    f_num = get_font(FONT_EN, 24)
    f_ft_title = get_font(FONT_ZH_BOLD, 26)
    f_ft_desc = get_font(FONT_ZH_LIGHT, 20)
    
    fy = 948
    card_h = 108
    for num, title, desc, col in features:
        # Background card
        draw.rounded_rectangle([card_x, fy, card_x + card_w, fy + card_h], radius=16, fill=(17, 24, 39, 235), outline=(51, 65, 85, 200), width=1)
        
        # Left color bar
        draw.rounded_rectangle([card_x, fy, card_x + 8, fy + card_h], radius=4, fill=col)
        
        # Number badge
        draw.rounded_rectangle([card_x + 28, fy + 24, card_x + 72, fy + 68], radius=8, fill=(30, 41, 59, 255), outline=col, width=1)
        draw.text((card_x + 36, fy + 32), num, font=f_num, fill=col)
        
        # Title & desc
        draw.text((card_x + 92, fy + 20), title, font=f_ft_title, fill=(255, 255, 255, 255))
        draw.text((card_x + 92, fy + 60), desc, font=f_ft_desc, fill=(156, 163, 175, 255))
        
        fy += 124
        
    # Footer
    f_tags = get_font(FONT_ZH_LIGHT, 20)
    tags_text = "#大模型开发  #HomeLab  #APISIX  #ClaudeCode  #架构实战"
    draw.text(((width - draw.textbbox((0, 0), tags_text, font=f_tags)[2]) // 2, 1370), tags_text, font=f_tags, fill=(107, 114, 128, 255))
    
    out_path = os.path.join(ASSETS_DIR, "gateway-01-xhs-cover.png")
    im.convert("RGB").save(out_path, "PNG", quality=95)
    print("Saved XHS Cover:", out_path)

# -------------------------------------------------------------
# 3. X (Twitter) Article Cover (1200 x 675, 16:9)
# -------------------------------------------------------------
def create_x_cover():
    width, height = 1200, 675
    im = Image.new("RGBA", (width, height), (10, 15, 26, 255))
    
    if os.path.exists(BASE_IMG_PATH):
        base = Image.open(BASE_IMG_PATH).convert("RGBA")
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
    draw.rounded_rectangle([60, 56, 400, 94], radius=8, fill=(14, 116, 144, 210), outline=(56, 189, 248, 255), width=1)
    draw.text((78, 64), "AI AGGREGATOR GATEWAY · PART 01", font=f_pill, fill=(224, 242, 254, 255))
    
    # Main Title
    f_title = get_font(FONT_ZH_BOLD, 46)
    draw.text((60, 120), "再也不用多账号切换了", font=f_title, fill=(255, 255, 255, 255))
    
    f_sub = get_font(FONT_ZH_BOLD, 36)
    draw.text((60, 184), "全能 AI 聚合网关搭建指南", font=f_sub, fill=(56, 189, 248, 255))
    
    f_topic = get_font(FONT_ZH_BOLD, 24)
    draw.text((60, 244), "选型篇：Kong vs APISIX Standalone 深度抉择", font=f_topic, fill=(245, 158, 11, 255))
    
    draw.line([(60, 296), (620, 296)], fill=(56, 189, 248, 200), width=2)
    
    # Features List
    f_body = get_font(FONT_ZH_LIGHT, 21)
    f_bold_tag = get_font(FONT_ZH_BOLD, 21)
    
    items = [
        ("统一接入", "单一 HTTPS 入口 + 单一网关 Token，全工具链无感对接"),
        ("拒绝沉重", "摒弃 DB 与 etcd 控制面依赖，极简 GitOps 文件驱动"),
        ("开源自由", "原生支持 ai-proxy-multi，多模型智能分流与熔断降级"),
    ]
    
    y = 328
    for tag, desc in items:
        draw_diamond(draw, 72, y + 12, 7, fill=(56, 189, 248, 255), outline=(224, 242, 254, 255))
        draw.text((92, y), tag + " · ", font=f_bold_tag, fill=(56, 189, 248, 255))
        w = draw.textbbox((92, y), tag + " · ", font=f_bold_tag)[2]
        draw.text((w, y), desc, font=f_body, fill=(226, 232, 240, 255))
        y += 48
        
    # Badges row
    badges = ["GitOps Declarative", "Zero-DB Runtime", "Multi-Account CPA", "Production Hardened"]
    f_badge = get_font(FONT_EN, 15)
    bx = 60
    by = 520
    for b in badges:
        bw = draw.textbbox((0, 0), b, font=f_badge)[2] + 24
        draw.rounded_rectangle([bx, by, bx + bw, by + 36], radius=6, fill=(15, 23, 42, 220), outline=(51, 65, 85, 255), width=1)
        draw.text((bx + 12, by + 9), b, font=f_badge, fill=(148, 163, 184, 255))
        bx += bw + 14
        
    # Footer Author
    f_foot = get_font(FONT_ZH_LIGHT, 16)
    draw.text((60, 592), "Cloud-Neutral Radar · haitao pan (@shenlan)", font=f_foot, fill=(100, 116, 139, 255))
    
    out_path = os.path.join(ASSETS_DIR, "gateway-01-x-cover.png")
    im.convert("RGB").save(out_path, "PNG", quality=95)
    print("Saved X/Twitter Cover:", out_path)

if __name__ == "__main__":
    create_wechat_cover()
    create_xhs_cover()
    create_x_cover()
