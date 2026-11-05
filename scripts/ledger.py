#!/usr/bin/env python3
"""ledger.py — 体检结果回流 RSI 台账（docs/CLOSED-LOOP.md 第 5 步的执行者）.

把 site_check --json 的产出增量追加到仓内 `_rsi_ledger.md`，同一家台账
同时服务号与站（「一库一站一号」闭环的闭合点）。

用法:
    python3 scripts/site_check.py --retry --json | python3 scripts/ledger.py
    python3 scripts/ledger.py check-result.json          # 读文件
    python3 scripts/ledger.py --dry-run                  # 只打印待写行，不落盘

设计原则：仅标准库、零第三方依赖；只追加不改历史行（证据真实性 R2）。
"""

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "_rsi_ledger.md"
MAX_ROWS = 500  # 超出时截掉最老的行（保留表头），防台账无限膨胀

HEADER = """# RSI 台账（站侧）

> 一库一站一号闭环的闭合点：chai 站每日体检结果增量回流至此（v2.2 起）。
> 只追加不改历史；生成者 scripts/ledger.py，纪律依据 docs/RULES.md R2/R3。

| 日期 | 结果 | 通过 | 明细（项=ms，复测注明） |
|---|---|---|---|
"""


def load_result(src):
    if src:
        raw = Path(src).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    return json.loads(raw)


def build_row(d):
    ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(d["ts"] / 1000))
    n_ok = sum(1 for c in d["checks"] if c["ok"])
    detail = "；".join(
        f"{'✓' if c['ok'] else '✗'}{c['id']}={c['ms']}ms" + ("（复测）" if "复测" in c["detail"] else "")
        for c in d["checks"]
    )
    return f"| {ts} | {d['overall'].upper()} | {n_ok}/{len(d['checks'])} | {detail} |"


def append(row, dry=False):
    if LEDGER.exists():
        text = LEDGER.read_text(encoding="utf-8").rstrip("\n") + "\n"
    else:
        text = HEADER
    text += row + "\n"
    lines = text.splitlines()
    if len(lines) > MAX_ROWS + len(HEADER.splitlines()):
        keep = len(HEADER.splitlines())
        lines = lines[:keep] + lines[-MAX_ROWS:]
        text = "\n".join(lines) + "\n"
    if dry:
        print(f"[dry-run] 将追加: {row}")
    else:
        LEDGER.write_text(text, encoding="utf-8")
        print(f"已记账 → {LEDGER.name}: {row[:80]}…")


def main():
    args = sys.argv[1:]
    dry = "--dry-run" in args
    src = next((a for a in args if not a.startswith("--")), None)
    d = load_result(src)
    append(build_row(d), dry=dry)


if __name__ == "__main__":
    main()
