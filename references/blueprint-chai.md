# 蓝本拆解：chai.aibay.asia 是怎么搭起来、怎么长大的

> 对 WorkBuddy 说「升级网站」「加功能」「我想像 chai.aibay.asia 那样…」时读本文。
> 本文是这个技能的出身：第二期工作坊现场「照着拆」的那个站，从 0 到今天的完整路径与全部踩坑。

## 蓝本现址与身世

- 线上：https://chai.aibay.asia （GitHub 仓 kenyanghui/chaishu，本地 /root/gh-chaishu）
- 技术栈演进：**纯静态 HTML → Vite+React SPA → GitHub Actions 自动部署 → 自定义域名 → 互动表单/工作手册 → 全库子站联动**
- 你现在的起点（site-minimal 模板）≈ 蓝本的第 0 阶段。每一阶段都是下一阶段的垫脚石，**不要跳级**。

## 阶段 0 → 1：从单页到多页（你已在此）

蓝本做法：`index.html` + 每篇文章一个独立 `.html` + 一份清单文件让首页列文章。
这就是 site-minimal 的形态：零依赖、双击即开、file:// 也能用。**够发 50 篇文章再考虑升级。**

## 阶段 1 → 2：组件化（Vite + React）

触发条件：页面超过 ~10 个、导航/页脚开始到处复制粘贴、想要标签筛选或搜索。
做法（小白版）：对 WorkBuddy 说「帮我把网站升级成 React」——让 AI 建骨架（Vite + React + react-router），页面内容照搬。蓝本的 Navbar/Footer/卡片组件都是这么长出来的。
坑：

- 升级后本地要 `npm run dev` 预览、`npm run build` 出 dist/ 目录——**上传的是 dist/ 内容，不是源码**
- SPA 直链（如 /hot）curl 到 404 是正常现象（客户端路由），浏览器访问没问题——别当故障修

## 阶段 2 → 3：自动化（GitHub Actions）

触发条件：每次改完要手动 build+上传，烦了。
做法：仓库里加 `.github/workflows/deploy.yml`，从此 `git push` 源码 → Actions 自动 build+部署。蓝本的 workflow（可直接抄）：

```yaml
name: Deploy to GitHub Pages
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 20
      - run: npm ci
      - run: npm run build
      - uses: actions/configure-pages@v4
      - uses: actions/upload-pages-artifact@v3
        with:
          path: dist
      - id: deployment
        uses: actions/deploy-pages@v4
```

坑：**改完 push 后等 1-2 分钟再验证线上**（部署间隙会拿到旧包，蓝本反复踩过——验证前先比对线上引用的资源 hash 是否等于本地产物）。

## 阶段 3 → 4：自己的域名

见 publish.md「绑自己的域名」。蓝本三要素：DNS CNAME + Pages 设置 + **仓库里的 CNAME 文件**（缺了它，下次 push 域名配置被冲掉）。

## 阶段 4 → 5：互动与生态（选学）

蓝本后来加的东西，全部有更简单的起步版：

| 蓝本终态 | 起步版 | 说明 |
|---------|--------|------|
| 报名表单（SMTP 邮件直达站长） | 用金数据/问卷星外链 | 表单服务免费版够用，先外链后自建 |
| 线上可填写工作手册（localStorage） | 静态页先上 | 「表格需求=填写物非陈列物」——要能存能导出再上 localStorage |
| 全库子站（chailive，2255 本书） | 每周一篇书摘文章 | 数据量是长出来的，不是第一天建的 |
| 多站导航矩阵 | 一个 nav 就够 | 站多了再谈矩阵 |

## 蓝本踩坑总账（升级前扫一眼，能省一晚上）

1. **.gitignore 误伤产物**：蓝本曾因一条 `dist` 规则把所有 PDF 挡在仓外，线上 404 半个月才发现——加例外 `!public/**/dist`
2. **大小写敏感**：Windows/Mac 本地不区分、GitHub 区分——文件名全小写最稳
3. **GitHub Pages 无目录列表**：`/dir/` 裸目录链接 404，要指到具体文件
4. **缓存错觉**：改了没变先强刷（Cmd/Ctrl+Shift+R）再怀疑代码
5. **仓库名=网址的一部分**：`用户名.github.io/仓库名/`，建仓时想好；改名的代价是所有旧链接 404（蓝本的 chailive 改名就是全站补跳转页收的尾）
6. **凭证永不进仓**：API key 一旦 push 到公开仓，视同泄露，立刻去平台吊销重发

## 给工作坊学员的一句话

蓝本的每一阶段都值得停下来住一阵子。**先把阶段 0 的 30 分钟走完，让世界看到你的站**——升级的事，交给 30 天飞轮里的某一周。
