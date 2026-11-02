#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""发文章 — 素材变网站文章 + 公众号粘贴版（双出口）

用法:
  python3 new_post.py --site ~/my-site --title "标题" --file 素材.md
  python3 new_post.py --site ~/my-site --title "标题" --stdin < 素材.md
  echo 素材... | python3 new_post.py --site ~/my-site --title "标题"
"""
import argparse
import html
import json
import re
import sys
import datetime
from pathlib import Path


# ---------- 站点配置 ----------

def load_config(site_dir: Path) -> dict:
    f = site_dir / "config.js"
    if not f.exists():
        print(f"✗ 找不到 {f}——请先跑 setup_wizard.py")
        raise SystemExit(1)
    text = f.read_text(encoding="utf-8")
    m = re.search(r"window\.SITE_CONFIG\s*=\s*(\{.*\})", text, re.S)
    return json.loads(m.group(1))


# ---------- 极简 Markdown → HTML（够用就好，不追求全语法） ----------

INLINE_PATTERNS = [
    (re.compile(r"\*\*(.+?)\*\*"), r"<strong>\1</strong>"),
    (re.compile(r"(?<!\*)\*([^*\n]+)\*(?!\*)"), r"<em>\1</em>"),
    (re.compile(r"`([^`]+)`"), r"<code>\1</code>"),
    (re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)"), r'<a href="\2" target="_blank" rel="noreferrer">\1</a>'),
]


def inline(s: str) -> str:
    s = html.escape(s, quote=False)
    for pat, rep in INLINE_PATTERNS:
        s = pat.sub(rep, s)
    return s


def md_to_html(text: str) -> str:
    out, para, list_open, quote_open, code_open, code_buf = [], [], False, False, False, []
    def flush_para():
        if para:
            out.append("<p>" + " ".join(inline(x) for x in para) + "</p>")
            para.clear()
    def close_list():
        nonlocal list_open
        if list_open:
            out.append("</ul>")
            list_open = False
    def close_quote():
        nonlocal quote_open
        if quote_open:
            out.append("</blockquote>")
            quote_open = False
    for line in text.replace("\r\n", "\n").split("\n"):
        stripped = line.strip()
        if stripped.startswith("```"):
            if code_open:
                out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
                code_buf, code_open = [], False
            else:
                flush_para(); close_list(); close_quote(); code_open = True
            continue
        if code_open:
            code_buf.append(line)
            continue
        if not stripped:
            flush_para(); close_list(); close_quote()
            continue
        m = re.match(r"^(#{1,3})\s+(.*)", stripped)
        if m:
            flush_para(); close_list(); close_quote()
            lvl = len(m.group(1)) + 1  # 站内 h1 是站名，文章从 h2 起
            out.append(f"<h{lvl}>{inline(m.group(2))}</h{lvl}>")
            continue
        if re.match(r"^[-*]\s+", stripped):
            flush_para(); close_quote()
            if not list_open:
                out.append("<ul>")
                list_open = True
            out.append("<li>" + inline(re.sub(r"^[-*]\s+", "", stripped)) + "</li>")
            continue
        if re.match(r"^>\s?", stripped):
            flush_para(); close_list()
            if not quote_open:
                out.append("<blockquote>")
                quote_open = True
            out.append("<p>" + inline(re.sub(r"^>\s?", "", stripped)) + "</p>")
            continue
        close_list(); close_quote()
        para.append(stripped)
    flush_para(); close_list(); close_quote()
    if code_open:
        out.append("<pre><code>" + html.escape("\n".join(code_buf)) + "</code></pre>")
    return "\n".join(out)


# ---------- slug / 摘要 ----------

def make_slug(title: str) -> str:
    s = title.strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"[^\w\u4e00-\u9fff-]", "", s, flags=re.UNICODE)
    return s[:40].strip("-") or "post"


def make_summary(text: str) -> str:
    plain = re.sub(r"\[([^\]]*)\]\((https?://[^)\s]+)\)", r"\1", text)  # 链接只留文字
    plain = re.sub(r"[#>*`\-]", "", plain)
    plain = re.sub(r"\s+", " ", plain).strip()
    return plain[:78] + ("…" if len(plain) > 78 else "")


# ---------- 页面模板 ----------

def article_html(cfg, title, date, body):
    wechat = cfg.get("wechat_account") or ""
    cta = (
        f'<p class="cta">本文出自 <strong>{html.escape(cfg["site_name"])}</strong>'
        + (f" · 微信搜索 <strong>{html.escape(wechat)}</strong> 看更多" if wechat else "")
        + "</p>"
    )
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · {html.escape(cfg['site_name'])}</title>
<link rel="stylesheet" href="../style.css">
<script src="../config.js"></script>
</head>
<body>
<main class="article">
  <nav class="top"><a href="../index.html">← {html.escape(cfg['site_name'])}</a></nav>
  <article>
    <h1 class="post-title">{html.escape(title)}</h1>
    <p class="post-meta">{date} · {html.escape(cfg.get('author', ''))}</p>
{body}
    {cta}
  </article>
  <script>document.title = document.title; </script>
</main>
</body>
</html>
"""


