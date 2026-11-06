---
name: rsi-ima-workbuddy-wechat-web
aliases:
  - 个人网站流水线
  - GitHub建站
  - 一库一站一号
  - 内容飞轮
description: 第二期工作坊主仓技能：IMA 知识库 → 网站(GitHub Pages) + 公众号 + chai 站自动化工作流（「一库一站一号」飞轮）。v2 新增站点体检 site_check（6 项只读检查）与每日定时 Actions 巡检；v1 建站流水线全保留：5 分钟零依赖网站上线、素材双出口、30 天飞轮台账。Use when user mentions "建网站", "个人网站", "GitHub Pages", "上线", "一库一站一号", "网站更新", "发文章到网站", "公众号联动", "内容飞轮", "站点体检", "site_check", "定时巡检", "拉网站反馈", "网站反馈", "读者来信", "兴趣雷达", "抓热点", "热点选题", "自动迭代".
version: 3.0.0
platforms: [darwin, linux, win32]
prerequisites:
  commands: [python3]
  optional_commands: [git]
  optional_connectors: [ima-mcp]
---

# 个人网站流水线（rsi-ima-workbuddy-wechat-web）

> **一句话**：把你的 IMA 知识库变成一个打开就能看的家——免费 GitHub Pages 网站 + 公众号双出口，同一篇素材两处发。蓝本：chai.aibay.asia（第二期拆AI工作坊现场照着拆的那个站）。

## 语言

跟随用户语言（默认中文）。

## ⚡ 首次使用：5 分钟

**第一步：初始化网站（二选一）**

- **路径 A · fork 讲师站（第二期课堂主线）**：对 WorkBuddy 说「**fork 讲师站**」或 `python3 scripts/fork_chaiai.py --user 你的用户名`——把 chai.aibay.asia 源码仓 fork 成你的，六大模块/材料回看/巡检全带走，五步 15 分钟。详见 `references/fork-chaiai.md`。
- **路径 B · 从零最小站**：对 WorkBuddy 说「**帮我建个人网站**」，或终端跑：

```bash
python3 scripts/setup_wizard.py
```

向导问 6 个问题（站名/一句话简介/笔名/公众号名/GitHub 用户名/仓库名），生成 `~/my-site/` 零依赖站点：`index.html` 双击即开，手机也能看。

**第二步：发布上线（二选一）**

- **路径 A · 网页上传（零终端）**：github.com 新建公开仓 → 拖拽上传 `my-site` 里的文件 → Settings → Pages → Deploy from branch。详见 `references/publish.md`。
- **路径 B · 终端**：`git init && git push`，命令清单同样在 `references/publish.md`。

**第三步：跑诊断**

对 WorkBuddy 说「**网站体检**」，或 `python3 scripts/diagnose.py --site ~/my-site`。

## Workflow Router（本文件是入口，只做路由）

| 任务意图 | 路由到 |
|---------|--------|
| fork 讲师站 / 换装 / 改六大模块 | `scripts/fork_chaiai.py` + `references/fork-chaiai.md`（**fork 主线必读**：五步表、品牌换装红线、信息流控制、ima/号联动不受影响） |
| 建站 / 重新初始化 | `scripts/setup_wizard.py`（`--demo` 可先生成演示站） |
| 写新文章 / 素材变文章 | `scripts/new_post.py`（读 `references/write.md` 再执行） |
| 发布 / 更新网站 / 自定义域名 | `references/publish.md`（双通道+DNS+验证清单） |
| IMA 素材进出 / 公众号双出口 / 30 天飞轮 | `references/flywheel.md`（**执行联动任务前必读**） |
| 想升级站（React/Actions/表单） | `references/blueprint-chai.md`（蓝本演进史，含全部踩坑） |
| 体检 / 哪里坏了 | `python3 scripts/diagnose.py`（本地站）；`python3 scripts/site_check.py`（chai 站线上体检，只读；`--retry` 失败项复测一次再定性） |
| 定时巡检 / Actions | `.github/workflows/site-ops.yml`（每日 09:17 北京自动体检+二轮复测+文档漂移防护，详见 `docs/CLOSED-LOOP.md`） |
| 改文档 / 改体检项 / 改流程前 | `docs/RULES.md`（六条仓规：写后回读/证据真实/先复测/只读红线/防漂移/复盘纪律）；改完跑 `python3 guards/check_docs_drift.py` |
| 事故复盘 / 教训沉淀 | `docs/retrospectives/TEMPLATE.md`（五段式+行动项四条硬约束；借鉴出处 `docs/BORROWED-FROM-LOONG-WORKFLOW.md`） |
| 工作坊目标与验收 | `docs/GOALS.md`；闭环设计 `docs/CLOSED-LOOP.md`；v1→v2 升级 `docs/UPGRADE-v2.md` |
| 兄弟技能联动（公众号 API 推草稿箱） | flywheel.md § 升级出口 |

**路由纪律**：改流程改 references/scripts，不动本文件；站点个人信息只放站点 `config.js`。

## 五阶段路线（对齐第二期工作坊「一库一站一号」）

```
Stage0 体检(diagnose) → Stage1 建(wizard→30分钟上线)
  → Stage2 写(new_post: IMA素材→网站文章+公众号粘贴版)
  → Stage3 联(飞轮: 库→站+号双出口, 文章回存库, 30天台账)
  → Stage4 长大(蓝本: 自定义域→React+Actions→互动表单)
```

- Stage2 产物：`posts/<日期>-<slug>.html`（文章页）+ `_local/wechat-<slug>.html`（公众号粘贴版，**不要上传**）+ `posts.js` 清单自动更新。
- **自进化（v3 灵魂）**：兴趣雷达 `scripts/interest_radar.py` 每日扫微博/知乎/抖音/头条四榜，用站内文章兴趣匹配全网热点，命中项入 ima「热点选题」；与反馈回流（feedback_pull.py → 「网站邮箱信息」）两流汇成同一池选题，飞轮从「人找题」变「闭环自己产题」——对 WorkBuddy 说「**扫热点选题**」。
- 与第一期的衔接：已配过 IMA 凭证（`~/.config/ima/`）或 ima-mcp 连接器的同学，素材环节直接查库；已装 rsi-wechat-publisher 技能的同学，出口升级为 API 推草稿箱。

## 安全红线（不可违反）

1. 凭证只放 `~/.config/`，绝不进站点目录、不提交 git、不进提示词。
2. `_local/` 目录（公众号粘贴版、飞轮台账）永远不上传——`.gitignore` 已排除，网页上传通道手动跳过它。
3. 站是公开的：身份证/手机号/住家地址/未公开收入等隐私不入文；素材转述遵守 Truth-first，不编造来源。
4. 先发布后优化：任何阶段网站打不开，回退上一版（git 或备份文件），不裸奔调试。

## 故障速查

| 症状 | 原因 | 解法 |
|------|------|------|
| xxx.github.io 404 | Pages 未开/等 1-5 分钟/大小写不符 | publish.md § 验证清单 |
| 更新了但内容没变 | 浏览器缓存/CDN 延迟 | 强刷 Cmd/Ctrl+Shift+R；等 2 分钟 |
| 文章页能开、首页列表没有 | posts.js 没更新或 JS 被拦 | 重跑 new_post；看浏览器控制台 |
| 公众号粘贴后样式乱 | 编辑器剥离样式 | 用 _local/wechat-*.html 整页复制，别复制源码 |
| 图片不显示 | 路径大小写/未上传 assets/ | 相对路径小写、检查远端文件在不在 |
