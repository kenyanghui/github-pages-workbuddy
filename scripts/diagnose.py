#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""网站体检 — 环境 / 站点结构 / 上传安全 / 联动凭证 一站式检查

用法:
  python3 diagnose.py                     # 检查默认站点 ~/my-site
  python3 diagnose.py --site ~/my-site
  python3 diagnose.py --online            # 额外探测线上地址（需网络）
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

OK, BAD, WARN, INFO = "✓", "✗", "！", "·"
results = []


def report(level, msg):
    results.append((level, msg))
    print(f" {level} {msg}")


def check_env():
    v = sys.version_info
    if v >= (3, 8):
        report(OK, f"Python {v.major}.{v.minor}")
    else:
        report(BAD, f"Python {v.major}.{v.minor} 过旧（需 3.8+）")
    git = shutil.which("git")
    report(OK if git else WARN, "git 可用" if git else "git 未安装：可用网页上传通道发布（publish.md 路径 A）")


def parse_js_json(path: Path, varname: str):
    m = re.search(rf"window\.{varname}\s*=\s*(\{{.*\}}|\[.*\])", path.read_text(encoding="utf-8"), re.S)
    return json.loads(m.group(1)) if m else None


def check_site(site: Path):
    if not site.is_dir():
        report(BAD, f"站点目录不存在: {site}（先跑 setup_wizard.py）")
        return None
    report(OK, f"站点目录: {site}")

    need = ["index.html", "config.js", "posts.js", "style.css"]
    ok_all = True
    for name in need:
        if (site / name).exists():
            report(OK, name)
        else:
            report(BAD, f"缺 {name}")
            ok_all = False
    if not ok_all:
        return None

    cfg = parse_js_json(site / "config.js", "SITE_CONFIG")
    if cfg and cfg.get("site_name"):
        report(OK, f"配置读取正常（站名: {cfg['site_name']}）")
    else:
        report(BAD, "config.js 解析失败（SITE_CONFIG 不是合法 JSON）")
        cfg = cfg or {}

    try:
        posts = parse_js_json(site / "posts.js", "POSTS") or []
        report(OK, f"文章清单: {len(posts)} 篇")
        missing = [p.get("url") for p in posts if not (site / p.get("url", "∅")).exists()]
        if missing:
            report(BAD, f"清单指向的文件缺失: {missing}")
        elif posts:
            report(OK, "清单与 posts/ 文件一一对应")
    except (json.JSONDecodeError, AttributeError):
        report(BAD, "posts.js 解析失败（JSON 损坏；重跑 new_post.py 可重建）")

    idx = (site / "index.html").read_text(encoding="utf-8")
    for token in ["config.js", "posts.js"]:
        if token in idx:
            report(OK, f"首页已挂载 {token}")
        else:
            report(BAD, f"首页没有引用 {token}（模板可能被改坏）")
    return cfg


def check_upload_safety(site: Path):
    local = site / "_local"
    if local.is_dir():
        gi = site / ".gitignore"
        ignored = gi.exists() and "_local" in gi.read_text(encoding="utf-8")
        if ignored:
            report(OK, "_local/ 已被 .gitignore 排除（公众号粘贴版不会上传）")
        else:
            report(WARN, "_local/ 存在但 .gitignore 没排除它——用 git 发布前先补一行 `_local/`")
        report(INFO, "网页上传通道请手动跳过 _local 文件夹（里面是公众号粘贴版和台账）")
    gitdir = site / ".git"
    if gitdir.is_dir():
        try:
            remote = subprocess.run(["git", "remote", "-v"], cwd=site, capture_output=True,
                                    text=True, timeout=10).stdout.strip()
            if "github.com" in remote:
                m = re.search(r"github\.com[:/]([^/.\s]+/[^/.\s]+)", remote)
                repo = m.group(1) if m else "?"
                report(OK, f"已连接 GitHub 仓库: {repo}")
                user = repo.split("/")[0]
                report(INFO, f"线上地址（Pages 开启后）: https://{user}.github.io/{repo.split('/')[-1]}/")
            else:
                report(INFO, f"git 远端: {remote or '未设置'}")
        except Exception as e:
            report(WARN, f"git 检查失败: {e}")


def check_online(cfg):
    user = cfg.get("github_user", "")
    repo = cfg.get("repo_name", "")
    if not user or user.startswith("your-"):
        report(INFO, "config 里 GitHub 用户名未填/为演示值，跳过线上探测")
        return
    import urllib.request
    url = f"https://{user}.github.io/{repo}/"
    try:
        with urllib.request.urlopen(url, timeout=15) as r:
            report(OK, f"线上可访问（HTTP {r.status}）: {url}")
    except Exception as e:
        code = getattr(e, "code", None)
        if code == 404:
            report(WARN, f"{url} 还 404：Pages 未开 / 刚提交等 1-5 分钟 / 仓库名不符（publish.md 验证清单）")
        else:
            report(WARN, f"线上探测失败（{e}）——网络问题可忽略，稍后再试")


def check_siblings():
    home = Path.home()
    ima = (home / ".config/ima/client_id").exists()
    wx = (home / ".config/wechat/appid").exists()
    rsi = (home / ".workbuddy/skills/rsi-wechat-publisher").is_dir()
    if ima:
        report(OK, "IMA 凭证已配（第一期复用）：素材可直接查库")
    else:
        report(INFO, "IMA 凭证未配：素材走粘贴通道（flywheel.md § 素材两通道）")
    if wx:
        report(OK, "公众号 API 凭证已配（第一期复用）")
    if rsi:
        report(OK, "兄弟技能 rsi-wechat-publisher 已装：文章出口可升级为 API 推草稿箱")
    else:
        report(INFO, "未装 rsi-wechat-publisher：公众号出口用 _local 粘贴版（够用）")


def main():
    ap = argparse.ArgumentParser(description="网站体检")
    ap.add_argument("--site", default=str(Path.home() / "my-site"))
    ap.add_argument("--online", action="store_true")
    args = ap.parse_args()
    site = Path(args.site).expanduser()

    print("=" * 46)
    print("网站体检 rsi-ima-workbuddy-wechat-web")
    print("=" * 46)
    print("[环境]")
    check_env()
    print("\n[站点]")
    cfg = check_site(site) or {}
    print("\n[上传安全]")
    check_upload_safety(site)
    print("\n[联动（第一期衔接）]")
    check_siblings()
    if args.online:
        print("\n[线上]")
        check_online(cfg)

    fails = [r for r in results if r[0] == BAD]
    print("\n" + "=" * 46)
    if fails:
        print(f"结果：{len(fails)} 项待修复。按上面 ✗ 行逐个处理；卡住就把这份输出发给 WorkBuddy。")
        sys.exit(1)
    print("结果：结构健康。祝写作顺利——库 → 网站 + 公众号，双出口飞轮转起来。")


if __name__ == "__main__":
    main()
