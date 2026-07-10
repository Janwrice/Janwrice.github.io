#!/usr/bin/env python3
"""
md2post.py — Markdown → 博客文章 HTML 转换器

用法:
    python md2post.py post.md                     # 基本转换
    python md2post.py post.md --date 2026-07-15   # 指定日期
    python md2post.py post.md --no-toc            # 不生成目录侧边栏
    python md2post.py post.md --no-add            # 不自动添加到 posts.js

功能:
    - Markdown → HTML（表格、图片、代码块、嵌套列表等）
    - LaTeX 数学公式（KaTeX 渲染，支持 $...$ 和 $$...$$）
    - 代码高亮（highlight.js）
    - 右侧目录索引（自动从 ## 标题生成）
    - 自动更新 posts.js
"""

import argparse
import os
import re
import sys
import json
from datetime import date
from pathlib import Path

try:
    import markdown
    from markdown.extensions.tables import TableExtension
    from markdown.extensions.fenced_code import FencedCodeExtension
except ImportError:
    print("Error: markdown library required -> pip install markdown")
    sys.exit(1)

# ── 项目根目录（脚本所在目录）──────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
POSTS_DIR = ROOT / "posts"
POSTS_JS = ROOT / "posts.js"

# ── HTML 模板 ──────────────────────────────────────────────────────────

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Janwrice's Blog</title>
    <script>(function(){{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})()</script>
    <link rel="stylesheet" href="../styles.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/styles/atom-one-dark.min.css">
    <style>
        .content-main {{
            padding: 40px 60px 60px;
        }}

        .post-header {{
            margin-bottom: 40px;
        }}

        .post-title {{
            font-size: 32px;
            font-weight: 800;
            color: var(--black);
            letter-spacing: 1px;
            margin-bottom: 12px;
        }}

        .post-meta {{
            font-size: 14px;
            color: var(--gray);
        }}

        .post-body {{
            font-size: 16px;
            line-height: 1.8;
            color: var(--black);
        }}

        .post-body h2 {{
            font-size: 24px;
            font-weight: 700;
            color: var(--black);
            margin: 48px 0 16px;
            padding-bottom: 8px;
            border-bottom: 2px solid var(--blue-light);
            scroll-margin-top: 84px;
        }}

        .post-body h3 {{
            font-size: 18px;
            font-weight: 600;
            color: var(--black);
            margin: 32px 0 12px;
            scroll-margin-top: 84px;
        }}

        .post-body h4 {{
            font-size: 16px;
            font-weight: 600;
            color: var(--black);
            margin: 24px 0 8px;
        }}

        .post-body p {{
            margin: 12px 0;
        }}

        .post-body blockquote {{
            margin: 16px 0;
            padding: 12px 20px;
            border-left: 4px solid var(--blue);
            background-color: var(--blue-light);
            color: var(--black);
            font-size: 15px;
        }}

        .post-body blockquote p {{
            margin: 4px 0;
        }}

        .post-body pre {{
            background-color: var(--code-bg);
            color: var(--code-text);
            padding: 20px 24px;
            border-radius: 8px;
            overflow-x: auto;
            font-size: 14px;
            line-height: 1.6;
            margin: 16px 0;
        }}

        .post-body pre code {{
            background: none;
            padding: 0;
            color: inherit;
            font-size: inherit;
        }}

        .post-body code {{
            font-family: "Cascadia Code", "Fira Code", "JetBrains Mono", "Consolas", monospace;
        }}

        .post-body :not(pre) > code {{
            background-color: var(--inline-code-bg);
            color: var(--inline-code-color);
            padding: 2px 6px;
            border-radius: 4px;
            font-size: 0.9em;
        }}

        .post-body table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 14px;
        }}

        .post-body th,
        .post-body td {{
            padding: 10px 14px;
            text-align: left;
            border: 1px solid var(--gray-light);
        }}

        .post-body th {{
            background-color: var(--blue-light);
            color: var(--blue-dark);
            font-weight: 600;
            font-size: 13px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        .post-body td {{
            background-color: var(--white);
        }}

        .post-body ul,
        .post-body ol {{
            margin: 12px 0;
            padding-left: 28px;
        }}

        .post-body li {{
            margin: 6px 0;
        }}

        .post-body strong {{
            color: var(--blue-dark);
        }}

        .post-body a {{
            color: var(--blue);
            text-decoration: none;
        }}

        .post-body a:hover {{
            text-decoration: underline;
        }}

        .post-body hr {{
            border: none;
            border-top: 1px solid var(--gray-light);
            margin: 48px 0;
        }}

        .post-body img {{
            max-width: 100%;
            border-radius: 8px;
            margin: 16px 0;
        }}

        /* highlight.js 背景覆盖 */
        .post-body pre code.hljs {{
            background: transparent;
            padding: 0;
        }}

        /* KaTeX 公式样式微调 */
        .katex-display {{
            margin: 20px 0;
            overflow-x: auto;
            overflow-y: hidden;
        }}

        .katex {{
            font-size: 1.1em;
        }}

        /* ── 目录侧边栏 ── */
        .toc-sidebar {{
            position: sticky;
            top: 64px;
            height: calc(100vh - 64px);
            overflow-y: auto;
        }}

        .toc-nav {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .toc-nav a {{
            text-decoration: none;
            color: var(--gray);
            font-size: 14px;
            font-weight: 400;
            padding: 8px 12px;
            border-radius: 6px;
            border-left: 2px solid transparent;
            transition: all 0.15s;
        }}

        .toc-nav a:hover {{
            color: var(--blue);
            background-color: var(--blue-light);
        }}

        .toc-nav a.active {{
            color: var(--blue);
            border-left-color: var(--blue);
            background-color: var(--blue-light);
            font-weight: 600;
        }}

        @media (max-width: 768px) {{
            .content-main {{
                padding: 24px 16px !important;
            }}
        }}
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="../index.html" class="navbar-brand"><span>J</span>anwrice</a>
        <div class="navbar-right">
            <ul class="navbar-links">
                <li><a href="../index.html">首页</a></li>
                <li><a href="../blog.html" class="active">博客</a></li>
                <li><a href="../about.html">关于</a></li>
            </ul>
        </div>
    </nav>
    <div class="page-layout">
        <div class="content-main">
            <div class="post-header">
                <h1 class="post-title">{title}</h1>
                <span class="post-meta">{date_str}</span>
            </div>
            <div class="post-body">
{body}
            </div>
        </div>
        <aside class="sidebar toc-sidebar">
            <span class="sidebar-title">目录索引</span>
            <nav class="toc-nav" id="toc-nav">
{toc_links}
            </nav>
        </aside>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
    <script src="https://cdn.jsdelivr.net/gh/highlightjs/cdn-release@11.9.0/build/highlight.min.js"></script>
    <script src="../posts.js"></script>
    <script src="../sidebar.js"></script>
    <script src="../theme.js"></script>
    <script src="../mobile-nav.js"></script>
    <script>
        // ── KaTeX 渲染 ──
        renderMathInElement(document.querySelector('.post-body'), {{
            delimiters: [
                {{left: '$$', right: '$$', display: true}},
                {{left: '$', right: '$', display: false}},
            ],
            throwOnError: false
        }});

        // ── 代码高亮 ──
        hljs.highlightAll();

        // ── 目录滚动高亮 ──
        (function() {{
            var nav = document.getElementById('toc-nav');
            if (!nav) return;
            var links = nav.querySelectorAll('a');
            var headings = [];
            links.forEach(function(a) {{
                var id = a.getAttribute('href');
                if (id && id.startsWith('#')) {{
                    var el = document.getElementById(id.slice(1));
                    if (el) headings.push(el);
                }}
            }});

            window.addEventListener('scroll', function() {{
                var current = '';
                headings.forEach(function(h) {{
                    if (h.getBoundingClientRect().top <= 150) current = h.id;
                }});
                links.forEach(function(a) {{
                    a.classList.toggle('active', a.getAttribute('href') === '#' + current);
                }});
            }});

            nav.addEventListener('click', function(e) {{
                if (e.target.tagName === 'A') {{
                    e.preventDefault();
                    var target = document.getElementById(e.target.getAttribute('href').slice(1));
                    if (target) target.scrollIntoView({{ behavior: 'smooth', block: 'start' }});
                }}
            }});
        }})();
    </script>
</body>
</html>"""


# ── 核心逻辑 ────────────────────────────────────────────────────────────

def protect_math(md_text: str) -> tuple[str, dict[str, str]]:
    """保护 LaTeX 数学公式，避免 markdown 解析器误处理其中的下划线等字符。
    块级公式用 <div> 包裹，防止被 markdown 包进 <p> 标签。"""
    placeholders: dict[str, str] = {}
    counter = [0]

    def save_display(m: re.Match) -> str:
        key = f"%%MATH_{counter[0]}%%"
        placeholders[key] = m.group(0)
        counter[0] += 1
        return f"<div>{key}</div>"

    def save_inline(m: re.Match) -> str:
        key = f"%%MATH_{counter[0]}%%"
        placeholders[key] = m.group(0)
        counter[0] += 1
        return key

    # 先保护 $$...$$（display math）—— 用 <div> 包裹避免被 <p> 包住
    md_text = re.sub(r'\$\$(.+?)\$\$', save_display, md_text, flags=re.DOTALL)
    # 再保护 $...$（inline math）
    md_text = re.sub(r'\$(.+?)\$', save_inline, md_text)

    return md_text, placeholders


def restore_math(html: str, placeholders: dict[str, str]) -> str:
    """将占位符恢复为原始 LaTeX 代码。"""
    for key, val in placeholders.items():
        html = html.replace(key, val)
    return html


def extract_title_and_body(md_text: str) -> tuple[str, str]:
    """从 markdown 中提取第一个 # 标题作为文章标题，其余为正文。"""
    lines = md_text.splitlines()
    title = None
    body_lines = []
    found_h1 = False

    for line in lines:
        if not found_h1 and line.startswith("# ") and not line.startswith("## "):
            title = line[2:].strip()
            found_h1 = True
        else:
            body_lines.append(line)

    if title is None:
        title = "Untitled"

    return title, "\n".join(body_lines)


def generate_toc(body_html: str) -> tuple[str, str]:
    """
    从正文 HTML 中提取所有 <h2> 标题，生成目录导航 HTML，
    同时给每个 <h2> 添加 id 属性。返回 (body_html_with_ids, toc_links_html)。
    """
    toc_entries: list[str] = []
    counter = [0]

    def replace_h2(m: re.Match) -> str:
        counter[0] += 1
        text = m.group(1).strip()
        # 生成 ID：优先用英文部分，否则用数字序号
        slug = slugify(text) or f"section-{counter[0]}"
        toc_entries.append(f'                <a href="#{slug}">{counter[0]}. {escape_html(text)}</a>')
        return f'<h2 id="{slug}">{text}</h2>'

    # 匹配 <h2>...内容...</h2>，内容中可能包含其他 HTML 标签
    body_html = re.sub(
        r'<h2>(.+?)</h2>',
        replace_h2,
        body_html,
        flags=re.DOTALL
    )

    toc_html = "\n".join(toc_entries) if toc_entries else '                <!-- 无二级标题 -->'
    return body_html, toc_html


def slugify(text: str) -> str:
    """将标题文本转为 URL 友好的英文 slug。中文标题返回空字符串。"""
    # 去除 HTML 标签
    text = re.sub(r'<[^>]+>', '', text)
    # 保留字母数字和空格
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', text)
    slug = slug.strip().lower()
    slug = re.sub(r'[\s]+', '-', slug)
    # 如果全是中文（slug 为空），返回空
    return slug if slug else ''


def escape_html(text: str) -> str:
    """HTML 转义（用于 TOC 链接文本中的特殊字符）。"""
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def convert_md_to_html(md_text: str) -> str:
    """将 markdown 文本转换为 HTML。"""
    md = markdown.Markdown(extensions=[
        'tables',
        'fenced_code',
        'sane_lists',
    ])
    return md.convert(md_text)


# ── posts.js 操作 ──────────────────────────────────────────────────────

def update_posts_js(title: str, date_str: str, url: str) -> None:
    """向 posts.js 添加新文章条目（插入到数组最前面）。"""
    if not POSTS_JS.exists():
        print(f"  [WARN] {POSTS_JS} not found, skip update")
        return

    content = POSTS_JS.read_text(encoding='utf-8')

    # 提取 window.__POSTS__ = [...] 中的数组
    match = re.search(r'window\.__POSTS__\s*=\s*(\[[\s\S]*?\]);', content)
    if not match:
        print(f"  [WARN] Cannot parse {POSTS_JS}, skip update")
        return

    try:
        posts = json.loads(match.group(1))
    except json.JSONDecodeError:
        print(f"  [WARN] Cannot parse JSON array in {POSTS_JS}, skip update")
        return

    # 检查是否已存在相同 url
    for p in posts:
        if p.get('url') == url:
            print(f"  [WARN] Post {url} already exists in posts.js, skip")
            return

    new_entry = {"title": title, "date": date_str, "url": url}
    posts.insert(0, new_entry)

    # 格式化输出
    lines = ["window.__POSTS__ = ["]
    for i, p in enumerate(posts):
        comma = "," if i < len(posts) - 1 else ""
        lines.append(f'  {{ "title": {json.dumps(p["title"], ensure_ascii=False)}, "date": "{p["date"]}", "url": "{p["url"]}" }}{comma}')
    lines.append("];")
    lines.append("")

    POSTS_JS.write_text("\n".join(lines), encoding='utf-8')
    print(f"  [OK] Added to {POSTS_JS}")


# ── 交互式确认 ─────────────────────────────────────────────────────────

def confirm_overwrite(filepath: Path) -> bool:
    """如果文件已存在，询问是否覆盖。"""
    if not filepath.exists():
        return True
    answer = input(f"  File {filepath} exists. Overwrite? [y/N] ").strip().lower()
    return answer in ('y', 'yes')


# ── 主入口 ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Markdown → 博客文章 HTML 转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python md2post.py my-post.md
  python md2post.py my-post.md --date 2026-07-15
  python md2post.py my-post.md --slug custom-filename
  python md2post.py my-post.md --no-toc --no-add
        """
    )
    parser.add_argument("input", help="输入的 Markdown 文件路径")
    parser.add_argument("--date", help="文章日期 (YYYY-MM-DD)，默认今天", default=None)
    parser.add_argument("--title", help="文章标题（默认从第一个 # 标题提取）", default=None)
    parser.add_argument("--slug", help="输出文件名（不含 .html），默认从标题生成", default=None)
    parser.add_argument("--no-toc", action="store_true", help="不生成目录侧边栏")
    parser.add_argument("--no-add", action="store_true", help="不自动添加到 posts.js")
    parser.add_argument("--force", "-f", action="store_true", help="覆盖已有文件不询问")

    args = parser.parse_args()

    # ── 读取 Markdown ──
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: file not found -> {input_path}")
        sys.exit(1)

    md_text = input_path.read_text(encoding='utf-8')
    print(f"[READ] {input_path}")

    # ── 保护数学公式 ──
    md_text, math_placeholders = protect_math(md_text)

    # ── 提取标题 ──
    if args.title:
        title = args.title
        body_md = md_text
    else:
        title, body_md = extract_title_and_body(md_text)
    print(f"[TITLE] {title}")

    # ── 确定日期 ──
    date_str = args.date or date.today().isoformat()
    print(f"[DATE] {date_str}")

    # ── 确定输出文件名 ──
    if args.slug:
        slug = args.slug
    else:
        # 从标题生成英文 slug，失败则用日期后缀
        slug = slugify(title) or f"post-{date_str}"
    if not slug.endswith('.html'):
        slug = slug + '.html'
    output_path = POSTS_DIR / slug
    print(f"[OUT] {output_path}")

    # ── 覆盖检查 ──
    if not args.force and not confirm_overwrite(output_path):
        print("Cancelled")
        sys.exit(0)

    # ── Markdown → HTML ──
    body_html = convert_md_to_html(body_md)

    # ── 恢复数学公式 ──
    body_html = restore_math(body_html, math_placeholders)

    # ── 生成 TOC ──
    if args.no_toc:
        body_html_with_ids = body_html
        toc_links = "                <!-- 目录已禁用 -->"
    else:
        body_html_with_ids, toc_links = generate_toc(body_html)
    toc_count = toc_links.count('<a href=')
    print(f"[TOC] {toc_count} entries")

    # ── 渲染完整 HTML ──
    full_html = HTML_TEMPLATE.format(
        title=escape_html(title),
        date_str=date_str,
        body=body_html_with_ids,   # 不额外缩进，避免污染 <pre> 块
        toc_links=toc_links,
    )

    # ── 写入文件 ──
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    output_path.write_text(full_html, encoding='utf-8')
    print(f"[DONE] {output_path}")

    # ── 更新 posts.js ──
    if not args.no_add:
        relative_url = f"posts/{output_path.name}"
        update_posts_js(title, date_str, relative_url)

    print("\nDone! Open the file in a browser to preview.")


if __name__ == "__main__":
    main()
