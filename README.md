# rsi-ima-workbuddy-wechat-web

> **第二期工作坊主仓**：把你的 IMA 知识库变成「站 + 号」双阵地——GitHub Pages 网站、公众号内容、chai 站自动化工作流，一个 RSI 自进化闭环全管。
> 蓝本即真实运营的 [chai.aibay.asia](https://chai.aibay.asia/)：工作坊现场照着拆的就是这套东西。

## 一句话定位

- **一期（rsi-ima-workbuddy-wechatpub）管「号」**：IMA 知识库 → 公众号内容工厂，九步流水线日更三篇进草稿箱，绝不自动群发。
- **二期（本仓）管「站」**：WorkBuddy 直接操作 GitHub——建站、发布、体检、定时巡检，同一个 RSI 范式从「号」扩展到「站」。

```
        ┌────────────────────────────┐
        │     IMA 知识库（库·源头）    │
        └─────────┬─────────┬────────┘
       WorkBuddy（一期·号）  WorkBuddy（二期·站）
                  ▼         ▼
          公众号草稿箱      GitHub Pages 网站
          （日更三篇）      （打开就能看的家）
                  └────┬────┘
                       ▼
              site_check 每日体检（本仓 v2）
```

## 核心能力

| 能力 | 组件 | 状态 |
|---|---|---|
| **fork 讲师站（v3 主线）** | `scripts/fork_chaiai.py` 五步向导 + `references/fork-chaiai.md`（fork chaiAI→换装→控信息流→ima/号联动不受影响） | 已交付（v3） |
| 建站 | `scripts/setup_wizard.py` 向导 + `templates/site-minimal` 单文件模板（config.js/index.html/posts.js/style.css，零依赖双击可开） | 已交付（v1） |
| 发文 | `scripts/new_post.py "标题"` 生成文章 → push main → Actions 自动上线 | 已交付（v1） |
| 诊断 | `scripts/diagnose.py` 环境自检（技能是否装好、依赖是否齐） | 已交付（v1） |
| 站点体检 | `scripts/site_check.py` 六项只读检查，支持 `--json`（exit 0=全过，供 CI 判定）与 `--retry`（失败项隔 10s 复测一次再定性） | 已交付（v2.1） |
| 定时巡检 | `.github/workflows/site-ops.yml` 每日 09:17（北京时间）自动体检，首轮 fail 隔 60s 二轮复测，两轮全挂才告警 | 已交付（v2.1） |
| 文档漂移防护 | `guards/check_docs_drift.py` 六项断言（README 声称 vs 仓库实际），CI 已接线 | 已交付（v2.1） |
| 行为规则库 | `docs/RULES.md` 六条仓规，每条注明层级与立规出处 | 已交付（v2.1） |
| 内容产线（号侧） | 由一期仓 rsi-ima-workbuddy-wechatpub 承接 | 姊妹仓 |
| 体检结果回流 RSI 台账 | `scripts/ledger.py` 由 site-ops 每日自动追加 `_rsi_ledger.md` | 已交付（v2.2） |

## 六项体检明细（site_check.py）

| # | 检查项 | 目标 | 判定 |
|---|---|---|---|
| 1 | chai-home | `https://chai.aibay.asia/` | 200 且含 `<title>` |
| 2 | chailive-home | `https://www.aibay.asia/chailive/` | 200 |
| 3 | chailive-books | `https://www.aibay.asia/chailive/books.html` | 200 且含 `riaComplete` |
| 4 | chaibuddy-home | `https://www.aibay.asia/chaibuddy/` | 200 |
| 5 | chaibuddy-people | `https://www.aibay.asia/chaibuddy/data/people.json` | 200 |
| 6 | ai-proxy-ping | `https://dopenclaw.aibay.asia/cl2-ai/ping` | 200 且 `ok:true` |

全部只读（GET + 15s 超时），不碰任何生产数据；换自己站点只需改脚本顶部 `CHECKS` 列表。

## 快速开始

```bash
# 0. 前置：python3（必需），git（可选），ima-mcp 连接器（可选）
# 1. 安装技能（详见 SETUP.md）
# 2. 二期课堂主线：fork 讲师站（15 分钟，六大模块/巡检全带走）
python3 scripts/fork_chaiai.py --user 你的用户名
#    或从零建最小站（5 分钟零依赖上线）
python3 scripts/setup_wizard.py
# 3. 写第一篇
python3 scripts/new_post.py "我的第一篇拆书笔记"
# 4. 站点体检（默认指向 chai 站资产，可改 CHECKS 换成你的站）
python3 scripts/site_check.py
python3 scripts/site_check.py --json   # 机器格式，供 CI 用
python3 scripts/site_check.py --retry  # 失败项隔 10s 复测一次再定性（防抖动误报）
```

WorkBuddy 用户直接说「**fork 讲师站**」「**把站换成我的**」「**帮我建个人网站**」「**给站点做个体检**」即可，技能路由见 SKILL.md。

## 仓库结构

```
rsi-ima-workbuddy-wechat-web/
├── SKILL.md                  # WorkBuddy 技能定义 v2.2.0（触发词/别名/前置/流程）
├── SETUP.md                  # 安装向导
├── README.md                 # 本文件
├── evidence.txt              # site_check 实跑证据（逐块标注结论，RULES R2 活样本）
├── docs/
│   ├── GOALS.md              # 工作坊目标与验收：G1 装好技能 → G2 建出站点
│   │                         #   → G3 跑通首篇发布 → G4 闭环体检全绿
│   ├── CLOSED-LOOP.md        # 自动化闭环设计（库→站→号总图，对照一期九步）
│   ├── UPGRADE-v2.md         # v1 → v2 升级说明（含改名公告与 remote 切换命令）
│   ├── RULES.md              # 六条仓规 R1–R6（写后回读/证据真实/先复测/只读红线/防漂移/复盘纪律）
│   ├── BORROWED-FROM-LOONG-WORKFLOW.md  # 机制学习笔记：从 loong-workflow 借了什么、落到哪
│   └── retrospectives/
│       └── TEMPLATE.md       # 复盘模板（五段式+行动项四条硬约束）
├── guards/
│   └── check_docs_drift.py   # 文档漂移防护：README 声称 vs 仓库实际 六项断言（R5）
├── scripts/
│   ├── setup_wizard.py       # 建站向导（v1）
│   ├── new_post.py           # 发文脚本（v1）
│   ├── diagnose.py           # 诊断脚本（v1）
│   └── site_check.py         # 站点体检（v2；v2.1 加 --retry 复测定性）
├── templates/
│   └── site-minimal/         # 单文件建站模板（v1）：config.js / index.html / posts.js / style.css
└── .github/workflows/
    └── site-ops.yml          # 每日定时体检 Actions（v2；v2.1 加二轮复测+漂移防护步）
```

## v1 → v2 变化一览

> v2.1 增量（2026-11-04，借鉴 loong-workflow 机制，完整学习笔记见
> [docs/BORROWED-FROM-LOONG-WORKFLOW.md](docs/BORROWED-FROM-LOONG-WORKFLOW.md)）：
> site_check 加 `--retry` 复测定性；site-ops 加二轮复测（两轮全挂才告警）；
> 新增 `guards/check_docs_drift.py` 漂移防护、`docs/RULES.md` 六条仓规、
> `docs/retrospectives/TEMPLATE.md` 复盘模板；evidence.txt 重构为逐块标注结论。

| 维度 | v1（github-pages-workbuddy） | v2（本仓现名） |
|---|---|---|
| 定位 | 小白 GitHub Pages 建站技能 | 一库一站一号飞轮的「站」侧主仓 |
| 新增 | — | site_check 六项体检、site-ops 每日 Actions、GOALS/CLOSED-LOOP/UPGRADE 三文档 |
| 保留 | 建站/发文/诊断全套 | 全部保留，接口不变 |

改名后旧地址自动重定向；本地已有 clone 的用
`git remote set-url origin https://github.com/kenyanghui/rsi-ima-workbuddy-wechat-web.git` 切换（详见 docs/UPGRADE-v2.md）。

## 与 chai 站资产的关系

本仓的体检目标是一组真实运营的站点资产：[chai.aibay.asia](https://chai.aibay.asia/)（课程阵地）、[chailive](https://www.aibay.asia/chailive/)（RIA 全库站）、[chaibuddy](https://www.aibay.asia/chaibuddy/)（拆搭子名录浏览器）。它们即「拆AI工作坊」的教学现场——学员看到的每个线上页面，背后都有本仓工作流的影子。

## 相关仓库

| 仓 | 关系 |
|---|---|
| rsi-ima-workbuddy-wechatpub | 一期姊妹仓：管「号」（公众号内容工厂九步流水线） |
| [chaiAI](https://github.com/kenyanghui/chaiAI) | chai.aibay.asia 源码仓（体检目标 1/2/5 的本体） |
| [chaiflow](https://github.com/kenyanghui/chaiflow) | 全部决策记录 / 复盘 / 手册的开源档案 |

## 许可证

MIT
