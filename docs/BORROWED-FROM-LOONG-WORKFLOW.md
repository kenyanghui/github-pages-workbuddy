# 借鉴清单 —— 从 loong-workflow 学什么（2026-11-04）

> 2026-11-04 应站长要求「重新学习 loong-workflow，看能借鉴什么，学到的就实现」。
> 本文是**学习笔记 + 落地对照**：每条写清源出处、学到什么、落到本仓哪个文件。
> 源仓：loong-workflow（内部 SSOT；GitHub 镜像 kenyanghui/loong-workflow，MIT）。

## 源仓是什么

provider 中立的 AI 编程工作流语料：18 个工作流技能 + 23 条行为规则 + 13 份检查清单
+ 2 套模板 + 9 个 JSON Schema + 漂移防护脚本，驱动「任务拆解 → 实现 → 审查 → 验证
→ 发布 → 复盘」环路。本仓是教学资产仓，规模小得多，但它的**纪律机制**可以直接平移。

## 借鉴对照表（六借）

| # | 源机制（出处） | 学到什么 | 本仓落地 |
|---|---|---|---|
| 1 | 规则文件化：每条规则一个 md，头部 L0/L1 分层 + **立规事件复盘互链**（core/rules/verify-external-writes.md 等 23 条） | 规则不是嘴上说说——每条规则有出处（哪次翻车立的规）、有层级（硬门禁 vs 软建议）、有反例 | `docs/RULES.md`（六条规则，全部注明立规事件） |
| 2 | 写后必回读（verify-external-writes，L1） | 「API 返回成功 ≠ 效果成立」——push 后用独立读路径（contents API）回读才记账成功 | `RULES.md` R1；本仓 2026-11-04 README push 曾报 Failure receiving data，contents API 回读证实已推成功 |
| 3 | 展示真实性（presentation-authenticity，L1） | 演示/证据严禁编排或择优：跑挂了就展示挂的样子；结论标记必须与被引内容一致 | `RULES.md` R2 + `evidence.txt` 重构（旧版末尾 EVIDENCE-PASS 与 JSON 块 overall=fail 脱节——正是该规防的事故，反例已存档于文件头） |
| 4 | 状态定性先复测（verify-external-writes 第 5 条） | 外部系统突发 401/超时，隔几分钟复测再定性；瞬时抖动 ≠ 持久故障 | `site_check.py` 新增 `--retry`（单检查项失败自动复测 1 次，间隔 10s）；site-ops.yml CI 侧同款接线 |
| 5 | 漂移防护脚本（guards/check-*.ts，README 数字与 core/ 实际文件数互相断言） | README/文档里的数字会随仓库演化腐烂——用脚本把「文档声称」钉在「实际内容」上 | `guards/check_docs_drift.py`（六项断言：README 六项体检表 vs CHECKS、CHECKS 数、脚本存在性、SKILL 版本号一致性） |
| 6 | 复盘清单化 + 行动项纪律（core/checklists/retrospective.md：行动项 ≤5、必须带文件路径、可度量、无指责） | 复盘的价值在行动项质量：「下次小心」是废纸，「改哪个文件」才是产出 | `docs/retrospectives/TEMPLATE.md`（五段式 GATE/SUCCESS/ACTION/LOOP/SAFE + 行动项四条硬约束） |

## 明确不借的（及为什么）

| 源机制 | 不借原因 |
|---|---|
| 完整 DAG 拆解/多角色流水线（analyze-dag/implement/review-code/verify） | 本仓交付物是模板+脚本，无多人开发环路；一套 site_check + CI 已够 |
| JSON Schema 全家桶 + 术语适配层（adapters/TERMINOLOGY.md） | 面向「可换宿主平台」的语料库才需要；本仓单宿主 |
| 矩阵派发/ZenTao 同步类规则 | 运维对象不同（内部节点 vs 公开教学站） |
| 三层台账（runs/_ledger） | 本仓台账即 `_local/` 个人产物，无多仓状态同步需求 |

## 验证

- `python3 guards/check_docs_drift.py` 六项断言全过（exit 0）
- `python3 scripts/site_check.py --retry` 两轮实跑 6/6（见 evidence.txt 2026-11-04 03:31 UTC）
- CI：site-ops.yml 已加复测步骤 + 漂移防护步骤，push 后在 Actions 页可见
