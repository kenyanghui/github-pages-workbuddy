#!/usr/bin/env python3
"""feedback_pull.py — 网站反馈回流：QQ 邮箱 → ima「网站邮箱信息」目录.

闭环（docs/CLOSED-LOOP.md 反馈回路）：
  网站页脚/QQ 邮箱 ← 读者来信 → 本脚本拉取 → 归档 ima「网站邮箱信息」目录
  → 飞轮周报对账时纳入「读者问得多的」选题信号，驱动下一轮网站迭代。

用法:
    python3 scripts/feedback_pull.py --since 7        # 拉近 7 天反馈（默认）
    python3 scripts/feedback_pull.py --dry-run        # 只列信件不写 ima
    python3 scripts/feedback_pull.py --print-folders  # 列 ima 目录（确认目录名）

数据源优先级:
    1) ima-mcp 连接器（WorkBuddy 内已装，走 MCP 工具调 ima）
    2) ~/.config/ima/feedback.json（一期同款凭证位；邮箱 IMAP 配置换 ~/.config/ima/email.json）

设计原则：仅标准库；邮箱只读（IMAP fetch，绝不删信，红线同 R4 只读精神）；
         首次运行自动在 ima 建目录「网站邮箱信息」（已存在则复用）。
"""

import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMA_DIR_NAME = "网站邮箱信息"
EMAIL_CFG = Path.home() / ".config" / "ima" / "email.json"

DOC_TMPL = """# 反馈 {subject}

- 收件时间: {date}
- 发件人: {from}
- 归档: {ts} 由 feedback_pull.py 自动入库
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


def pull_via_imap(cfg, since_days, dry):
    """QQ 邮箱 IMAP 只读拉取。cfg 需含 host/port/user/password(QQ 授权码)。"""
    import imaplib
    import email
    from email.header import decode_header

    since = time.strftime("%d-%b-%Y", time.gmtime(time.time() - since_days * 86400))
    box = cfg.get("mailbox", "INBOX")
    m = imaplib.IMAP4_SSL(cfg["host"], cfg.get("port", 993))
    m.login(cfg["user"], cfg["password"])
    m.select(box, readonly=True)  # 只读，绝不改邮箱状态
    _, data = m.search(None, f'(SINCE "{since}")')
    msgs = []
    for num in data[0].split():
        _, d = m.fetch(num, "(RFC822)")
        raw = d[0][1]
        msg = email.message_from_bytes(raw)

        def dec(v):
            if not v:
                return ""
            parts = decode_header(v)
            out = ""
            for s, enc in parts:
                if isinstance(s, bytes):
                    out += s.decode(enc or "utf-8", "ignore")
                else:
                    out += s
            return out

        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode(
                        part.get_content_charset() or "utf-8", "ignore")
                    break
        else:
            body = msg.get_payload(decode=True) or b""
            body = body.decode(msg.get_content_charset() or "utf-8", "ignore") if isinstance(body, bytes) else body
        msgs.append({
            "subject": dec(msg.get("Subject", "(无主题)")),
            "from": dec(msg.get("From", "")),
            "date": dec(msg.get("Date", "")),
            "body": body.strip()[:5000],
        })
    m.logout()
    return msgs


def save_via_mcp(msgs, dry):
    """ima-mcp 通道：打印入库指令，由 WorkBuddy 会话内 MCP 工具执行。"""
    for i, msg in enumerate(msgs, 1):
        doc = DOC_TMPL.format(ts=time.strftime("%Y-%m-%d %H:%M"), **msg)
        if dry:
            print(f"[dry-run] 第{i}封 将入 ima/{IMA_DIR_NAME}: {msg['subject'][:30]}")
            continue
        print(f"IMA_UPSERT_DIR={IMA_DIR_NAME}")
        print("IMA_DOC_BEGIN")
        print(json.dumps({"title": f"反馈 {msg['subject'][:40]}", "content": doc}, ensure_ascii=False))
        print("IMA_DOC_END")
    return len(msgs)


def main():
    ap = argparse.ArgumentParser(description="网站反馈回流（QQ 邮箱 → ima 网站邮箱信息）")
    ap.add_argument("--since", type=int, default=7, help="拉取近 N 天（默认 7）")
    ap.add_argument("--dry-run", action="store_true", help="只列不写")
    ap.add_argument("--print-folders", action="store_true", help="列 ima 目录确认目录名")
    args = ap.parse_args()

    if args.print_folders:
        print("请在 WorkBuddy 会话内用 ima-mcp 的列目录工具确认；"
              "目录不存在时首次入库会自动创建「网站邮箱信息」。")
        return

    cfg = load_email_cfg()
    if not cfg:
        print(f"未找到邮箱配置 {EMAIL_CFG}。")
        print("请创建（QQ 邮箱需先在设置开启 IMAP 并生成授权码）：")
        print(json.dumps({"host": "imap.qq.com", "port": 993,
                          "user": "你的QQ号@qq.com", "password": "QQ授权码(非登录密码)",
                          "mailbox": "INBOX"}, ensure_ascii=False, indent=2))
        sys.exit(1)

    msgs = pull_via_imap(cfg, args.since, args.dry)
    if not msgs:
        print(f"近 {args.since} 天无反馈信件。")
        return
    n = save_via_mcp(msgs, args.dry)
    print(f"{'[dry-run] ' if args.dry else ''}共 {n} 封 → ima「{IMA_DIR_NAME}」"
          f"（周报对账时纳入选题信号）" if n else "无信件", file=sys.stderr)


if __name__ == "__main__":
    main()
