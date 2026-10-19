# 《图解 IT 简史》书稿工程（book-src）

以 Markdown + 图片为源，一条命令生成书籍式 PDF（封面 → 关于服务支持方 → 序言 → 总目录 → 各章 → 附录 → 封底广告页）。

**本仓库只收录 Markdown、配置与脚本；章节图片不进 Git。** 克隆后需从 Google Drive 拉图再出 PDF。

整理版 Drive 文件夹：https://drive.google.com/drive/folders/1GOf7MX28-JpUwWuKjVtbNm7V8HtY1NMO  
（子文件夹 `00-总览与索引` … `10-AI时代`，与 `chapters/` 前缀一一对应；详见 `scripts/sync_drive.md`）

```bash
# 示例：Google Drive 桌面版本地路径（按本机账号调整）
make sync DRIVE_DIR="~/Library/CloudStorage/GoogleDrive-<账号>/我的云端硬盘/自媒体/图解IT简史-整理版"
make check && make pdf
```

## 目录
```
book.yml                 书名、版本、日期、作者/服务支持署名、主站、章节顺序、压缩参数、大小上限
front/cover.md           封面要点（{image_count} 自动替换为图片总数）
front/about.md           关于页正文、产品页、邮箱、版权（版本/日期/主站自动取 book.yml）
front/preface.md         序言
front/back-cover.md      封底广告页：标题、一句话介绍、三个产品、主站、底部署名
chapters/NN-slug/chapter.md   章节 front matter（标题/导读/时间线）+ 正文图片 ![图注](images/x.png)
chapters/NN-slug/images/      本章图片（Git 中仅保留 .gitkeep；用 make sync 从 Drive 拉取）
appendix/errata.md, gaps.md   附录 A/B；excluded.yml 未收录的非图片文件清单
scripts/build.py check.py sync_drive.py pack.py common.py fonts.py
dist/                    输出（PDF、预览、zip、缓存），可随时 make clean；已 gitignore
```

## 安装（macOS / Linux）
1. Python 3.9+；`make deps`（= pip install -r requirements.txt，并检查字体）。
2. 字体 Noto Sans CJK SC：macOS `brew install --cask font-noto-sans-cjk-sc`；Debian/Ubuntu `sudo apt install fonts-noto-cjk`。找不到时在 book.yml `fonts:` 写绝对路径。
3. 可选：poppler（pdftoppm）。不需要 Chrome。Makefile 兼容 macOS 自带 GNU make 3.81。

## 常用命令
```
make help                 列出命令
make check                图片链接 / 未引用图片 / 缺字检查
make pdf                  先 check，再出全书 dist/图解IT简史-合集-<version>.pdf 并校验目录、书签、页码
make preview CH=03,05     只出部分章节 → dist/preview-03_05.pdf
make dpi DPI=180          换压缩参数出全书（超过 max_size_mb 会报警告并返回非 0）
make sync DRIVE_DIR=...   从本地 Drive 同步目录新增图片（见 scripts/sync_drive.md）
make zip [NOIMG=1]        打包源文件
make clean
```

## 常见更新
- **加一张图**：把图放进对应章 `images/`（或 `make sync`），在 `chapter.md` 合适位置加一行 `![图注](images/文件名.png)`；`make check && make preview CH=05`。图号按出现顺序自动编号。
- **改文字**：章导读/时间线改 chapter.md 的 front matter；序言、关于页、封底改 front/*.md；署名、主站改 book.yml。chapter.md 正文里也可写普通段落/标题，会排成文字页。
- **新增一章**：建 `chapters/11-xxx/chapter.md`（front matter 至少含 `ch`、`label`、`title`）和 `images/`（放 `.gitkeep`），再把目录名加到 book.yml `chapters:`。
- **调整顺序**：改 book.yml `chapters:` 顺序；章内顺序即 chapter.md 里图片行的顺序。
- **出新版本**：改 book.yml `version`、`edition`、`date`，`make pdf`，新文件不会覆盖旧版。

## 说明
- 长图在空白处自动切分；横图两张拼一页；图片按 dpi/JPEG 质量压缩并缓存于 dist/.cache。
- 字体按实际用字子集化（保留原 GID，保证各类阅读器正常显示）。
