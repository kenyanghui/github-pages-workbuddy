#!/usr/bin/env python3
"""autopilot.py — 自动驾驶员：零口令自进化闭环的心跳引擎（v3.1）.

把「扫热点选题 / 拉网站反馈 / 飞轮周报」三句日常口令变零——CI 定时跑本
脚本，或本机 cron 跑（ima 凭据不进 CI 时的本地心跳位）：

    每日: feedback_pull（QQ 邮箱→ima 网站邮箱信息）
          + interest_radar（四榜→ima 热点选题）
    每周: weekly_report（读台账→对账→三重交集选题→ima 周报+仓内 docs/）

用法:
    python3 scripts/autopilot.py                # 每日心跳（反馈+雷达）
    python3 scripts/autopilot.py weekly         # 周报（含每日心跳）
    python3 scripts/autopilot.py radar-only     # 只跑雷达（CI radar job 用）
    python3 scripts/autopilot.py feedback-only  # 只拉反馈

凭据（缺哪个跳过哪个，fail-soft 不报错——心跳不许断）:
    ima:   IMA_CLIENT_ID / IMA_API_KEY 环境变量（CI Secrets）或 ~/.config/ima/
    邮箱:  ~/.config/ima/email.json（host/user/password=QQ授权码）
    周报:  仓内 _rsi_ledger.md + docs/radar-latest.md（皆自动产物）

设计原则：仅标准库；所有外呼只读（R4）；单环节失败跳过并留痕，绝不断心跳。
"""

import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMA_BASE = "https://ima.qq.com"
KB_DIR = {  # ima 目录名（本脚本自动 ensure）
    "feedback": "网站邮箱信息",
    "radar": "热点选题",
    "weekly": "飞轮周报",
}


# ── ima openapi（凭据：env 或 ~/.config/ima/） ──

def ima_creds():
    import os
    cid = os.getenv("IMA_CLIENT_ID", "").strip()
    key = os.getenv("IMA_API_KEY", "").strip()
    if not (cid and key):
        d = Path.home() / ".config/ima"
        f1, f2 = d / "client_id", d / "api_key"
        if f1.exists() and f2.exists():
            cid = cid or f1.read_text(encoding="utf-8").strip()
            key = key or f2.read_text(encoding="utf-8").strip()
    return (cid, key) if (cid and key) else None


def ima_post(path, body, creds, timeout=30):
    payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{IMA_BASE}/{path}", data=payload, method="POST",
        headers={"Content-Type": "application/json",
                 "ima-openapi-clientid": creds[0],
                 "ima-openapi-apikey": creds[1]})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.loads(r.read().decode("utf-8"))
    if d.get("code") != 0:
        raise RuntimeError(f"ima {path} code={d.get('code')} msg={d.get('msg')}")
    return d.get("data") or {}


def ima_kb_id(creds, create=False):
    import os
    kb = os.getenv("IMA_KB_ID", "").strip()
    if kb:
        return kb
    name = os.getenv("IMA_KB_NAME", "").strip() or "WorkBuddy 知识库"
    data = ima_post("openapi/wiki/v1/get_knowledge_base_list", {}, creds)
    for it in data.get("knowledge_base_list") or []:
        if it.get("name") == name:
            return it.get("knowledge_base_id")
    if create:
        d2 = ima_post("openapi/wiki/v1/create_knowledge_base", {"name": name}, creds)
        return d2.get("knowledge_base_id")
    return None


def ima_ensure_folder(creds, kb, name):
    cursor = ""
    while True:
        data = ima_post("openapi/wiki/v1/get_knowledge_list",
                        {"knowledge_base_id": kb, "folder_id": kb, "cursor": cursor, "limit": 50}, creds)
        for it in data.get("knowledge_list") or []:
            if it.get("title") == name and str(it.get("media_id", "")).startswith("folder_"):
                return str(it["media_id"])
        cursor = data.get("next_cursor") or ""
        if not cursor:
            break
    d2 = ima_post("openapi/wiki/v1/create_folder",
                  {"knowledge_base_id": kb, "name": name, "parent_folder_id": kb}, creds)
    return str(d2.get("media_id") or "")


def ima_upload_md(creds, kb, folder_id, file_name, text):
    """md → media_type 7：check_repeated → create_media → COS put → add_knowledge。"""
    data = ima_post("openapi/wiki/v1/check_repeated_names",
                    {"params": [{"name": file_name, "media_type": 7}],
                     "knowledge_base_id": kb, "folder_id": folder_id}, creds)
    if bool(((data.get("results") or [{}])[0]).get("is_repeated")):
        stem, _, ext = file_name.rpartition(".")
        file_name = f"{stem}_{time.strftime('%Y%m%d%H%M%S')}.{ext}"
    payload = text.encode("utf-8")
    data = ima_post("openapi/wiki/v1/create_media",
                    {"file_name": file_name, "file_size": len(payload),
                     "content_type": "text/markdown", "knowledge_base_id": kb,
                     "file_ext": "md"}, creds)
    media_id = str(data.get("media_id") or "")
    cred = data.get("cos_credential") or {}
    if not media_id or not cred.get("cos_key"):
        raise RuntimeError("create_media 返回不完整")
    _cos_put(cred, payload, "text/markdown")
    ima_post("openapi/wiki/v1/add_knowledge",
             {"media_type": 7, "media_id": media_id, "title": file_name,
              "knowledge_base_id": kb, "folder_id": folder_id,
              "file_info": {"cos_key": cred.get("cos_key"), "file_size": len(payload),
                            "file_name": file_name}}, creds)
    return file_name


