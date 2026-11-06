#!/usr/bin/env python3
"""feedback_pull.py — 链路 B：网站反馈 → 站长 QQ 邮箱 → ima「网站邮箱信息」.

闭环：网站页脚/文章尾的 QQ 邮箱反馈入口 ← 读者来信 ← 本脚本（WorkBuddy 调用
本技能时执行）IMAP 只读拉取 → 逐封写入 ima「网站邮箱信息」目录（独立新建）
→ 飞轮周报把"待处理"反馈纳入选题，驱动下一轮网站迭代。

用法:
    python3 scripts/feedback_pull.py                # 拉近 7 天 → 直连写 ima
    python3 scripts/feedback_pull.py --since 14     # 拉近 14 天
    python3 scripts/feedback_pull.py --dry-run      # 只列信件不写 ima
    python3 scripts/feedback_pull.py --mirror       # 同时写本地镜像（供雷达提词）

配置（~/.config/ima/email.json，QQ 邮箱需先开 IMAP 并生成授权码）:
    {"host": "imap.qq.com", "port": 993,
     "user": "你的QQ号@qq.com", "password": "QQ授权码(非登录密码)"}

设计原则：仅标准库；邮箱只读（IMAP readonly，绝不删信）；来信原文逐字
保留（R2 证据真实性）；ima 写入走 ima_client.py（独立目录，幂等可重入）。
"""

import argparse
import email as em
import imaplib
import json
import sys
import time
from email.header import decode_header
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ima_client

IMA_DIR_NAME = ima_client.DIR_FEEDBACK  # 「网站邮箱信息」
EMAIL_CFG = Path.home() / ".config" / "ima" / "email.json"
MIRROR = Path.home() / ".config" / "ima" / "feedback-mirror.json"

DOC_TMPL = """# 反馈 {subject}

- 收件时间: {date}
- 发件人: {from}
- 归档: {ts} feedback_pull（链路 B）
- 状态: 待处理

## 原文

{body}

## 摘要（下一轮迭代信号）

（WorkBuddy 补：读者想要什么/哪里坏了/什么值得加）
"""


def load_email_cfg():
    if not EMAIL_CFG.exists():
        return None
    return json.loads(EMAIL_CFG.read_text(encoding="utf-8"))


def pull_via_imap(cfg, since_days):
    """QQ 邮箱 IMAP 只读拉取（readonly，绝不删信）。"""
    since = time.strftime("%d-%b-%Y", time.gmtime(time.time() - since_days * 86400))
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
    return msgs


def save_to_ima(msgs, dry):
    """链路 B 回写：逐封写 ima「网站邮箱信息」目录。"""
    n_ok = 0
    for i, msg in enumerate(msgs, 1):
        doc = DOC_TMPL.format(ts=time.strftime("%Y-%m-%d %H:%M"), **msg)
        fname = f"反馈-{time.strftime('%Y%m%d')}-{msg['subject'][:20]}.md"
        if dry:
            print(f"[dry-run] 第{i}封 将写 ima/{IMA_DIR_NAME}/{fname}")
            n_ok += 1
            continue
        try:
            _, name = ima_client.save_to_dir(IMA_DIR_NAME, fname, doc)
            print(f"  ✓ ima/{IMA_DIR_NAME}/{name}")
            n_ok += 1
        except Exception as e:
            print(f"  ✗ 第{i}封写入失败: {str(e)[:100]}", file=sys.stderr)
    return n_ok


def write_mirror(msgs):
    MIRROR.parent.mkdir(parents=True, exist_ok=True)
    old = []
    if MIRROR.exists():
        try:
            old = json.loads(MIRROR.read_text(encoding="utf-8"))
        except Exception:
            old = []
    seen = {m["subject"] for m in old}
    merged = old + [m for m in msgs if m["subject"] not in seen]
    MIRROR.write_text(json.dumps(merged[-200:], ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  ✓ 本地镜像 {MIRROR}（{len(merged)} 封，雷达提词用）")


def main():
    ap = argparse.ArgumentParser(description="链路 B：QQ 邮箱反馈 → ima 网站邮箱信息")
    ap.add_argument("--since", type=int, default=7, help="拉取近 N 天（默认 7）")
    ap.add_argument("--dry-run", action="store_true", help="只列不写")
    ap.add_argument("--mirror", action="store_true", help="同时写本地镜像（雷达提词）")
    args = ap.parse_args()

    cfg = load_email_cfg()
    if not cfg:
        print(f"未找到邮箱配置 {EMAIL_CFG}。")
        print("请创建（QQ 邮箱需先在设置开启 IMAP 并生成授权码）：")
        print(json.dumps({"host": "imap.qq.com", "port": 993,
                          "user": "你的QQ号@qq.com", "password": "QQ授权码(非登录密码)",
                          "mailbox": "INBOX"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    msgs = pull_via_imap(cfg, args.since)
    if not msgs:
        print(f"近 {args.since} 天无反馈信件。")
        return
    print(f"拉到 {len(msgs)} 封反馈：")
    for m in msgs:
        print(f"  · {m['subject']} ({m['from']})")
    n = save_to_ima(msgs, args.dry_run)
    if args.mirror:
        write_mirror(msgs)
    print(f"{'[dry-run] ' if args.dry_run else ''}共 {n}/{len(msgs)} 封 → ima「{IMA_DIR_NAME}」（周报对账时纳入选题信号）")


if __name__ == "__main__":
    main()
