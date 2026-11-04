#!/usr/bin/env python3
"""site_check.py — chai 站线上体检（只读）.

检查 chai.aibay.asia 及其姊妹资产（chailive / chaibuddy / AI 代理）是否健康。
设计原则：仅标准库、零第三方依赖、绝不写线上任何内容（体检只读红线）。

用法:
    python3 scripts/site_check.py              # 人类可读表格
    python3 scripts/site_check.py --json       # 机器格式（供 CI / Actions 消费）
    python3 scripts/site_check.py --retry      # 失败项隔 10s 复测一次再定性

退出码: 全部通过 exit 0，任一失败 exit 1；网络异常按 fail 记录，不崩溃。

纪律依据（docs/RULES.md R3「状态定性先复测」）：瞬时抖动 ≠ 站点故障，
单检查项失败先复测一次；复测恢复记 pass 并注明，复测仍挂才算持续故障。
"""

import json
import sys
import time
import urllib.request

TIMEOUT = 15
RETRY_DELAY = 10  # R3 复测间隔（秒）

CHECKS = [
    {"id": "chai-home", "url": "https://chai.aibay.asia/", "expect": "status+title", "desc": "主站首页 200 且含 <title>"},
    {"id": "chailive-home", "url": "https://www.aibay.asia/chailive/", "expect": "status", "desc": "chailive 首页 200"},
    {"id": "chailive-books", "url": "https://www.aibay.asia/chailive/books.html", "expect": "status+riaComplete", "desc": "chailive 书目页 200 且含 riaComplete"},
    {"id": "chaibuddy-home", "url": "https://www.aibay.asia/chaibuddy/", "expect": "status", "desc": "chaibuddy 首页 200"},
    {"id": "chaibuddy-people", "url": "https://www.aibay.asia/chaibuddy/data/people.json", "expect": "status", "desc": "chaibuddy 数据 people.json 200"},
    {"id": "ai-proxy-ping", "url": "https://dopenclaw.aibay.asia/cl2-ai/ping", "expect": "status+ok-true", "desc": "AI 代理健康检查 200 且 ok:true"},
]


def run_check(c, retry=False):
    res = _probe(c)
    if retry and not res["ok"]:
        first_err = res["detail"]
        time.sleep(RETRY_DELAY)
        res2 = _probe(c)
        if res2["ok"]:
            res = res2
            res["detail"] = f"{res['detail']}（复测通过；首轮: {first_err}）"
    return res


def _probe(c):
    start = time.time()
    res = {"id": c["id"], "ok": False, "ms": 0, "detail": ""}
    try:
        req = urllib.request.Request(c["url"], headers={"User-Agent": "site-check/2.0 (+chai workshop)"})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
            body = r.read(65536).decode("utf-8", "replace")
            status = r.status
        ms = int((time.time() - start) * 1000)
        res["ms"] = ms
        if status != 200:
            res["detail"] = f"HTTP {status}"
            return res
        if c["expect"] == "status+title" and "<title" not in body.lower():
            res["detail"] = "200 但未见 <title>"
            return res
        if c["expect"] == "status+riaComplete" and "riaComplete" not in body:
            res["detail"] = "200 但未见 riaComplete"
            return res
        if c["expect"] == "status+ok-true":
            j = json.loads(body)
            if not j.get("ok") is True:
                res["detail"] = f"200 但 ok={j.get('ok')!r}"
                return res
        res["ok"] = True
        res["detail"] = c["desc"] + f"（{len(body)}B）"
    except Exception as e:
        res["ms"] = int((time.time() - start) * 1000)
        res["detail"] = f"异常: {type(e).__name__}: {e}"[:180]
    return res


def main():
    as_json = "--json" in sys.argv
    do_retry = "--retry" in sys.argv
    results = [run_check(c, retry=do_retry) for c in CHECKS]
    overall = "pass" if all(r["ok"] for r in results) else "fail"
    if as_json:
        print(json.dumps({"ts": int(time.time() * 1000), "overall": overall, "checks": results}, ensure_ascii=False, indent=2))
    else:
        print(f"chai 站体检  {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}")
        print("-" * 64)
        for r in results:
            mark = "✓" if r["ok"] else "✗"
            print(f" {mark} {r['id']:<18} {r['ms']:>5}ms  {r['detail']}")
        print("-" * 64)
        n_ok = sum(1 for r in results if r["ok"])
        print(f" 结果: {overall.upper()} （{n_ok}/{len(results)} 项通过）")
    sys.exit(0 if overall == "pass" else 1)


if __name__ == "__main__":
    main()
