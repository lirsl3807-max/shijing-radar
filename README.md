# 📖 诗经学文献雷达 Academic Radar

**自动追踪 CSSCI 期刊中的《诗经》研究动态**

🌐 **GitHub Pages：** `https://<你的用户名>.github.io/<仓库名>/`
🌐 **本地运行：** `http://localhost:8081`（运行 `python3 server.py` 后访问）

---

## ✨ 功能

- 🔍 **自动搜索** — 每周自动在知网搜索诗经学相关论文
- 📋 **CSSCI 全覆盖** — 涵盖文学、语言学、历史学、考古学等 95 种 CSSCI 期刊
- 📱 **手机可看** — 部署到 GitHub Pages，手机浏览器直接访问
- ⏰ **定时更新** — GitHub Actions 定时运行，无需手动操作

## 📂 项目结构

```
.
├── radar.py                    # 核心搜索脚本
├── server.py                   # 本地 Web 服务器
├── index.html                  # 网页展示
├── data/
│   └── academic_radar_data.json   # 搜索结果数据
├── .github/workflows/
│   └── radar.yml               # GitHub Actions 自动搜索 + 部署
├── 诗经学关键词列表.md            # 搜索关键词文档
├── CSSCI期刊列表_文学_语言学_历史学_2025-2026.md
└── README.md
```

## 🚀 部署到 GitHub Pages

### 首次部署（需在浏览器操作，约 5 分钟）

1. **在 GitHub 创建仓库**
   - 打开 [github.com/new](https://github.com/new)
   - 仓库名：`shijing-radar`（或任意你喜欢的名字）
   - 选择 **Public**（公开，免费的 Pages 托管）
   - 点击 "Create repository"

2. **上传代码**
   ```bash
   # 在命令行执行（在你的电脑上）
   cd C:\Users\llo\Desktop\我的项目\academic_radar
   
   git init
   git add .
   git commit -m "🎉 初始化诗经学文献雷达"
   git branch -M main
   git remote add origin https://github.com/<你的用户名>/shijing-radar.git
   git push -u origin main
   ```

3. **启用 GitHub Pages**
   - 在浏览器打开你的仓库页面
   - 进入 **Settings** → **Pages**
   - 在 "Source" 处选择 **GitHub Actions**
   - 完成！首次部署会自动触发

4. **等待部署完成**
   - 进入仓库的 **Actions** 选项卡
   - 看到绿色 ✅ 即部署成功
   - 地址为 `https://<你的用户名>.github.io/shijing-radar/`

### 后续自动更新

- ✅ **每周一早上**自动搜索知网并更新数据
- ✅ 你随时可以在 Actions 页面点击 **"Run workflow"** 手动触发搜索
- ✅ 更新后页面自动刷新，无需任何操作

## 💻 本地开发

### 启动 Web 服务
```bash
cd academic_radar
python3 server.py
# 访问 http://localhost:8081
```

### 手动运行搜索
```bash
# Windows
export PATH="C:\Users\llo\Desktop\go-portable\go\bin:$PATH"
python3 radar.py

# Linux/macOS（Go 在 PATH 中即可）
python3 radar.py
```

## 📊 当前成果

- **覆盖期刊：** 95 种 CSSCI 期刊（文学/语言学/历史学/考古学/社科综合）
- **搜索关键词：** 41 个核心 + 26 个补充关键词
- **2026 年上半年已收录：** 28 篇诗经学相关论文

## 🔧 技术栈

| 组件 | 说明 |
|------|------|
| **[cnki-search](https://github.com/ExquisiteCore/cnki-search)** | Go 编写的知网搜索 CLI |
| **Python** | 搜索编排脚本（radar.py） |
| **GitHub Actions** | 定时运行 + 自动部署 |
| **GitHub Pages** | 免费静态页面托管 |
| **HTML + JS** | 前端展示页面 |

## 📝 许可

本项目仅供学术研究使用。数据来源于中国知网（CNKI），版权归原作者及期刊所有。
