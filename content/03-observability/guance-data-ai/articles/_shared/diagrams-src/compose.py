from PIL import Image, ImageDraw, ImageFont
import glob, os
CAP = {
 "a1-01-stack-blindspots": "图1｜低成本栈各层都有指标，但用户体验、跨层上下文和数据库内部仍是盲区",
 "a1-02-free-boundary": "图2｜免费空间与合作/商业空间的权限边界（核验日期 2026-10-27，发布前复核）",
 "a1-03-automation-path": "图3｜GitOps 声明 → PR → Terraform → Playbook，Vault 在运行时分开注入凭据",
 "a1-04-evidence-chain": "图4｜一条 UAT 请求的证据链：未实测关联的环节一律标为盲区",
 "a1-05-saas-or-selfhost": "图5｜按“是否需要跨信号/用户视角”和维护成本，决定交给 SaaS 还是继续自建",
 "a2-01-migration-funnel": "图1｜从 Grafana JSON 盘点到 3 个面板，再逐个定性为可迁移/需重写/暂保留",
 "a2-02-query-traps": "图2｜PromQL/LogsQL 到观测云查询的六类语义陷阱，以同窗并排比对为准",
 "a2-03-gitops-hcl": "图3｜监控意图进 Git，renderer 生成 HCL；无 API 权限的空间只做离线生成",
 "a2-04-side-by-side-rollback": "图4｜新旧链路并排对照；配置回退靠 Git + plan/apply，数据回退靠原始存储",
}
font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 30, index=2)  # SC
def wrap(d, text, maxw):
    lines, cur = [], ""
    for ch in text:
        if d.textlength(cur+ch, font=font) > maxw: lines.append(cur); cur = ch
        else: cur += ch
    return lines+[cur]
def make(raw, name, W, H=None):
    im = Image.open(raw).convert("RGB")
    pad = 50; maxw = W-2*pad
    tmp = ImageDraw.Draw(Image.new("RGB",(10,10)))
    lines = wrap(tmp, CAP[name], maxw); caph = 46*len(lines)+30
    if H is None:
        s = min(1.0, maxw/im.width); im = im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS)
        Hc = im.height+2*pad+caph
    else:
        avail = H-2*pad-caph; s = min(maxw/im.width, avail/im.height, 1.0)
        im = im.resize((int(im.width*s), int(im.height*s)), Image.LANCZOS); Hc = H
    c = Image.new("RGB",(W,Hc),"white"); d = ImageDraw.Draw(c)
    top = pad if H is None else pad+(Hc-2*pad-caph-im.height)//2
    c.paste(im, ((W-im.width)//2, top))
    y = top+im.height+24
    d.line([(pad,y),(W-pad,y)], fill="#E4E7EB", width=2); y += 14
    for l in lines:
        d.text(((W-d.textlength(l,font=font))//2, y), l, font=font, fill="#3E4C59"); y += 46
    return c
for raw in sorted(glob.glob("src/*.raw.png")):
    name = os.path.basename(raw).replace(".raw.png","")
    make(raw, name, 1080).save(f"{name}-wechat.png")
    make(raw, name, 1080, 1440).save(f"{name}-xhs.png")
    print(name)
