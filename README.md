# github-pages-workbuddy

**小白友好的 GitHub Pages 个人网站流水线**——跑在 WorkBuddy 上的技能（Skill）。

以 [chai.aibay.asia](https://chai.aibay.asia) 的真实搭建史为蓝本，把「第二期拆AI工作坊：一库一站一号内容飞轮」的目标变成学员现场可安装、可带走的工具：

- **5 分钟建站**：向导生成零依赖个人网站，双击即开、手机能看、GitHub Pages 免费上线
- **素材变双出口**：IMA 知识库素材 → 同一篇文章，网站发布 + 公众号可粘贴排版
- **30 天飞轮台账**：库 → 网站 + 公众号，越写越顺的闭环（承接第一期 ima 知识库工作流）
- **可持续长大**：静态起步，沿蓝本升级到 React + Actions + 自定义域名

## 安装（3 分钟）

```bash
git clone https://github.com/kenyanghui/github-pages-workbuddy ~/.workbuddy/skills/github-pages-workbuddy
```

不会用终端？看 [SETUP.md](SETUP.md) 的图文版（ZIP 下载 + 拖拽安装）。

## 三步跑通

```bash
# 1. 生成网站（回答 6 个问题，先看效果可加 --demo）
python3 scripts/setup_wizard.py

# 2. 写文章（素材文件变网站文章 + 公众号粘贴版）
python3 scripts/new_post.py --site ~/my-site --title "我的第一篇" --file 素材.md

# 3. 体检
python3 scripts/diagnose.py --site ~/my-site
```

在 WorkBuddy 里直接说人话更简单：「帮我建个人网站」「用这段素材发篇文章」「网站体检」。

## 文档地图

| 文件 | 内容 |
|------|------|
| [SKILL.md](SKILL.md) | 技能入口与五阶段路线（WorkBuddy 读这个） |
| [SETUP.md](SETUP.md) | 零基础安装图文指南 |
| references/publish.md | 发布上线双通道 + 自定义域名 + 验证清单 |
| references/flywheel.md | 一库一站一号飞轮：IMA 素材进出 + 公众号双出口 + 30 天台账 |
| references/blueprint-chai.md | 蓝本 chai.aibay.asia 演进史（想升级必读，含全部踩坑） |

## 和兄弟技能的关系

- [rsi-wechat-publisher](https://github.com/kenyanghui/wechat-pub-workbuddy)（第一期：公众号流水线）：装了它，本技能的文章出口自动升级为「API 推公众号草稿箱」；IMA/公众号凭证完全复用。
- 本技能专注「站」这一环：库（ima）→ **站（GitHub Pages）** → 号（公众号）。

## 适用与限制

- 适合：个人网站、作品集、知识库落地页、周更/日更文章站
- 免费、公开托管：不要放隐私信息；站点内容人人可见
- 想要会员/支付/数据库？蓝本里给了升级路线图，但那已是下一阶段的事

## License

MIT
