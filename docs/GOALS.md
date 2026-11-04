# 工作坊目标（第二期）——「一库一站一号」飞轮

> 一期跑通了「一库 → 一号」。二期把「一站」插进飞轮：IMA 知识库（库）→ 个人网站（站）→ 公众号（号），三者同源、互相导流、同一套 RSI 自进化范式驱动。

## 目标拆解（可量化）

| # | 目标 | 量化口径 |
|---|---|---|
| G1 | 学员装好 WorkBuddy 技能 | `SETUP.md` 走完，`diagnose.py` 全绿 |
| G2 | 学员建出自己的站点 | `setup_wizard.py` 产站，本地 `vite preview` 或浏览器双击可开，GitHub Pages 可访问 |
| G3 | 跑通首篇发布 | `new_post.py` 发文 → push main → Actions 自动构建 → 线上 URL 可见新内容 |
| G4 | 闭环体检全绿 | `site_check.py` 六项检查全 pass（exit 0），`--json` 输出 overall=pass |
| G5 | （进阶）定时巡检上线 | fork 本仓后 site-ops Actions 在自己账号跑起来，收到首次定时体检报告 |

## 里程碑

| 里程碑 | 内容 | 验收口径 |
|---|---|---|
| M1 装技能 | 安装 WorkBuddy 技能 + 连上 IMA | G1：diagnose 全绿 |
| M2 建站 | 用 site-minimal 模板建出个人站 | G2：Pages URL 返回 200 且含自己标题 |
| M3 内容产线 | 首篇拆书笔记从 IMA 到站点上线 | G3：线上可见新 post，commit 有据 |
| M4 闭环体检 | 站点体检 + 定时 Actions + 结果回流 | G4/G5：site_check exit 0；Actions 历史有绿勾 |

## 验收口径细则（每项怎么算过）

- **G1**：`python3 scripts/diagnose.py` 输出无 FAIL 项；技能目录被 WorkBuddy 识别（`/skills` 列表可见）。
- **G2**：`https://<用户名>.github.io/<仓名>/` 返回 200；页面 `<title>` 非模板默认值（即学员已改）。
- **G3**：新 post 文件在仓；`git log` 有对应 commit；线上页面能检索到 post 标题关键词。
- **G4**：连续两天 `site_check.py` exit 0；`--json` 的 checks 数组 6 项 ok=true。
- **G5**：GitHub Actions 页面可见 site-ops workflow 的 schedule 触发记录（非手动 dispatch）。

## 与一期目标的衔接

一期验收的是「号」：技能装好、素材库建好、首篇文章进草稿箱。二期在此基础上加「站」：同一套 RSI 台账（素材避重 / 风格偏好 / 人工修正分级）同时服务号与站两个出口。学员只需维护一个知识库，两个出口自动受益。
