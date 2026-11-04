#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fork chaiAI 工作流 — 把讲师站 fork 成你的站

用法:
  python3 fork_chaiai.py --user octocat                # 交互式向导（推荐课堂用）
  python3 fork_chaiai.py --user octocat --demo         # 演示模式（不落盘，只打印计划）
  python3 fork_chaiai.py --user octocat --dir ~/my-chai
动作:
  1. GitHub 网页 fork kenyanghui/chaiAI（本脚本打印直达链接，人点一下）
  2. clone 你的 fork 到本地
  3. 品牌换装（站名/署名/导航，只改 src/data 与 public 根文件，不动组件逻辑）
  4. 推回你的 fork，Actions 自动构建
  5. 打开 用户名.github.io/chaiAI/ 验收
"""
import argparse
import subprocess
import sys
from pathlib import Path

UPSTREAM = "kenyanghui/chaiAI"
DEFAULT_DIR = "~/my-chai"

STEPS = [
    ("0–2′", "fork", "浏览器开 github.com/kenyanghui/chaiAI/fork → 点 Create fork（全默认）",
     "你的 fork：github.com/你/chaiAI ☐"),
    ("2–5′", "clone", "对 WorkBuddy 说「clone 我的 fork」或终端：git clone https://github.com/你/chaiAI.git",
     "本地目录：______"),
    ("5–10′", "换装", "对 WorkBuddy 说「把站换成我的」→ 改站名/署名/导航（src/data/*.js + public/people.json）",
     "新站名：______"),
    ("10–13′", "推回", "git add -A && git commit -m '换装' && git push",
     "已推送 ☐"),
    ("13–15′", "验收", "等 Actions 跑完（1–5 分钟）→ 打开 用户名.github.io/chaiAI/ → 六模块还在、名字已是你的",
     "网址：______"),
]

BRAND_FILES = [
    "src/data/workshops.js",
    "public/people.json",
    "index.html",
]


def run(cmd, cwd=None):
    return subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd,
                          capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser(description="fork chaiAI → 你的站")
    ap.add_argument("--user", required=True, help="你的 GitHub 用户名")
    ap.add_argument("--dir", default=DEFAULT_DIR, help="本地目录（默认 ~/my-chai）")
    ap.add_argument("--demo", action="store_true", help="演示模式：只打印五步计划")
    args = ap.parse_args()

    print(f"\n fork chaiAI · 五步把讲师站变成你的站\n  上游 {UPSTREAM} → github.com/{args.user}/chaiAI\n")
    for t, name, act, chk in STEPS:
        act = act.format(up="chaiAI")
        print(f"  [{t}] {name}\n      {act}\n      凭证：{chk}\n")

    print("  品牌换装只动这三个文件（信息流与组件逻辑不动）：")
    for f in BRAND_FILES:
        print(f"    - {f}")
    print("\n  下一步：说「把站换成我的」进入换装向导；"
          "「用这段素材发篇文章」进产线；联动 ima/公众号见 references/fork-chaiai.md\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
