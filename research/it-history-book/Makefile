# 《图解 IT 简史》日常入口（兼容 GNU make 3.81 / macOS 自带 make）
PYTHON  ?= python3
VERSION ?= $(shell sed -n 's/^version:[ ]*//p' book.yml | tr -d "'\"")
OUTPUT   = dist/图解IT简史-合集-$(VERSION).pdf
CH      ?=
DPI     ?=
DRIVE_DIR ?=
DPI_ARG  = $(if $(DPI),--dpi $(DPI),)

.DEFAULT_GOAL := help
.PHONY: help deps check pdf preview dpi sync zip clean

help: ## 列出所有命令
	@echo "用法：make <目标> [变量=值]"
	@echo ""
	@grep -E '^[a-z]+:.*## ' Makefile | sed 's/:.*## /|/' | awk -F'|' '{printf "  %-9s %s\n", $$1, $$2}'
	@echo ""
	@echo "变量：VERSION=$(VERSION)（默认读 book.yml）  CH=03,05  DPI=180  DRIVE_DIR=/path/to/整理版"

deps: ## 安装 Python 依赖并检查字体等
	$(PYTHON) -m pip install -r requirements.txt || $(PYTHON) -m pip install --user --break-system-packages -r requirements.txt
	@$(PYTHON) -c "import sys; sys.path.insert(0,'scripts'); import fonts; print('字体 Regular:', fonts.find('regular')); print('字体 Bold   :', fonts.find('bold'))"
	@command -v pdftoppm >/dev/null 2>&1 && echo "pdftoppm: OK（可选，用于导出预览 PNG）" || echo "pdftoppm: 未安装（可选：brew install poppler / apt install poppler-utils）"
	@echo "Chrome：本工程不需要 Chrome（PDF 由 PyMuPDF 直接排版）。"

check: ## 自检：图片引用、未引用图片、缺字；有 PDF 时校验目录/书签/页码
	$(PYTHON) scripts/check.py --no-pdf

pdf: check ## 生成全书到 dist/图解IT简史-合集-<版本>.pdf，并校验
	$(PYTHON) scripts/build.py --version $(VERSION) --out "$(OUTPUT)" $(DPI_ARG)
	$(PYTHON) scripts/check.py --pdf "$(OUTPUT)"

preview: ## 只生成指定章节：make preview CH=03,05
	@test -n "$(CH)" || (echo "请指定 CH，例如 make preview CH=03,05"; exit 1)
	$(PYTHON) scripts/build.py --chapters $(CH) $(DPI_ARG)

dpi: ## 用指定压缩参数出全书：make dpi DPI=180
	@test -n "$(DPI)" || (echo "请指定 DPI，例如 make dpi DPI=180"; exit 1)
	$(MAKE) pdf DPI=$(DPI)

sync: ## 从本地 Drive 同步目录拷新图（只新增）：make sync DRIVE_DIR=...
	@test -n "$(DRIVE_DIR)" || (echo "请指定 DRIVE_DIR=<Google Drive 本地路径>/图解IT简史-整理版"; exit 1)
	$(PYTHON) scripts/sync_drive.py --drive-dir "$(DRIVE_DIR)"

zip: ## 打包源文件到 dist/book-src.zip（含 images，不含 dist）；NOIMG=1 不含图片
	$(PYTHON) scripts/pack.py $(if $(NOIMG),--no-images,)

clean: ## 清理 dist/ 和缓存
	rm -rf dist scripts/__pycache__
