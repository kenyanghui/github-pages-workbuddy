#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""个人网站初始化向导 — rsi-ima-workbuddy-wechat-web

用法:
  python3 setup_wizard.py                 # 交互式，7 个问题
  python3 setup_wizard.py --demo          # 演示模式，全默认值 + 欢迎文章
  python3 setup_wizard.py --dir ~/my-site # 指定站点目录
"""
import argparse
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TPL_DIR = SKILL_DIR / "templates" / "site-minimal"

DEMO = {
    "site_name": "我的拆书笔记",
    "tagline": "把读过的书，拆成能用的招",
    "author": "爱读书的小白",
    "wechat_account": "我的公众号",
    "github_user": "your-github-username",
    "repo_name": "my-site",
    "feedback_email": "your-qq@example.com",
}

QUESTIONS = [
    ("site_name", "站名（别人第一眼看到的名字，如：老王读书笔记）"),
    ("tagline", "一句话简介（这个站是干嘛的，如：把读过的书，拆成能用的招）"),
    ("author", "署名/笔名（文章落款用）"),
    ("wechat_account", "公众号名（联动用，没有直接回车）"),
    ("github_user", "GitHub 用户名（还没注册就回车，之后可改）"),
    ("repo_name", "GitHub 仓库名（回车默认 my-site）"),
    ("feedback_email", "QQ 邮箱（网站反馈入口展示用，读者来信回流 ima「网站邮箱信息」目录）"),
]


def ask(answers: dict, demo: bool) -> dict:
    print("=" * 46)
    print("个人网站初始化向导（共 7 个问题，回车可用默认值）")
    print("=" * 46)
    for key, prompt in QUESTIONS:
        default = DEMO[key] if demo else ""
        if key == "repo_name":
            default = default or "my-site"
        if demo:
            answers[key] = default
            print(f"{prompt}\n  → {default}")
            continue
        while key == "site_name" and not (answers.get(key) or default):
            val = input(f"{prompt}: ").strip()
            if val:
                answers[key] = val
                break
            print("  站名不能为空，再想一个～")
        else:
            if key == "site_name" and not answers.get(key):
                continue
            val = input(f"{prompt} [{default}]: ").strip()
            answers[key] = val or default
    return answers


def render_config(cfg: dict) -> str:
    import json
    body = json.dumps(cfg, ensure_ascii=False, indent=2)
    return (
        "/* 站点配置 — 本文件由向导生成，可手动微调 */\n"
        "/* 网站所有页面都会读这里：改站名/简介/公众号，只改这一个文件 */\n"
        f"window.SITE_CONFIG = {body}\n"
    )


def scaffold(target: Path, cfg: dict) -> None:
    if target.exists() and any(target.iterdir()):
        print(f"✗ 目录 {target} 已存在且不为空。换个位置请用 --dir，或先备份旧目录。")
        sys.exit(1)
    target.mkdir(parents=True)
    for item in TPL_DIR.rglob("*"):
        if "__pycache__" in item.parts:
            continue
        rel = item.relative_to(TPL_DIR)
        dest = target / rel
        if item.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        if rel.name == "config.js":
            dest.write_text(render_config(cfg), encoding="utf-8")
        else:
            dest.write_bytes(item.read_bytes())
    print(f"✓ 站点已生成: {target}")
    print(f"  首页: {target / 'index.html'}  （双击即可在浏览器打开）")


def main() -> None:
    ap = argparse.ArgumentParser(description="个人网站初始化向导")
    ap.add_argument("--dir", default=None, help="站点目录（默认 ~/my-site）")
    ap.add_argument("--demo", action="store_true", help="演示模式：全默认值 + 一篇欢迎文章")
    args = ap.parse_args()

    target = Path(args.dir).expanduser() if args.dir else Path.home() / DEMO["repo_name"]
    cfg = ask({}, args.demo)
    cfg["created"] = __import__("datetime").date.today().isoformat()

    scaffold(target, cfg)

    if args.demo:
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        from new_post import publish_post
        publish_post(
            site_dir=target,
            title="欢迎来到我的网站",
            material=(
                "这是演示文章。可以删掉它：删 posts/ 里对应文件后重跑向导即可。\n\n"
                "## 这个站怎么用\n\n"
                "1. 把 ima 里攒的素材（笔记、摘录、想法）交给 WorkBuddy\n"
                "2. 说「用这段素材帮我在网站上发一篇文章」\n"
                "3. 技能生成网站文章 + 公众号粘贴版，双出口同时更\n\n"
                "> 素材从库里来，文章到站和号去——这就是一库一站一号。"
            ),
        )

    print()
    print("下一步：")
    print(f"  1. 双击打开 {target / 'index.html'} 预览")
    print("  2. 发布上线：对 WorkBuddy 说「发布网站」，或看 references/publish.md")
    print("  3. 体检：python3 scripts/diagnose.py --site " + str(target))


if __name__ == "__main__":
    main()
