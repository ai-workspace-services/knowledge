# 从 Drive 同步新图

整理版文件夹：https://drive.google.com/drive/folders/1GOf7MX28-JpUwWuKjVtbNm7V8HtY1NMO
（子文件夹 `00-总览与索引`、`01-系统演变与复杂度` … `07x-数据基础设施演进概览` … `10-AI时代`，与 `chapters/` 前缀一一对应）

## 方式一：Google Drive 桌面版（推荐）
1. 安装 Google Drive for desktop，登录后在 Finder / 文件管理器中找到整理版文件夹，例如
   - macOS：`~/Library/CloudStorage/GoogleDrive-<账号>/我的云端硬盘/自媒体/图解IT简史-整理版`
   - Linux 可用 rclone 挂载或 `rclone copy` 到本地目录。
2. 在 book-src 下运行：
   ```bash
   make sync DRIVE_DIR="<上面的本地路径>"          # 只新增，不删除、不覆盖
   python3 scripts/sync_drive.py --drive-dir "<路径>" --dry-run   # 先看会加哪些
   ```
3. 脚本按 MD5 去重，新图以 `NNN-原文件名` 存入对应章 `images/`，并在该章 `chapter.md` 末尾追加 `![图注](images/…)`。
4. 打开 chapter.md 调整图注文字和位置，然后 `make check`、`make preview CH=05`。

## 方式二：手动下载
在 Drive 网页里把新图下载到对应章的 `images/`，然后在 `chapter.md` 里自己加一行 `![图注](images/文件名.png)`。
`make check` 会提示「images/ 中未被引用」的图，避免漏加。

注意：sync 不会删除任何文件；Drive 上删掉或改名的图，需要手动在 chapter.md 中处理。