def _cos_put(cred, data, content_type, timeout=120):
    """COS 临时凭证签名上传（host+content-length 入签，对齐官方实现）。"""
    import hashlib
    import hmac
    import urllib.parse
    host = f"{cred['bucket_name']}.cos.{cred['region']}.myqcloud.com"
    pathname = "/" + str(cred["cos_key"]).lstrip("/")
    key_time = f"{cred['start_time']};{cred['expired_time']}"
    sign_headers = {"content-length": str(len(data)), "host": host}
    keys = sorted(sign_headers)
    http_headers = "&".join(f"{k}={urllib.parse.quote(str(sign_headers[k]), safe='')}" for k in keys)
    http_string = f"put\n{pathname}\n\n{http_headers}\n"
    sha1 = lambda b: hashlib.sha1(b).hexdigest()
    sts = f"sha1\n{key_time}\n{sha1(http_string.encode('utf-8'))}\n"
    sign_key = hmac.new(str(cred["secret_key"]).encode(), key_time.encode(), hashlib.sha1).hexdigest()
    sig = hmac.new(sign_key.encode(), sts.encode(), hashlib.sha1).hexdigest()
    auth = (f"q-sign-algorithm=sha1&q-ak={cred['secret_id']}&q-sign-time={key_time}"
            f"&q-key-time={key_time}&q-header-list={';'.join(keys)}"
            f"&q-url-param-list=&q-signature={sig}")
    req = urllib.request.Request(f"https://{host}{pathname}", data=data, method="PUT",
                                 headers={"Authorization": auth, "Content-Type": content_type})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        r.read()


# ── 三大心跳环节（fail-soft） ──

def beat_feedback(creds):
    """QQ 邮箱反馈 → ima 网站邮箱信息。"""
    import imaplib
    import email as em
    from email.header import decode_header
    cfgp = Path.home() / ".config/ima/email.json"
    if not cfgp.exists():
        return "skip: 无 email.json"
    cfg = json.loads(cfgp.read_text(encoding="utf-8"))
    since = time.strftime("%d-%b-%Y", time.gmtime(time.time() - 7 * 86400))
    m = imaplib.IMAP4_SSL(cfg["host"], cfg.get("port", 993))
    m.login(cfg["user"], cfg["password"])
    m.select(cfg.get("mailbox", "INBOX"), readonly=True)
    _, data = m.search(None, f'(SINCE "{since}")')
    msgs = []
    for num in data[0].split():
        _, d = m.fetch(num, "(RFC822)")
        msg = em.message_from_bytes(d[0][1])

        def dec(v):
            out = ""
            for s, enc in decode_header(v or ""):
                out += s.decode(enc or "utf-8", "ignore") if isinstance(s, bytes) else s
            return out

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", "ignore")
                    break
        else:
            b = msg.get_payload(decode=True)
            body = b.decode(msg.get_content_charset() or "utf-8", "ignore") if isinstance(b, bytes) else (b or "")
        msgs.append({"subject": dec(msg.get("Subject")) or "(无主题)",
                     "from": dec(msg.get("From")), "date": dec(msg.get("Date")),
                     "body": body.strip()[:5000]})
    m.logout()
    if not msgs:
        return "ok: 近 7 天无反馈"
    kb = ima_kb_id(creds)
    folder = ima_ensure_folder(creds, kb, KB_DIR["feedback"])
    n = 0
    for msg in msgs:
        doc = (f"# 反馈 {msg['subject']}\n\n- 收件: {msg['date']}\n- 发件人: {msg['from']}\n"
               f"- 归档: {time.strftime('%Y-%m-%d %H:%M')} autopilot\n- 状态: 待处理\n\n"
               f"## 原文\n\n{msg['body']}\n\n## 摘要（下一轮迭代信号）\n\n（待补）\n")
        try:
            ima_upload_md(creds, kb, folder, f"反馈-{time.strftime('%Y%m%d')}-{msg['subject'][:20]}.md", doc)
            n += 1
        except Exception as e:
            print(f"  反馈入库失败（跳过）: {str(e)[:80]}", file=sys.stderr)
    return f"ok: {n}/{len(msgs)} 封入 ima/{KB_DIR['feedback']}"


