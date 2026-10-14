#!/usr/bin/env node
const fs = require('fs');
const path = require('path');
const puppeteer = require('puppeteer');
const { marked } = require('marked');
const frontMatter = require('front-matter');
const hljs = require('highlight.js');
const katex = require('katex');

// Find repository root (2 levels up from scripts/pdf)
const REPO_ROOT = path.resolve(__dirname, '../..');

// Matrix category definitions mapping relative glob/path patterns
const CATEGORY_DEFINITIONS = {
  'content-00-global': [
    'content/00-global'
  ],
  'content-security-iac-obs': [
    'content/01-id-security',
    'content/02-iac-devops',
    'content/03-observability'
  ],
  'content-infra-data-workshops': [
    'content/04-infra-platform',
    'content/05-data-ai',
    'content/06-workshops'
  ],
  'content-website': [
    'content/website'
  ],
  'docs-01-console': [
    'docs/01-console'
  ],
  'docs-02-accounts': [
    'docs/02-accounts'
  ],
  'docs-03-rag-server': [
    'docs/03-rag-server'
  ],
  'docs-04-postgresql': [
    'docs/04-postgresql'
  ],
  'docs-guides-zh': [
    'docs/zh'
  ],
  'docs-guides-en': [
    'docs/en'
  ],
  'docs-reference': [
    'docs/reference'
  ],
  'docs-core-and-misc': [
    'docs/get-started',
    'docs/core-concepts',
    'docs/design',
    'docs/integrations',
    'docs/website',
    'docs'
  ],
  'articles-research-threads': [
    'threads',
    'research',
    'platform-registration',
    'products',
    '.'
  ]
};

// Ignore patterns
const IGNORE_PATTERNS = [
  'node_modules',
  '.git',
  '.github',
  'scripts/pdf/node_modules',
  'artifacts',
  '.cmdb-coding',
  '.local-gitops'
];

/**
 * Determine category of a relative file path
 */
function getFileCategory(relPath) {
  const norm = relPath.replace(/\\/g, '/');
  
  // Specific checks first
  if (norm.startsWith('content/00-global/')) return 'content-00-global';
  if (norm.startsWith('content/01-id-security/') || 
      norm.startsWith('content/02-iac-devops/') || 
      norm.startsWith('content/03-observability/')) return 'content-security-iac-obs';
  if (norm.startsWith('content/04-infra-platform/') || 
      norm.startsWith('content/05-data-ai/') || 
      norm.startsWith('content/06-workshops/')) return 'content-infra-data-workshops';
  if (norm.startsWith('content/website/')) return 'content-website';

  if (norm.startsWith('docs/01-console/')) return 'docs-01-console';
  if (norm.startsWith('docs/02-accounts/')) return 'docs-02-accounts';
  if (norm.startsWith('docs/03-rag-server/')) return 'docs-03-rag-server';
  if (norm.startsWith('docs/04-postgresql/')) return 'docs-04-postgresql';
  if (norm.startsWith('docs/zh/')) return 'docs-guides-zh';
  if (norm.startsWith('docs/en/')) return 'docs-guides-en';
  if (norm.startsWith('docs/reference/')) return 'docs-reference';
  if (norm.startsWith('docs/get-started/') || 
      norm.startsWith('docs/core-concepts/') || 
      norm.startsWith('docs/design/') || 
      norm.startsWith('docs/integrations/') || 
      norm.startsWith('docs/website/') || 
      (norm.startsWith('docs/') && !norm.slice(5).includes('/'))) {
    return 'docs-core-and-misc';
  }

  if (norm.startsWith('threads/') || 
      norm.startsWith('research/') || 
      norm.startsWith('platform-registration/') || 
      norm.startsWith('products/') || 
      !norm.includes('/')) {
    return 'articles-research-threads';
  }

  return 'misc';
}

/**
 * Generate systematic series PDF name for a markdown file
 * Example:
 * docs/zh/ai-collaboration-guide/01-cognitive-shift.md
 * -> docs__zh__ai-collaboration-guide__01-cognitive-shift.pdf
 */