def wechat_html(cfg, title, date, body):
    """公众号粘贴版：全内联样式（公众号编辑器会剥离 class 和外部样式）。
    浏览器打开 → Cmd/Ctrl+A 全选 → 复制 → 粘贴进公众号编辑器。"""

    def inlineify(html_str):
        # 只处理本生成器产出的标签，给常用块级元素加内联样式
        styles = {
            "h2": "margin:28px 0 12px;font-size:19px;font-weight:700;line-height:1.5;",
            "h3": "margin:24px 0 10px;font-size:17px;font-weight:700;line-height:1.5;",
            "h4": "margin:20px 0 8px;font-size:16px;font-weight:700;line-height:1.5;",
            "p": "margin:0 0 16px;font-size:15.5px;line-height:1.9;color:#333;",
            "ul": "margin:0 0 16px;padding-left:22px;",
            "li": "font-size:15.5px;line-height:1.9;color:#333;margin-bottom:6px;",
            "blockquote": "margin:16px 0;padding:10px 14px;border-left:3px solid #999;background:#f7f7f7;",
            "pre": "margin:0 0 16px;padding:12px;background:#f6f8fa;overflow-x:auto;",
            "code": "font-family:Menlo,Consolas,monospace;font-size:14px;",
        }
        for tag, st in styles.items():
            html_str = re.sub(rf"<{tag}>", f'<{tag} style="{st}">', html_str)
            html_str = re.sub(rf'<{tag}(?![ >])', f'<{tag} style="{st}"', html_str)  # 安全兜底
        return html_str

    wechat = cfg.get("wechat_account") or cfg.get("site_name", "")
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>公众号粘贴版 · {html.escape(title)}</title></head>
<body style="max-width:677px;margin:24px auto;padding:0 16px;font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;">
<p style="color:#999;font-size:12px;">使用方法：Cmd/Ctrl+A 全选 → 复制 → 粘贴进公众号编辑器。本文件不要上传到网站。</p>
<hr style="border:none;border-top:1px dashed #ddd;margin:12px 0 24px;">
<h1 style="font-size:21px;font-weight:700;line-height:1.5;margin-bottom:6px;">{html.escape(title)}</h1>
<p style="color:#999;font-size:13px;margin-bottom:24px;">{date} · {html.escape(cfg.get('author',''))}</p>
{inlineify(body)}
<p style="margin-top:28px;padding:12px 16px;background:#f2f6ff;border-radius:8px;font-size:14px;line-height:1.8;">
  本文同步发布于<strong>{html.escape(cfg['site_name'])}</strong>（{html.escape(cfg.get('github_user',''))} 的 GitHub Pages 网站）。<br>
  微信搜索 <strong>{html.escape(wechat)}</strong>，第一时间看到更新。</p>
</body>
</html>
"""


# ---------- posts.js 清单维护 ----------

def update_posts_js(site_dir: Path, entry: dict) -> None:
    f = site_dir / "posts.js"
    posts = []
    if f.exists():
        m = re.search(r"window\.POSTS\s*=\s*(\[.*\])", f.read_text(encoding="utf-8"), re.S)
        if m:
            posts = json.loads(m.group(1))
    posts = [p for p in posts if p.get("slug") != entry["slug"]]
    posts.insert(0, entry)
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)
    f.write_text(
        "/* 自动生成：文章清单。请勿手改，new_post.py 会维护 */\n"
        "window.POSTS = " + json.dumps(posts, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


# ---------- 主流程 ----------

def publish_post(site_dir: Path, title: str, material: str, date=None, slug=None):
    cfg = load_config(site_dir)
    date = date or datetime.date.today().isoformat()
    slug = slug or make_slug(title)
    fname = f"{date}-{slug}.html"
    body = md_to_html(material)

    posts_dir = site_dir / "posts"
    posts_dir.mkdir(exist_ok=True)
    (posts_dir / fname).write_text(article_html(cfg, title, date, body), encoding="utf-8")

    local = site_dir / "_local"
    local.mkdir(exist_ok=True)
    wechat_file = local / f"wechat-{date}-{slug}.html"
    wechat_file.write_text(wechat_html(cfg, title, date, body), encoding="utf-8")

    update_posts_js(site_dir, {
        "title": title, "date": date, "slug": slug,
        "url": f"posts/{fname}", "summary": make_summary(material),
    })
    return {"post": posts_dir / fname, "wechat": wechat_file}


def main():
    ap = argparse.ArgumentParser(description="素材变网站文章 + 公众号粘贴版")
    ap.add_argument("--site", default=str(Path.home() / "my-site"))
    ap.add_argument("--title", required=True)
    ap.add_argument("--file", help="素材 Markdown 文件")
    ap.add_argument("--stdin", action="store_true", help="从管道读素材")
    ap.add_argument("--slug", default=None)
    ap.add_argument("--date", default=None)
    args = ap.parse_args()

    if args.file:
        material = Path(args.file).read_text(encoding="utf-8")
    elif args.stdin or not sys.stdin.isatty():
        material = sys.stdin.read()
    else:
        print("✗ 请用 --file 指定素材文件，或用管道传入（--stdin）")
        raise SystemExit(1)

    result = publish_post(Path(args.site).expanduser(), args.title, material, args.date, args.slug)
    print(f"✓ 网站文章:  {result['post']}")
    print(f"✓ 公众号版:  {result['wechat']}（浏览器打开→全选复制→粘贴进公众号编辑器；勿上传）")
    print(f"✓ 首页清单已更新: {Path(args.site).expanduser() / 'posts.js'}")
    print("下一步：发布（references/publish.md）→ 体检（scripts/diagnose.py）")


if __name__ == "__main__":
    main()
