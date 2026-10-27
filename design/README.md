# XWork Technologies 品牌设计与视觉资产库 (Design Assets)

本目录为 **XWork Technologies** 官方品牌识别体系、产品矩阵 Logo、原始矢量 SVG 及设计规范白皮书的终极归档仓。

---

## ⚡ 核心品牌资产一览

| 资产维度 | 适用载体 | 视觉主体 | 核心配色 | 源文件路径 |
| :--- | :--- | :--- | :--- | :--- |
| **🏢 官网 / ORG 身份** | 官网 Header/Footer、GitHub Org、企业控制台 | **2×2 互锁方格 + XWork 字标** | `#0F172A` / `#38BDF8` / `#FFFFFF` | [`svg/xwork-org-mark.svg`](svg/xwork-org-mark.svg)<br>[`svg/xwork-org-lockup-dark.svg`](svg/xwork-org-lockup-dark.svg) |
| **🚀 XConnect APP** | iOS / Android / macOS / Windows / Linux 客户端 | **Swift-Ray (微笑飞鳐 + 脉冲球)** | `#0EA5E9` (极速青) / `#1E1B4B` (深靛) | [`svg/xconnect-swift-ray-light.svg`](svg/xconnect-swift-ray-light.svg)<br>[`svg/xconnect-swift-ray-dark.svg`](svg/xconnect-swift-ray-dark.svg) |
| **🤖 XWorkmate APP** | 协同伴侣、对话 Copilot、IDE 插件、Bot 头像 | **Worky-Bot (大耳罩工伴 + 微笑)** | `#F97316` (暖阳橙) / `#FFF7ED` (奶霜白) | [`svg/xworkmate-worky-bot-light.svg`](svg/xworkmate-worky-bot-light.svg)<br>[`svg/xworkmate-worky-bot-dark.svg`](svg/xworkmate-worky-bot-dark.svg) |
| **🌌 AI Workspace** | 工作空间底座控制台、K8s/Docker 平台印标 | **Cubo-Dock (双灵眸全景母舱)** | `#6366F1` (智境紫) / `#10B981` (灵眸绿) | [`svg/ai-workspace-cubo-dock-light.svg`](svg/ai-workspace-cubo-dock-light.svg)<br>[`svg/ai-workspace-cubo-dock-dark.svg`](svg/ai-workspace-cubo-dock-dark.svg) |

---

## 📁 目录结构

- **[`brand-identity-guidelines.zh.md`](brand-identity-guidelines.zh.md)**: 完整的品牌视觉规范白皮书（双轨制架构、色彩空间、网格、暗黑模式、字体）。
- **`svg/`**: 生产就绪的标准 SVG 矢量底稿（包含 512×512 App 图标、1200×320 横版组合标）。
- **`svg/micro-icons-32x32/`**: 32×32 极限微像素与 Favicon 专用矢量资产。
- **`showcase/`**:
  - `index.html`: 终极定版设计规范全景展板。
  - `logo_matrix_wall.html`: 全景 Logo 矩阵墙（可直接打印导出高清海报）。
  - `wechat_vote.html`: 手机端微信投票调研与辨识度评测 H5。
- **`source-images/`**: 设计演进阶段的原始截图与过程底稿。

---

## 🛠️ 前端快速接入示例

### 1. 替换官网导航栏原有闪电标
```html
<a class="xds-logo flex items-center gap-3" href="/">
  <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
    <rect width="32" height="32" rx="8" fill="#0F172A"/>
    <rect x="5" y="5" width="9.5" height="9.5" rx="2.5" fill="#FFFFFF"/>
    <rect x="17.5" y="5" width="9.5" height="9.5" rx="2.5" fill="#38BDF8"/>
    <rect x="5" y="17.5" width="9.5" height="9.5" rx="2.5" fill="#38BDF8"/>
    <rect x="17.5" y="17.5" width="9.5" height="9.5" rx="2.5" fill="#FFFFFF"/>
  </svg>
  <span class="font-black text-xl text-slate-900 dark:text-white">XWork</span>
  <span class="font-normal text-xl text-slate-500">Technologies</span>
</a>
```

### 2. 本地查看画廊
```bash
# 在当前目录下启动轻量 Web 预览
python3 -m http.server 8080 --directory showcase
# 浏览器访问 http://localhost:8080
```
