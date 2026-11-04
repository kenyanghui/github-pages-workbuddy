# SETUP.md — 安装指南（3 分钟装好，不需要懂代码）

> 前提：已安装 WorkBuddy。本指南面向零基础学员。
> 现场 usage：第二期拆AI工作坊「一库一站一号」环节，跟着做即可。

## 第 0 步：把技能装进 WorkBuddy

**方式一 · 终端（推荐，一行）**：

```bash
git clone https://github.com/kenyanghui/rsi-ima-workbuddy-wechat-web ~/.workbuddy/skills/rsi-ima-workbuddy-wechat-web
```

**方式二 · 不用终端**：

1. 浏览器打开 https://github.com/kenyanghui/rsi-ima-workbuddy-wechat-web
2. 绿色 `Code` 按钮 → `Download ZIP` → 解压
3. 把解压出的 `rsi-ima-workbuddy-wechat-web-main` 改名为 `rsi-ima-workbuddy-wechat-web`
4. 整个文件夹放进 `~/.workbuddy/skills/`（Mac Finder 按 `Cmd+Shift+G` 输入 `~/.workbuddy/skills/` 回车；Windows 在用户目录下建同名路径）

装完重启 WorkBuddy（或新开一个对话），说「**网站体检**」——看到技能名出现在检查结果里就是装好了。

## 第 1 步：拿两个账号（已有就跳过）

| 账号 | 哪里注册 | 干什么用 |
|------|---------|---------|
| GitHub | github.com（邮箱注册即可） | 免费托管网站 |
| 微信公众号 | mp.weixin.qq.com | 第二个出口 |

第一期已配过 IMA / 公众号 API 凭证（`~/.config/ima/`、`~/.config/wechat/`）的同学：全部直接复用，无需重配。

## 第 2 步：生成你的网站（二选一）

**路径 A · fork 讲师站（课堂主线，推荐）**：把讲师站 chai.aibay.asia 的源码仓 fork 成你的——六大模块、工作坊详情、材料回看、每日巡检全部带走，再换名字换内容：

1. 浏览器开 https://github.com/kenyanghui/chaiAI/fork → Create fork（全默认）
2. clone 你的 fork，对 WorkBuddy 说「**把站换成我的**」（站名/署名/导航/people）
3. push 后等 Actions 1–5 分钟，开 `https://用户名.github.io/chaiAI/`

完整五步表与换装红线见 `references/fork-chaiai.md`。

**路径 B · 从零最小站**：

对 WorkBuddy 说：

> **帮我建个人网站**

（或终端 `python3 ~/.workbuddy/skills/rsi-ima-workbuddy-wechat-web/scripts/setup_wizard.py`）

向导问 6 个问题，然后生成 `~/my-site/`。**双击 `index.html` 就能看到你的站**。

## 第 3 步：发布上线

最顺的路径（零终端，约 10 分钟）：

1. github.com 右上角 `+` → `New repository` → 仓库名填向导里那个（如 `my-site`）→ Public → Create
2. 仓库页 `Add file → Upload files` → 把 `~/my-site/` 里**除 `_local` 外**的所有文件拖进去（文件夹会整体上传）→ Commit
3. 仓库 `Settings → Pages` → Source 选 `Deploy from a branch`，Branch 选 `main` / `/ (root)` → Save
4. 等 1-5 分钟，刷新 Pages 页，你的网址就在上面（形如 `https://用户名.github.io/my-site/`）

终端通道、自定义域名（如 chai.aibay.asia 那样用自己的域名）见 `references/publish.md`。

## 第 4 步：写出第一篇文章

把你在 ima 里攒的素材（一段文字/读书笔记都行）交给 WorkBuddy：

> 用这段素材帮我在网站上发一篇文章：<粘贴素材>

技能会生成：网站文章页（自动更新首页列表）+ `_local/` 里的公众号粘贴版（浏览器打开 → 全选复制 → 粘进公众号编辑器）。

## 常见安装问题

| 症状 | 解法 |
|------|------|
| clone 报权限/不存在 | 仓库名拼错了，直接浏览器能打开就说明仓库在 |
| ~/.workbuddy/skills/ 不存在 | 自己建：`mkdir -p ~/.workbuddy/skills` |
| 说了「网站体检」没反应 | 技能文件夹名字必须叫 `rsi-ima-workbuddy-wechat-web`；重启 WorkBuddy |
| wizard 跑不起来 | 需要 Python 3.8+；终端跑 `python3 --version` 确认 |