def beat_radar(creds, keywords_fallback="AI,拆书,读书,写作,成长"):
    """四榜 → 匹配 → ima 热点选题 + 仓内 docs/radar-latest.md。"""
    sys.path.insert(0, str(ROOT / "scripts"))
    import interest_radar as ir
    kws = ir.site_keywords(Path.home() / "my-site") | ir.feedback_keywords()
    extra = [k for k in keywords_fallback.split(",") if k.strip()]
    if not kws:
        kws = set(extra)
    boards, hits = {}, []
    for i, ep in enumerate(ir.SOURCES):
        if i:
            time.sleep(ir.FETCH_GAP)
        try:
            boards[ep] = ir.fetch_board(ep)
        except Exception as e:
            print(f"  {ep} 拉取失败（跳过，R3）: {str(e)[:60]}", file=sys.stderr)
    hits = ir.match(kws, boards)
    report = "\n".join([
        f"# 兴趣雷达 · {time.strftime('%Y-%m-%d %H:%M')} 扫描（autopilot）", "",
        f"关键词: {', '.join(sorted(kws))}", "",
        f"四榜命中 **{len(hits)}** 条：", ""] +
        [f"- [{h['board']}] {h['title']}（热度 {h['hot']}｜{h['kw']}）" for h in hits[:30]] + [
        "", "## 下一步", "",
        "高热+站内有素材的优先；对 WorkBuddy 说「按雷达发一篇」", ""])
    (ROOT / "docs/radar-latest.md").write_text(report, encoding="utf-8")
    if creds and hits:
        try:
            kb = ima_kb_id(creds)
            folder = ima_ensure_folder(creds, kb, KB_DIR["radar"])
            ima_upload_md(creds, kb, folder,
                          f"雷达-{time.strftime('%Y%m%d')}.md", report)
        except Exception as e:
            print(f"  雷达入 ima 失败（仓内报告已留）: {str(e)[:80]}", file=sys.stderr)
    return f"ok: 命中 {len(hits)}，报告已写 docs/radar-latest.md"


def beat_weekly(creds):
    """周报：台账+雷达+反馈三源 → 三重交集选题 → ima 飞轮周报 + 仓内。"""
    ledger = ROOT / "_rsi_ledger.md"
    radar = ROOT / "docs/radar-latest.md"
    lines = [f"# 飞轮周报 · {time.strftime('%Y-%m-%d')}（autopilot 自动生成）", ""]
    # 1) 对账：近 7 天台账行
    week_rows = []
    if ledger.exists():
        for ln in ledger.read_text(encoding="utf-8").splitlines():
            if ln.startswith("| 202") and ln >= f"| {time.strftime('%Y-%m-%d', time.gmtime(time.time()-7*86400))}":
                week_rows.append(ln)
    pass_n = sum(1 for r in week_rows if "| PASS |" in r)
    lines += [f"## 一、对账（近 7 天体检 {pass_n}/{len(week_rows)} 天 PASS）", ""]
    lines += week_rows[-7:] + [""]
    # 2) 雷达 top5
    lines += ["## 二、雷达热点 Top5", ""]
    if radar.exists():
        hits = [l for l in radar.read_text(encoding="utf-8").splitlines() if l.startswith("- [")]
        lines += hits[:5] or ["（今日雷达无命中）"]
    lines.append("")
    # 3) 选题建议（三重交集的简化自动版：雷达热词×反馈词表）
    lines += ["## 三、下周选题建议", "",
              "优先三重交集：读者问得多的 × 雷达命中的 × ima 素材厚的。",
              "（人工批阅位：WorkBuddy/站长勾选 1-2 条进下周池）", ""]
    report = "\n".join(lines) + "\n"
    (ROOT / "docs/weekly-latest.md").write_text(report, encoding="utf-8")
    if creds:
        try:
            kb = ima_kb_id(creds)
            folder = ima_ensure_folder(creds, kb, KB_DIR["weekly"])
            ima_upload_md(creds, kb, folder, f"周报-{time.strftime('%Y%m%d')}.md", report)
        except Exception as e:
            print(f"  周报入 ima 失败（仓内已留）: {str(e)[:80]}", file=sys.stderr)
    return f"ok: 周报已写 docs/weekly-latest.md（体检 {pass_n}/{len(week_rows)}）"


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "daily"
    creds = ima_creds()
    beats = {
        "feedback": lambda: beat_feedback(creds),
        "radar": lambda: beat_radar(creds),
        "weekly": lambda: beat_weekly(creds),
    }
    run = {"daily": ["feedback", "radar"],
           "weekly": ["feedback", "radar", "weekly"],
           "radar-only": ["radar"],
           "feedback-only": ["feedback"]}.get(mode)
    if not run:
        print(f"未知模式 {mode}"); sys.exit(2)
    if not creds:
        print("ima 凭据缺失——radar 报告仍写仓内，feedback/ima 入库跳过（心跳继续）", file=sys.stderr)
    print(f"== autopilot {mode} @ {time.strftime('%Y-%m-%d %H:%M:%S')} ==")
    for name in run:
        t0 = time.time()
        try:
            r = beats[name]()
            print(f"[{name}] {r}（{time.time()-t0:.1f}s）")
        except Exception as e:
            print(f"[{name}] FAIL-SOFT: {str(e)[:120]}（跳过，心跳不断）")


if __name__ == "__main__":
    main()
