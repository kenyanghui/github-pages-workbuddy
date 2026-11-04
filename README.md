# rsi-ima-workbuddy-wechat-web

> **第二期工作坊主仓**：把你的 IMA 知识库变成「站 + 号」双阵地——GitHub Pages 网站、公众号内容、chai 站自动化工作流，一个 RSI 自进化闭环全管。

## 一句话定位

- **一期（rsi-ima-workbuddy-wechatpub）管「号」**：IMA 知识库 → 公众号内容工厂，九步流水线日更三篇进草稿箱，绝不自动群发。
- **二期（本仓）管「站」**：WorkBuddy 直接操作 chai 站（GitHub）——建站、发布、体检、定时巡检，同一个 RSI 范式从「号」扩展到「站」。

## 核心能力

| 能力 | 组件 | 状态 |
|---|---|---|
| 站点体检 | `scripts/site_check.py`（6 项检查：主站/chailive 首页与书目页/chaibuddy 名录与数据/AI 代理健康，支持 `--json`） | 已交付 |
| 定时巡检 | `.github/workflows/site-ops.yml`（每日 09:17 北京时间自动体检，失败输出中文告警块） | 已交付 |
| 建站技能（v1 全保留） | `templates/site-minimal` 单文件模板 + `scripts/new_post.py` 发文 + `scripts/setup_wizard.py` 向导 + `scripts/diagnose.py` 诊断 | 已交付 |
| 内容产线（号侧） | 由一期仓 rsi-ima-workbuddy-wechatpub 承接 | 已交付（姊妹仓） |
| 体检结果回流 RSI 台账 | `_rsi_ledger.md` 增量记录 | 规划中 |

## 快速开始

```bash
# 1. 安装技能（详见 SETUP.md）
# 2. 建出你的第一个站
python3 scripts/setup_wizard.py
# 3. 写第一篇
python3 scripts/new_post.py "我的第一篇拆书笔记"
# 4. 站点体检（本仓默认指向 chai 站资产，可自行改 CHECKS 列表）
python3 scripts/site_check.py
python3 scripts/site_check.py --json   # 机器格式，供 CI 用
```

## 仓库结构

```
rsi-ima-workbuddy-wechat-web/
├── SKILL.md                  # WorkBuddy 技能定义（v2）
├── SETUP.md                  # 安装向导
├── README.md                 # 本文件
├── docs/
│   ├── GOALS.md              # 工作坊目标与里程碑验收
│   ├── CLOSED-LOOP.md        # 自动化闭环设计（对照一期九步）
│   └── UPGRADE-v2.md         # v1 → v2 升级说明
├── scripts/
│   ├── setup_wizard.py       # 建站向导（v1）
│   ├── new_post.py           # 发文脚本（v1）
│   ├── diagnose.py           # 诊断脚本（v1）
│   └── site_check.py         # 站点体检（v2 新增）
├── templates/
│   └── site-minimal/         # 单文件建站模板（v1）
└── .github/workflows/
    └── site-ops.yml          # 每日定时体检 Actions（v2 新增）
```

## 与 chai 站的关系

本仓的体检目标是一组真实运营的站点资产：[chai.aibay.asia](https://chai.aibay.asia/)（课程阵地）、[chailive](https://www.aibay.asia/chailive/)（RIA 全库站）、[chaibuddy](https://www.aibay.asia/chaibuddy/)（拆搭子名录）。它们即「拆AI工作坊」的教学现场——学员看到的每个线上页面，背后都有本仓工作流的影子。

## 许可证

MIT
