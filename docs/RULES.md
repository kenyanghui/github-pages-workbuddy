# RULES —— 本仓行为规则

> 借鉴 loong-workflow「规则文件化」机制：每条规则一个编号、注明层级（硬门禁 L1 /
> 软建议 L2）与**立规出处**（哪次事件立的规）。改仓内脚本/文档/CI 前先过这里。
> 机制学习笔记见 [BORROWED-FROM-LOONG-WORKFLOW.md](BORROWED-FROM-LOONG-WORKFLOW.md)。

## R1 · 外部写入回读验证（L1）

**push / API 写操作返回成功 ≠ 效果成立；必须用独立读路径回读后才记账「成功」。**

- git push：回读 = `curl contents API` 比对远端 sha，或本地 `git ls-remote`。
- 只带回执时表述为「已提交，待验证」。
- 立规出处：源规则 loong-workflow `core/rules/verify-external-writes.md`
  （2026-10-06 rsi-wechat 公众号流水线「p2 假成功」事件）。本仓实证：
  2026-11-04 README push 报 `Failure receiving data`，重试显示
  `Everything up-to-date`，contents API 回读证实已推成功——push 回执不可信，
  独立读路径才可信。

## R2 · 展示真实性（L1）

**证据与演示严禁择优或编排：跑挂了就展示挂的样子；结论标记必须与被引内容一致。**

- 证据文件每个块标注实际 exit 码/结论，原文逐字保留、不删不改。
- fail 块不丢弃——按 R3 复测后定性，定性过程留痕。
- 立规出处：源规则 loong-workflow `core/rules/presentation-authenticity.md`。
  本仓反例（已存档 [evidence.txt](../evidence.txt) 文件头）：旧版末尾挂
  `EVIDENCE-PASS` 单标记，而中间 JSON 块实际 `overall: fail`——标记与内容脱节，
  读者无法判断哪个块有效。2026-11-04 重构为逐块标注 + VERDICT 行。

## R3 · 状态定性先复测（L1）

**外部目标突发超时/非 200，先复测一次再定性为持久故障；瞬时抖动 ≠ 站点故障。**

- 脚本侧：`site_check.py --retry` 对单检查项失败自动复测 1 次（间隔 10s），
  复测通过记 pass 且 detail 注明「复测通过」。
- CI 侧：site-ops.yml 先跑 `--retry`；仍 fail 时 workflow 级再复跑一轮，
  两轮全挂才告警。
- 定性口径：复测恢复 = 瞬时抖动（记 detail，不算故障）；复测仍挂 = 持续故障（告警）。
- 立规出处：源规则 `verify-external-writes.md` 第 5 条（Gitea push 401 数分钟后
  自愈事件）。本仓实证：evidence.txt 历史 fail 轮 = SSL 握手抖动，复测即恢复。

## R4 · 体检只读红线（L1）

**site_check / diagnose 对生产站点只发 GET，绝不写线上任何内容。**

- 新增检查项必须保持只读；不得加 POST/DELETE/PUT 探测。
- 立规出处：本仓 site_check.py 模块 docstring（v2 设计原则），本仓原创。

## R5 · 文档数字防漂移（L2）

**README/文档中声称的「数量、清单、版本」必须能被 guards 脚本断言；改了事实必须改文档，改了文档必须过 guard。**

- `python3 guards/check_docs_drift.py` 六项断言：README 体检明细表 vs
  site_check.CHECKS 逐项一致、CHECKS 总数（中文数词联动）、九个脚本存在性、SKILL version 与
  README 一致、workflows 存在、RULES 六条编号齐全。
- CI 已接线（site-ops.yml 漂移防护步，`if: always()` 体检结果不影响其执行）；
  本地改文档后手动跑一次。
- 立规出处：源机制 loong-workflow `guards/check-core-*.ts`（README 数字与
  core/ 实际文件数互相断言）。本仓 2026-11-04 落地。

## R6 · 复盘行动项纪律（L2）

**复盘的价值在行动项质量：每条行动项 ≤5 条总量、必须带具体文件路径、可度量、禁「下次小心」式空话、无指责。**

- 模板：[retrospectives/TEMPLATE.md](retrospectives/TEMPLATE.md)（五段式
  GATE/SUCCESS/ACTION/LOOP/SAFE）。
- 立规出处：源清单 loong-workflow `core/checklists/retrospective.md`
  （ACTION 段四条硬约束 + SAFE 无指责原则）。

## 相关文件

| 文件 | 关系 |
|---|---|
| [BORROWED-FROM-LOONG-WORKFLOW.md](BORROWED-FROM-LOONG-WORKFLOW.md) | 机制的完整学习笔记与落地对照 |
| [../guards/check_docs_drift.py](../guards/check_docs_drift.py) | R5 的执行者 |
| [retrospectives/TEMPLATE.md](retrospectives/TEMPLATE.md) | R6 的模板 |
| [../evidence.txt](../evidence.txt) | R2/R3 的活样本 |