function getSeriesPdfName(relPath) {
  const norm = relPath.replace(/\\/g, '/');
  const parts = norm.split('/');
  const fileName = parts.pop();
  
  // Strip .md
  let stem = fileName;
  if (stem.endsWith('.md')) {
    stem = stem.slice(0, -3);
  }

  if (parts.length === 0) {
    return `root__${stem}.pdf`;
  }

  // Join directory parts with double underscore
  const dirPrefix = parts.join('__');
  return `${dirPrefix}__${stem}.pdf`;
}

/**
 * Scan repository for all valid markdown documents
 */
function scanMarkdownFiles(dir = REPO_ROOT, fileList = []) {
  const entries = fs.readdirSync(dir, { withFileTypes: true });
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name);
    const relPath = path.relative(REPO_ROOT, fullPath).replace(/\\/g, '/');

    if (IGNORE_PATTERNS.some(p => relPath === p || relPath.startsWith(p + '/'))) {
      continue;
    }

    if (entry.isDirectory()) {
      scanMarkdownFiles(fullPath, fileList);
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      const stats = fs.statSync(fullPath);
      // Skip 0-byte or trivial stub placeholder files (< 15 bytes)
      if (stats.size >= 15) {
        fileList.push({
          relPath,
          fullPath,
          size: stats.size,
          category: getFileCategory(relPath),
          seriesName: getSeriesPdfName(relPath)
        });
      }
    }
  }
  return fileList;
}

/**
 * Resolve relative markdown images to Base64 Data URLs
 */
function inlineImages(content, mdDir) {
  return content.replace(/!\[([^\]]*)\]\(([^)]+)\)/g, (match, alt, src) => {
    // If already web or data url, keep as is
    if (src.startsWith('http://') || src.startsWith('https://') || src.startsWith('data:')) {
      return match;
    }

    // Strip title if present in link: (image.png "Title")
    const cleanSrc = src.split(' ')[0].trim();
    const resolvedPath = path.resolve(mdDir, cleanSrc);

    if (fs.existsSync(resolvedPath)) {
      try {
        const ext = path.extname(resolvedPath).toLowerCase();
        let mime = 'image/png';
        if (ext === '.jpg' || ext === '.jpeg') mime = 'image/jpeg';
        else if (ext === '.svg') mime = 'image/svg+xml';
        else if (ext === '.gif') mime = 'image/gif';
        else if (ext === '.webp') mime = 'image/webp';

        const b64 = fs.readFileSync(resolvedPath).toString('base64');
        return `![${alt}](data:${mime};base64,${b64})`;
      } catch (err) {
        console.warn(`[WARN] Failed to read image ${resolvedPath}:`, err.message);
      }
    }
    return match;
  });
}

/**
 * Render LaTeX math formulas using KaTeX
 */
function renderMath(content) {
  // Block math: $$ ... $$
  content = content.replace(/\$\$([\s\S]+?)\$\$/g, (match, tex) => {
    try {
      return `<div class="katex-block">${katex.renderToString(tex.trim(), { displayMode: true, throwOnError: false })}</div>`;
    } catch (e) {
      return match;
    }
  });

  // Inline math: $ ... $ (exclude escaped \$ or dollar currency numbers)
  content = content.replace(/(^|[^\\])\$([^\$\n]+?)\$/g, (match, prefix, tex) => {
    // Basic heuristic: skip if looks like pure currency: $100, $5.99
    if (/^\d+(\.\d+)?$/.test(tex.trim())) {
      return match;
    }
    try {
      const rendered = katex.renderToString(tex.trim(), { displayMode: false, throwOnError: false });
      return `${prefix}${rendered}`;
    } catch (e) {
      return match;
    }
  });

  return content;
}

/**
 * Render GitHub alert blocks
 */
function renderAlerts(content) {
  const alertTypes = ['NOTE', 'TIP', 'IMPORTANT', 'WARNING', 'CAUTION'];
  const regex = new RegExp(`> \\[\\!(${alertTypes.join('|')})\\]([\\s\\S]*?)(?=\\n\\n|\\n(?!>)|$)`, 'gi');

  return content.replace(regex, (match, type, text) => {
    const cleanType = type.toUpperCase();
    const cleanText = text.replace(/^> ?/gm, '').trim();
    return `<div class="markdown-alert markdown-alert-${cleanType.toLowerCase()}"><div class="markdown-alert-title"><span class="alert-icon"></span>${cleanType}</div><div class="markdown-alert-content">${cleanText}</div></div>`;
  });
}

