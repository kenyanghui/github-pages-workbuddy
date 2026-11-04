# fork-chaiai.md — fork 讲师站工作流（第二期主线 v3）

> **一句话**：不从零建站——把讲师站 chaiAI（chai.aibay.asia 源码）fork 成你的，换名字换内容，六大模块信息流和 ima/公众号联动全部保留。

## 为什么 fork 而不是从零建

- 从零建站只得到「空名片」；fork 得到**整条产线**：六大模块首页、工作坊详情页、材料回看、留言板、每日巡检 Actions。
- fork 是 GitHub 原生动作，一步到位；之后你的修改与讲师站互不影响。
- rsi 技能已内置本仓的发布/体检/双出口流程，fork 后全部直接可用。

## 五步（15 分钟，课堂节奏）

| 时间 | 动作 | 凭证 |
|---|---|---|
| 0–2′ | 浏览器开 `github.com/kenyanghui/chaiAI/fork` → Create fork（全默认） | 你的 fork 地址 ☐ |
| 2–5′ | clone 你的 fork：`git clone https://github.com/<你>/chaiAI.git` | 本地目录：____ |
| 5–10′ | 换装（见下节）：站名/署名/导航/people | 新站名：____ |
| 10–13′ | `git add -A && git commit -m "换装" && git push` | 已推送 ☐ |
| 13–15′ | 等 Actions（1–5 分钟）→ 开 `https://<你>.github.io/chaiAI/` | 网址：____ |

## 品牌换装：只动数据，不动骨架

**红线：组件逻辑（src/components、src/pages 的 JSX 结构）第一周不动**——先让站活着，再谈改功能。

| 文件 | 改什么 |
|---|---|
| `src/data/workshops.js` | 你的工作坊/活动主题、时间、链接 |
| `public/people.json` | 你的名录（自己先写一条） |
| `index.html` | `<title>` 站名 |
| `src/pages/About.jsx` | 你的身份三段（我是谁/做什么/怎么找到我） |

对 WorkBuddy 说「**把站换成我的**」，技能按上表逐项问你要值再改——不整页重写，diff 最小。

## 控制信息流（rsi 技能的日常用法）

- **发内容**：说「用这段素材发篇文章」→ `scripts/new_post.py` 生成文章页+首页列表自动更新；`_local/` 同步出公众号粘贴版。
- **改首页六大模块**：数字与文案在 `src/pages/Home.jsx` 顶部 `modules` 数组——说「把拆学习换成拆职场」即可，整表替换（playbook 纪律：有序数组禁止局部插入）。
- **上下线页面**：`src/components/Navbar.jsx` + `src/App.jsx` 路由表整表替换，每条 path 唯一性断言。
- **验收**：说「网站体检」→ `scripts/site_check.py` 六项只读检查。

## 联动 ima / 公众号（与 fork 前完全一致）

fork 不破坏联动——凭据在你本机（`~/.config/ima/`、`~/.config/wechat/`），与仓库无关：

1. ima 取素材 → WorkBuddy「用这段素材发篇文章」→ 网站文章页 + `_local/` 公众号粘贴版。
2. 进阶（API 直推草稿箱）：见 `references/flywheel.md` § 升级出口。
3. 每日巡检 Actions（site-ops.yml）随 fork 带走，记得在 fork 仓 Settings → Actions 开启。

## 与讲师站同步上游（可选）

```bash
git remote add upstream https://github.com/kenyanghui/chaiAI.git
git fetch upstream && git rebase upstream/main   # 只在你没大改时用
```

改过骨架的（第二周以后）：别 rebase，挑文件 cherry-pick。

## 常见坑

| 症状 | 解法 |
|---|---|
| fork 后 Pages 404 | fork 默认启用 Pages，但需等 Actions 首跑；Settings → Pages 确认 Branch=main |
| Actions 没跑 | fork 仓 Actions 默认关闭，页面上点 Enable workflows |
| 推送被拒 401 | 本地 clone 的 remote 是你的 fork，不是讲师仓；token 用你自己的 |
| 网站开了但样式乱 | vite 的 `base` 路径仓内已配好 `'/chaiAI/'`；若你把 fork 改名，需同步改 `vite.config` 的 base 与路由 basename |
