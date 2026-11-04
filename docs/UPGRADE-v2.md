# v1 → v2 升级说明

## 改名公告

本仓已从 **github-pages-workbuddy** 更名为 **rsi-ima-workbuddy-wechat-web**。

- 旧地址自动重定向：原 `github.com/kenyanghui/github-pages-workbuddy` 的所有链接（clone/网页/API）自动跳转新名，无需改 bookmark。
- 本地已有 clone 的用户：`git remote set-url origin https://github.com/kenyanghui/rsi-ima-workbuddy-wechat-web.git` 一条命令切换（不改也能推，GitHub 会自动跟随重定向，但建议改）。

## 为什么改名

v1 名字只说了「GitHub Pages 建站」，装不下第二期的定位：IMA 知识库 → 网站 + 公众号 + chai 站自动化工作流。新名字把「站（web）+ 号（wechat）」都写进去，与一期仓 rsi-ima-workbuddy-wechatpub（管号）成对。

## 新增组件清单（v2.0.0）

| 组件 | 路径 | 作用 |
|---|---|---|
| 站点体检脚本 | `scripts/site_check.py` | 6 项只读检查，人类表格 + `--json` 双输出，全过 exit 0 |
| 定时体检 workflow | `.github/workflows/site-ops.yml` | 每日 09:17（北京）自动体检，失败输出中文告警块 |
| 工作坊目标 | `docs/GOALS.md` | 「一库一站一号」目标拆解 + 里程碑验收口径 |
| 闭环设计 | `docs/CLOSED-LOOP.md` | 自动化闭环图解 + 与一期九步对照表 + 安全红线 |
| 本升级说明 | `docs/UPGRADE-v2.md` | 本文件 |

## v1 用户如何平滑升级

- **git pull 即可**：v1 的全部技能（site-minimal 模板、new_post.py、setup_wizard.py、diagnose.py）原样保留，一个字节没动。
- 新增的 site_check/site-ops 不影响旧流程；不想要定时体检，不启用 Actions 即可（默认就能跑，零配置）。
- SKILL.md 已升级 v2 描述，老技能调用习惯不变。

## 版本

- v1.0.0：github-pages-workbuddy（建站技能）
- **v2.0.0**：rsi-ima-workbuddy-wechat-web（+站点体检、定时 Actions、工作坊文档；改名）