/**
 * Configure marked renderer
 */
marked.setOptions({
  gfm: true,
  breaks: false,
  highlight: function(code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      try {
        return hljs.highlight(code, { language: lang }).value;
      } catch (e) {}
    }
    return hljs.highlightAuto(code).value;
  }
});

/**
 * Get KaTeX CSS content
 */
function getKatexCss() {
  try {
    const katexCssPath = require.resolve('katex/dist/katex.min.css');
    return fs.readFileSync(katexCssPath, 'utf8');
  } catch (e) {
    return '';
  }
}

/**
 * Build complete styled HTML document for PDF printing
 */
function buildHtml({ title, seriesName, relPath, meta, bodyHtml }) {
  const katexCss = getKatexCss();
  const breadcrumb = relPath.split('/').slice(0, -1).join(' / ') || 'root';

  return `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <title>${escapeHtml(title)}</title>
  <style>
    ${katexCss}

    @page {
      size: A4;
      margin: 22mm 18mm 22mm 18mm;
    }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Noto Sans CJK SC", "WenQuanYi Micro Hei", sans-serif;
      font-size: 13.5px;
      line-height: 1.68;
      color: #24292f;
      background-color: #ffffff;
      padding: 0;
      margin: 0;
      word-wrap: break-word;
    }

    /* Document Header Card */
    .doc-series-header {
      border: 1px solid #e1e4e8;
      border-left: 4px solid #0969da;
      background-color: #f6f8fa;
      border-radius: 6px;
      padding: 18px 22px;
      margin-bottom: 30px;
    }

    .doc-breadcrumb {
      font-size: 11px;
      font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      color: #57606a;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }

    .doc-main-title {
      font-size: 24px;
      font-weight: 700;
      color: #1f2328;
      margin: 0 0 12px 0;
      line-height: 1.3;
    }

    .doc-meta-row {
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      font-size: 11.5px;
      color: #57606a;
    }

    .meta-badge {
      display: inline-flex;
      align-items: center;
      background: #eaeef2;
      padding: 2px 8px;
      border-radius: 12px;
      font-weight: 500;
    }

    .doc-desc {
      margin-top: 10px;
      font-size: 12.5px;
      color: #57606a;
      border-top: 1px dashed #d0d7de;
      padding-top: 8px;
    }

    /* Headings */
    h1, h2, h3, h4, h5, h6 {
      color: #1f2328;
      font-weight: 600;
      margin-top: 24px;
      margin-bottom: 14px;
      page-break-after: avoid;
      break-after: avoid;
    }

    h1 { font-size: 20px; border-bottom: 1px solid #eaecef; padding-bottom: 6px; }
    h2 { font-size: 17px; border-bottom: 1px solid #eaecef; padding-bottom: 4px; }
    h3 { font-size: 15px; }
    h4 { font-size: 14px; }

    /* Paragraphs and lists */
    p { margin-top: 0; margin-bottom: 14px; }
    ul, ol { padding-left: 24px; margin-top: 0; margin-bottom: 14px; }
    li { margin-bottom: 4px; }

    /* Tables */
    table {
      border-collapse: collapse;
      width: 100%;
      margin: 16px 0;
      page-break-inside: avoid;
      break-inside: avoid;
      font-size: 12.5px;
    }

    th, td {
      border: 1px solid #d0d7de;
      padding: 7px 12px;
      text-align: left;
    }

    th {
      background-color: #f6f8fa;
      font-weight: 600;
    }

    tr:nth-child(even) {
      background-color: #fafbfc;
    }

    /* Code blocks */
    pre {
      background-color: #f6f8fa;
      border: 1px solid #e1e4e8;
      border-radius: 6px;
      padding: 12px 14px;
      overflow-x: auto;
      font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 12px;
      line-height: 1.45;
      page-break-inside: avoid;
      break-inside: avoid;
      margin: 14px 0;
    }

    code {
      font-family: SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace;
      font-size: 85%;
      background-color: rgba(175, 184, 193, 0.2);
      padding: 0.2em 0.4em;
      border-radius: 4px;
    }

    pre code {
      background-color: transparent;
      padding: 0;
      border-radius: 0;
      font-size: 100%;
    }

    /* Blockquotes */
    blockquote {
      border-left: 4px solid #d0d7de;
      padding: 4px 16px;
      color: #57606a;
      margin: 14px 0;
      page-break-inside: avoid;
      break-inside: avoid;
      background: #fafbfc;
    }

    /* Alerts */
    .markdown-alert {
      border-left: 4px solid #0969da;
      padding: 10px 14px;
      margin: 14px 0;
      border-radius: 4px;
      page-break-inside: avoid;
      break-inside: avoid;
      background-color: #f6f8fa;
    }

    .markdown-alert-title {
      font-weight: 600;
      font-size: 12px;
      margin-bottom: 4px;
      display: flex;
      align-items: center;
      gap: 6px;
    }

    .markdown-alert-note { border-left-color: #0969da; background-color: #ddf4ff; }
    .markdown-alert-note .markdown-alert-title { color: #0969da; }

    .markdown-alert-tip { border-left-color: #1a7f37; background-color: #dafbe1; }
    .markdown-alert-tip .markdown-alert-title { color: #1a7f37; }

    .markdown-alert-important { border-left-color: #8250df; background-color: #fbefff; }
    .markdown-alert-important .markdown-alert-title { color: #8250df; }

    .markdown-alert-warning { border-left-color: #9a6700; background-color: #fff8c5; }
    .markdown-alert-warning .markdown-alert-title { color: #9a6700; }

    .markdown-alert-caution { border-left-color: #cf222e; background-color: #ffebe9; }
    .markdown-alert-caution .markdown-alert-title { color: #cf222e; }

    /* Images */
    img {
      max-width: 100%;
      height: auto;
      border-radius: 6px;
      border: 1px solid #e1e4e8;
      display: block;
      margin: 16px auto;
      page-break-inside: avoid;
      break-inside: avoid;
    }

    /* KaTeX math block */
    .katex-block {
      overflow-x: auto;
      margin: 14px 0;
      text-align: center;
      page-break-inside: avoid;
      break-inside: avoid;
    }

    /* Horizontal rule */
    hr {
      height: 1px;
      background-color: #d0d7de;
      border: none;
      margin: 24px 0;
    }
  </style>
</head>
<body>
  <div class="doc-series-header">
    <div class="doc-breadcrumb">📂 ${escapeHtml(breadcrumb)}</div>
    <div class="doc-main-title">${escapeHtml(title)}</div>
    <div class="doc-meta-row">
      <span class="meta-badge">📄 ${escapeHtml(seriesName)}</span>
      ${meta.date ? `<span class="meta-badge">📅 ${escapeHtml(String(meta.date).slice(0, 10))}</span>` : ''}
      ${meta.author ? `<span class="meta-badge">✍️ ${escapeHtml(meta.author)}</span>` : ''}
      ${meta.category ? `<span class="meta-badge">🏷️ ${escapeHtml(meta.category)}</span>` : ''}
      ${meta.lang ? `<span class="meta-badge">🌐 ${escapeHtml(meta.lang.toUpperCase())}</span>` : ''}
    </div>
    ${meta.description ? `<div class="doc-desc">${escapeHtml(meta.description)}</div>` : ''}
  </div>

  <div class="doc-content">
    ${bodyHtml}
  </div>
</body>
</html>`;
}

