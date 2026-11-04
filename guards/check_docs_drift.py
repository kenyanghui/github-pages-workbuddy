#!/usr/bin/env python3
"""check_docs_drift.py — 文档漂移防护（RULES.md R5 的执行者）.

机制借鉴 loong-workflow guards/check-core-*.ts：README/文档里声称的
「数量、清单、版本」必须与仓库实际内容互相断言，防止文档随演化腐烂。

断言六项（全过 exit 0，任一失败 exit 1 并逐项指出改哪里）:
  1. README「六项体检明细」表 vs site_check.CHECKS 逐项一致（顺序/id/URL）
  2. README 中文数词（六项/七项…）与 CHECKS 实际总数一致
  3. 四个 v1/v2 脚本在磁盘上存在
  4. SKILL.md version 与 README「技能定义 vX.Y.Z」一致
  5. site-ops.yml 存在且 README 提及
  6. docs/RULES.md 六条规则编号（R1–R6）齐全

设计原则：仅标准库、零第三方依赖、只读（不修改任何文件）。
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CN_NUM = {1: "一", 2: "二", 3: "三", 4: "四", 5: "五", 6: "六", 7: "七", 8: "八", 9: "九", 10: "十"}
V1_V2_SCRIPTS = ["setup_wizard.py", "new_post.py", "diagnose.py", "site_check.py"]


def fail(msg):
    print(f"  ✗ {msg}")
    return False


def ok(msg):
    print(f"  ✓ {msg}")
    return True


def load_checks():
    sys.path.insert(0, str(ROOT / "scripts"))
    import site_check
    return site_check.CHECKS


def parse_readme_table(readme):
    rows = []
    in_section = False
    for line in readme.splitlines():
        if line.startswith("## "):
            in_section = "六项体检明细" in line
            continue
        if in_section and line.startswith("| ") and "---" not in line:
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            if len(cells) >= 3 and cells[0].isdigit():
                rows.append({"id": cells[1], "url": cells[2].strip("`")})
    return rows


def main():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    checks = load_checks()
    table = parse_readme_table(readme)
    results = []

    # 1. 体检表逐项一致
    if len(table) != len(checks):
        results.append(fail(f"断言1: README 体检表 {len(table)} 行 ≠ CHECKS {len(checks)} 项——两边数量对齐"))
    else:
        mismatch = [
            f"第{i + 1}行 README({r['id']}, {r['url']}) ≠ CHECKS({c['id']}, {c['url']})"
            for i, (r, c) in enumerate(zip(table, checks)) if r["id"] != c["id"] or r["url"] != c["url"]
        ]
        results.append(ok(f"断言1: 体检表与 CHECKS 逐项一致（{len(checks)} 项）") if not mismatch else fail(f"断言1: " + "; ".join(mismatch)))

    # 2. 中文数词与总数一致
    cn = CN_NUM.get(len(checks), str(len(checks)))
    results.append(ok(f"断言2: README 数词「{cn}项」与 CHECKS 总数 {len(checks)} 一致") if f"{cn}项" in readme else fail(f"断言2: CHECKS 实际 {len(checks)} 项，但 README 找不到「{cn}项」表述——同步措辞"))

    # 3. 脚本存在性
    missing = [s for s in V1_V2_SCRIPTS if not (ROOT / "scripts" / s).exists()]
    results.append(ok(f"断言3: 四脚本齐全 {V1_V2_SCRIPTS}") if not missing else fail(f"断言3: scripts/ 缺 {missing}——README/规则引用了不存在的文件"))

    # 4. SKILL 版本一致
    m_skill = re.search(r"^version:\s*(\S+)", skill, re.MULTILINE)
    m_readme = re.search(r"技能定义\s+(v[\d.]+)", readme)
    if not m_skill or not m_readme:
        results.append(fail(f"断言4: 版本号解析失败（SKILL={'有' if m_skill else '无'}, README={'有' if m_readme else '无'}）"))
    elif m_skill.group(1) == m_readme.group(1).lstrip("v"):
        results.append(ok(f"断言4: SKILL.md version {m_skill.group(1)} == README 技能定义 {m_readme.group(1)}"))
    else:
        results.append(fail(f"断言4: SKILL.md version {m_skill.group(1)} ≠ README 技能定义 {m_readme.group(1)}——两处一起改"))

    # 5. workflow 存在且被 README 提及
    wf = ROOT / ".github" / "workflows" / "site-ops.yml"
    results.append(ok("断言5: site-ops.yml 存在且 README 提及") if wf.exists() and "site-ops.yml" in readme else fail("断言5: site-ops.yml 缺失或 README 未提及"))

    # 6. RULES 六条编号齐全
    rules_path = ROOT / "docs" / "RULES.md"
    if not rules_path.exists():
        results.append(fail("断言6: docs/RULES.md 不存在"))
    else:
        rules_txt = rules_path.read_text(encoding="utf-8")
        missing_rules = [f"R{i}" for i in range(1, 7) if f"## R{i}" not in rules_txt]
        results.append(ok("断言6: RULES.md R1–R6 齐全") if not missing_rules else fail(f"断言6: RULES.md 缺 {missing_rules}"))

    n_ok = sum(1 for r in results if r is True)
    print(f"漂移防护: {'PASS' if all(results) else 'FAIL'} （{n_ok}/{len(results)} 断言通过）")
    sys.exit(0 if all(results) else 1)


if __name__ == "__main__":
    main()
