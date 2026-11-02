# 发布上线（双通道）+ 自定义域名 + 验证清单

> 对 WorkBuddy 说「发布网站」「更新网站」「绑定自己的域名」时读本文。

## 你要先知道的三件事

1. **两条通道殊途同归**：网页上传（零终端）和 git 推送最终都是「文件进仓库 → Pages 出网站」。选顺手的，以后可换。
2. **第一次发布要等 1-5 分钟**（GitHub 在构建）。之后每次更新约 1 分钟内生效。
3. **`_local/` 永不上传**（公众号粘贴版+台账，私人产物）。git 通道已被 `.gitignore` 挡住；网页上传时手动别拖它。

## 路径 A · 网页上传（零终端，第一次发布约 10 分钟）

1. github.com 右上角 `+` → `New repository`
   - Repository name: 填向导里的仓库名（如 `my-site`）
   - 选 **Public**（免费版 Pages 只服务公开仓）
   - **不要**勾选 Add README（避免和本地文件冲突）
   - `Create repository`
2. 仓库页 `Add file → Upload files`
3. 打开你的站点目录（如 `~/my-site`），把**除 `_local` 外**的所有东西拖进上传区
   - `index.html` `config.js` `posts.js` `style.css` `posts/` `.gitignore` 都要
4. 页面底部 `Commit changes`
5. 仓库 `Settings → Pages`：
   - Source: `Deploy from a branch`
   - Branch: `main` + `/ (root)` → `Save`
6. 等 1-5 分钟，刷新 Pages 设置页——顶部会出现你的网址（`https://用户名.github.io/my-site/`）

### 更新网站（路径 A）

- **改了文章/新增文章**：重新上传变动的文件（`posts/新文章.html`、`posts.js`、如动了配置再加 `config.js`），Commit
- **拖文件夹没反应**：上传区只接受拖拽文件树，个别浏览器怪异——换 Chrome，或改用路径 B

## 路径 B · git 终端通道（第一次配置约 10 分钟，之后每次更新 30 秒）

### 第一次：把本地站点接上仓库

```bash
cd ~/my-site
git init
git add .
git commit -m "我的个人网站第一版"
git branch -M main
git remote add origin https://github.com/<用户名>/<仓库名>.git
git push -u origin main
```

（仓库本身还是要按路径 A 第 1 步先建好；Pages 开关按路径 A 第 5 步打开——就这两步离不开网页）

### 之后每次更新

```bash
cd ~/my-site
git add .
git commit -m "更新：<写了什么>"
git push
```

约 1 分钟后线上生效。**卡住就这样**：`git pull --rebase origin main` 再 push；还乱就 `git status` 把输出发给 WorkBuddy。

## 绑自己的域名（可选，进阶）

蓝本 chai.aibay.asia 用的就是这条路。你需要：一个买来的域名（约 ¥50-80/年）。

1. 域名 DNS 控制台加一条 CNAME：`www` → `<用户名>.github.io`
2. 仓库 `Settings → Pages → Custom domain` 填 `www.你的域名.com` → Save
3. 勾选 **Enforce HTTPS**（等 DNS 生效后证书自动签发，几分钟到几小时）
4. 站点目录加一个 `CNAME` 文件（内容就一行你的域名），随下次发布上传——**不加的话下次推送会把域名配置冲掉**（蓝本踩过的真坑）

⚠️ 域名备案问题只影响「域名解析到国内服务器」的情形；github.io 在境外，一般无需备案，但域名实名认证仍要做。

## 验证清单（每次发布后过一遍）

- [ ] 打开线上网址，首页能开、站名对
- [ ] 点一篇最新文章，正文完整
- [ ] 手机打开一次（或浏览器开发者工具切手机视图）
- [ ] 浏览器地址栏是 https（Pages 自动配）
- [ ] `site:<线上网址>` 谷歌/必应搜一下（几天后可被收录）

**打不开/不对时**：

| 症状 | 九成是 | 解法 |
|------|--------|------|
| 404 | Pages 没开 / 仓库名大小写不符 / 刚提交没到 5 分钟 | 核对 Settings→Pages；等；强刷 |
| 还是旧内容 | 浏览器缓存 / CDN 延迟 | Cmd/Ctrl+Shift+R；等 2 分钟再看 |
| 样式全丢 | `style.css` 没传上 / 目录层级错了 | 对照线上文件列表补传 |
| 文章 404 | `posts/` 文件夹没整体上传 | 重新拖 `posts/` 整个文件夹 |
| 自定义域证书一直 pending | DNS 未生效 / CNAME 指错 | `ping <用户名>.github.io` 核对；等几小时 |