function escapeHtml(text) {
  if (!text) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Extract Title from frontmatter or Markdown
 */
function extractTitle(fmAttributes, body, fileName) {
  if (fmAttributes && fmAttributes.title) {
    return fmAttributes.title.trim();
  }
  // Try finding first # Heading
  const h1Match = body.match(/^#\s+(.+)$/m);
  if (h1Match) {
    return h1Match[1].trim();
  }
  // Fallback to formatted filename
  return fileName.replace(/\.(zh|en|zh-CN|cn)?\.md$/, '').replace(/[-_]/g, ' ');
}

/**
 * Launch Chromium browser instance
 */
async function launchBrowser(executablePath) {
  const launchOptions = {
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-dev-shm-usage',
      '--disable-gpu',
      '--font-render-hinting=none'
    ]
  };

  if (executablePath && fs.existsSync(executablePath)) {
    launchOptions.executablePath = executablePath;
  } else if (process.platform === 'darwin') {
    const macOSChrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
    if (fs.existsSync(macOSChrome)) {
      launchOptions.executablePath = macOSChrome;
    }
  }

  return await puppeteer.launch(launchOptions);
}

/**
 * Convert a single markdown file to PDF
 */
async function convertFileToPdf(doc, outputDir, browser) {
  const rawContent = fs.readFileSync(doc.fullPath, 'utf8');
  const parsedFm = frontMatter(rawContent);
  const title = extractTitle(parsedFm.attributes, parsedFm.body, path.basename(doc.relPath));

  const mdDir = path.dirname(doc.fullPath);
  let processedMd = parsedFm.body;

  // Process Images, Math and Alerts
  processedMd = inlineImages(processedMd, mdDir);
  processedMd = renderMath(processedMd);
  processedMd = renderAlerts(processedMd);

  const bodyHtml = marked.parse(processedMd);
  const fullHtml = buildHtml({
    title,
    seriesName: doc.seriesName,
    relPath: doc.relPath,
    meta: parsedFm.attributes,
    bodyHtml
  });

  const outPath = path.join(outputDir, doc.seriesName);
  fs.mkdirSync(path.dirname(outPath), { recursive: true });

  const page = await browser.newPage();
  try {
    await page.setContent(fullHtml, {
      waitUntil: 'load',
      timeout: 30000
    });

    const headerTitle = title.length > 50 ? title.substring(0, 48) + '...' : title;

    await page.pdf({
      path: outPath,
      format: 'A4',
      printBackground: true,
      margin: {
        top: '20mm',
        bottom: '20mm',
        left: '16mm',
        right: '16mm'
      },
      displayHeaderFooter: true,
      headerTemplate: `
        <div style="font-size: 8px; color: #8c8c8c; font-family: -apple-system, sans-serif; width: 100%; padding: 0 16mm; display: flex; justify-content: space-between; border-bottom: 0.5px solid #eaecef; padding-bottom: 3px;">
          <span>${escapeHtml(doc.seriesName)}</span>
          <span>${escapeHtml(headerTitle)}</span>
        </div>
      `,
      footerTemplate: `
        <div style="font-size: 8px; color: #8c8c8c; font-family: -apple-system, sans-serif; width: 100%; padding: 0 16mm; display: flex; justify-content: space-between; border-top: 0.5px solid #eaecef; padding-top: 3px;">
          <span>knowledge &middot; ai-workspace-services</span>
          <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
        </div>
      `
    });

    return {
      success: true,
      title,
      relPath: doc.relPath,
      seriesName: doc.seriesName,
      category: doc.category,
      outPath,
      size: fs.statSync(outPath).size
    };
  } catch (err) {
    console.error(`[ERROR] Failed to convert ${doc.relPath}:`, err.message);
    return {
      success: false,
      relPath: doc.relPath,
      error: err.message
    };
  } finally {
    await page.close();
  }
}

/**
 * Generate Master PDF Catalog
 */
function generateCatalog(results, catalogPath) {
  let md = `# Knowledge Base PDF Series Catalog\n\n`;
  md += `> Automatically generated by PDF Matrix Release Pipeline on ${new Date().toISOString().replace('T', ' ').slice(0, 19)} UTC.\n\n`;
  md += `Total Generated PDFs: **${results.filter(r => r.success).length}**\n\n`;

  // Group by category
  const categories = {};
  for (const r of results) {
    if (!r.success) continue;
    if (!categories[r.category]) categories[r.category] = [];
    categories[r.category].push(r);
  }

  for (const [cat, list] of Object.entries(categories)) {
    md += `### Category: \`${cat}\` (${list.length} PDFs)\n\n`;
    md += `| Series PDF Asset Name | Title | Source Document | Size |\n`;
    md += `| :--- | :--- | :--- | :--- |\n`;
    for (const item of list) {
      const sizeKb = (item.size / 1024).toFixed(1) + ' KB';
      md += `| \`${item.seriesName}\` | ${item.title.replace(/\|/g, '\\|')} | \`${item.relPath}\` | ${sizeKb} |\n`;
    }
    md += `\n`;
  }

  fs.mkdirSync(path.dirname(path.resolve(catalogPath)), { recursive: true });
  fs.writeFileSync(catalogPath, md, 'utf8');
  console.log(`[CATALOG] Master catalog written to ${catalogPath}`);
}

/**
 * Compile unified release notes from category catalogs
 */
function compileReleaseNotes({ distDir, tag, title, repo, outputPath }) {
  const catalogsDir = path.join(distDir, 'catalogs');
  const pdfDir = path.join(distDir, 'pdf');
  const bundlesDir = path.join(distDir, 'bundles');

  let totalPdfs = 0;
  const categoryCounts = {};
  if (fs.existsSync(pdfDir)) {
    const cats = fs.readdirSync(pdfDir);
    for (const cat of cats) {
      const catPath = path.join(pdfDir, cat);
      if (fs.statSync(catPath).isDirectory()) {
        const files = fs.readdirSync(catPath).filter(f => f.endsWith('.pdf'));
        categoryCounts[cat] = files.length;
        totalPdfs += files.length;
      }
    }
  }

  let totalBundles = 0;
  if (fs.existsSync(bundlesDir)) {
    totalBundles = fs.readdirSync(bundlesDir).filter(f => f.endsWith('.zip')).length;
  }

  const dateStr = new Date().toISOString().replace('T', ' ').slice(0, 19) + ' UTC';

  let md = `# ${title}\n\n`;
  md += `Automated multi-level directory PDF publication matrix from [\`${repo}\`](https://github.com/${repo}).\n\n`;
  md += `## 📊 Release Summary\n`;
  md += `- **Release Tag**: \`${tag}\`\n`;
  md += `- **Generated Series PDFs**: **${totalPdfs}**\n`;
  md += `- **Category Bundles**: **${totalBundles}**\n`;
  md += `- **Published At**: ${dateStr}\n\n`;

  md += `## 📦 Complete Archive Download\n`;
  md += `- Download all PDFs in one click: [\`knowledge-pdf-complete-collection.zip\`](https://github.com/${repo}/releases/download/${tag}/knowledge-pdf-complete-collection.zip)\n\n`;

  md += `## 📑 Category Directory Breakdown\n`;
  md += `| Category | PDFs | Bundle Archive |\n`;
  md += `| :--- | :--- | :--- |\n`;

  for (const [cat, count] of Object.entries(categoryCounts).sort()) {
    const zipName = `knowledge-pdf-${cat}.zip`;
    md += `| \`${cat}\` | ${count} | [\`${zipName}\`](https://github.com/${repo}/releases/download/${tag}/${zipName}) |\n`;
  }
  md += `\n`;

  md += `## 📚 Document Series Index\n\n`;

  if (fs.existsSync(catalogsDir)) {
    const catFiles = fs.readdirSync(catalogsDir).filter(f => f.endsWith('.md')).sort();
    for (const file of catFiles) {
      const content = fs.readFileSync(path.join(catalogsDir, file), 'utf8');
      const lines = content.split('\n');
      const bodyLines = lines.slice(5).join('\n').trim();
      if (bodyLines) {
        md += bodyLines + '\n\n';
      }
    }
  }

  fs.mkdirSync(path.dirname(path.resolve(outputPath)), { recursive: true });
  fs.writeFileSync(outputPath, md, 'utf8');
  console.log(`[NOTES] Compiled release notes written to ${outputPath} (Total PDFs: ${totalPdfs}, Bundles: ${totalBundles})`);
  return { totalPdfs, totalBundles };
}

/**
 * Main Entry Point
 */
async function main() {
  const args = process.argv.slice(2);
  let categoryFilter = null;
  let fileFilter = null;
  let outputDir = path.resolve(REPO_ROOT, 'output/pdf');
  let catalogPath = path.resolve(REPO_ROOT, 'output/PDF_CATALOG.md');
  let discoverMatrix = false;
  let compileNotesMode = false;
  let distDir = path.resolve(REPO_ROOT, 'dist');
  let releaseTag = 'latest';
  let releaseTitle = 'Knowledge Base PDF Series';
  let repoName = 'ai-workspace-services/knowledge';
  let notesOutput = path.resolve(REPO_ROOT, 'output/RELEASE_NOTES.md');
  let customChrome = process.env.PUPPETEER_EXECUTABLE_PATH || null;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--category' && args[i + 1]) {
      categoryFilter = args[++i];
    } else if (args[i] === '--file' && args[i + 1]) {
      fileFilter = args[++i];
    } else if (args[i] === '--output-dir' && args[i + 1]) {
      outputDir = path.resolve(args[++i]);
    } else if (args[i] === '--catalog' && args[i + 1]) {
      catalogPath = path.resolve(args[++i]);
    } else if (args[i] === '--discover-matrix') {
      discoverMatrix = true;
    } else if (args[i] === '--compile-release-notes') {
      compileNotesMode = true;
    } else if (args[i] === '--dist-dir' && args[i + 1]) {
      distDir = path.resolve(args[++i]);
    } else if (args[i] === '--tag' && args[i + 1]) {
      releaseTag = args[++i];
    } else if (args[i] === '--title' && args[i + 1]) {
      releaseTitle = args[++i];
    } else if (args[i] === '--repo' && args[i + 1]) {
      repoName = args[++i];
    } else if (args[i] === '--notes-output' && args[i + 1]) {
      notesOutput = path.resolve(args[++i]);
    } else if (args[i] === '--executable-path' && args[i + 1]) {
      customChrome = args[++i];
    }
  }

  // If compile release notes mode
  if (compileNotesMode) {
    compileReleaseNotes({
      distDir,
      tag: releaseTag,
      title: releaseTitle,
      repo: repoName,
      outputPath: notesOutput
    });
    return;
  }

  // 1. Scan files
  const allDocs = scanMarkdownFiles();

  // If discover matrix mode
  if (discoverMatrix) {
    const presentCategories = new Set(allDocs.map(d => d.category));
    const matrixList = Object.keys(CATEGORY_DEFINITIONS).filter(c => presentCategories.has(c));
    // Output JSON for GitHub Actions outputs
    console.log(JSON.stringify(matrixList));
    return;
  }

  // Filter documents
  let targetDocs = allDocs;
  if (fileFilter) {
    const normFilter = fileFilter.replace(/\\/g, '/');
    targetDocs = allDocs.filter(d => d.relPath === normFilter || d.relPath.endsWith('/' + normFilter));
  } else if (categoryFilter) {
    targetDocs = allDocs.filter(d => d.category === categoryFilter);
  }

  console.log(`[INFO] Found ${allDocs.length} total docs. Target docs to render: ${targetDocs.length}`);
  if (categoryFilter) console.log(`[INFO] Category: ${categoryFilter}`);

  if (targetDocs.length === 0) {
    console.log('[INFO] No documents to process.');
    return;
  }

  fs.mkdirSync(outputDir, { recursive: true });

  const browser = await launchBrowser(customChrome);
  const results = [];
  const startTime = Date.now();

  try {
    for (let i = 0; i < targetDocs.length; i++) {
      const doc = targetDocs[i];
      console.log(`[${i + 1}/${targetDocs.length}] Converting: ${doc.relPath} -> ${doc.seriesName}`);
      const res = await convertFileToPdf(doc, outputDir, browser);
      results.push(res);
    }
  } finally {
    await browser.close();
  }

  const durationSec = ((Date.now() - startTime) / 1000).toFixed(1);
  const successCount = results.filter(r => r.success).length;
  console.log(`\n========================================`);
  console.log(`[DONE] Rendered ${successCount}/${targetDocs.length} PDFs in ${durationSec}s`);
  console.log(`[OUTPUT] Directory: ${outputDir}`);
  console.log(`========================================\n`);

  if (catalogPath) {
    generateCatalog(results, catalogPath);
  }
}

if (require.main === module) {
  main().catch(err => {
    console.error('[FATAL]', err);
    process.exit(1);
  });
}
