# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**诗经学文献雷达 (Academic Radar)** — 自动从知网 (CNKI) 追踪 CSSCI 期刊中的《诗经》研究动态。

- 覆盖 **95 种 CSSCI 期刊**（文学/语言学/历史学/考古学/社科综合/扩展版/集刊）
- 使用 **41 个核心 + 26 个补充关键词** 搜索
- 当前（2026 上半年）已收录 **28 篇** 相关论文，**全部有摘要**
- 部署在 GitHub Pages，手机可访问

## 技术栈

| 组件 | 说明 |
|------|------|
| **[cnki-search](https://github.com/ExquisiteCore/cnki-search)** | Go 编写的知网搜索 CLI，逆向 KNS8S HTTP API |
| **radar.py** (Python) | 搜索编排脚本——多关键词 + 多期刊策略 |
| **AnySearch (skill)** | 网络搜索引擎，用于通过论文标题搜索摘要（替代被知网屏蔽的 detail 接口） |
| **server.py** (Python) | 简易本地 HTTP 服务器（端口 8081） |
| **index.html** (HTML+JS) | 前端展示——搜索、筛选、摘要展开/折叠 |
| **GitHub Actions** | 定时运行（每周日 UTC 00:00 = 北京周一 08:00）+ 手动触发 |
| **GitHub Pages** | 静态页面托管（legacy 模式，需 .nojekyll） |

## 项目结构

```
academic_radar/
├── radar.py                    # 核心搜索脚本（唯一需要修改的 Python 文件）
├── server.py                   # 本地 Web 服务器 (端口 8081)
├── index.html                  # 前端展示页面
├── data/
│   └── academic_radar_data.json   # 搜索结果数据（含摘要）
├── .github/workflows/
│   └── radar.yml               # GitHub Actions 工作流
├── .nojekyll                   # 必须存在，禁用 Jekyll Pages 处理
├── .gitignore
├── 诗经学关键词列表.md            # 完整关键词文档
├── CSSCI期刊列表_文学_语言学_历史学_2025-2026.md
├── README.md
└── CLAUDE.md                   # 本文件
```

## 核心架构与数据流

```
radar.py 运行流程:
  策略1: 15 个关键词 × cnki search → 按期刊过滤 → 收集文章
  策略2: 24 个重点期刊 × cnki search → 按关键词过滤 → 收集文章
      ↓
  fetch_article_details() → search_abstract_web() → 
    对每篇文章，用 AnySearch 搜索论文标题，从网页搜索结果中提取摘要
      ↓
  去重 → 保存为 data/academic_radar_data.json
      ↓
  index.html 读取 JSON → 展示（摘要可展开/折叠）

cnki-search 子进程调用:
  cnki search <关键词> --field=topic --type=journal --from=2026 --to=2026 --sort=date --size=100 --format=json
```

## 关键命令

```bash
# 运行完整搜索（搜索论文 + 获取摘要）
python3 radar.py

# 仅运行搜索（不获取摘要，更快）
python3 radar.py 2>&1 | head -50

# 启动 Web 服务器
python3 server.py
# 访问 http://localhost:8081

# 推送到 GitHub Pages（开 VPN）
git add .
git commit -m "更新说明"
git push

# cnki-search 手动测试
"C:\Users\llo\Desktop\cnki-search\cnki.exe" search 诗经 --format=json
```

## 已知问题和限制

### 1. GitHub Actions 搜索返回 0 条结果（核心未解决 Blocking Issue）

**原因：** GitHub Actions 运行在 ubuntu-latest（美国 Azure 机房），知网 CNKI 屏蔽海外 IP 地址。

**影响：** 空的 `academic_radar_data.json` 被 commit 到 main 分支，覆盖本地真实数据。

**当前变通方案：** 在本地（Windows 电脑，国内 IP）手动运行 `python3 radar.py`，然后 git push 到 GitHub。

**长期解决方案（尚未实施）：**
- **方案 A（推荐）：配置自托管 GitHub Actions Runner**。将 Windows 电脑注册为 self-hosted runner，在本地执行搜索（国内 IP 可访问知网）。需要配置 VPN 分流规则（github.com/api.github.com 走代理，kns.cnki.net 直连）。
- **方案 B：Windows 任务计划程序。** 用 Task Scheduler 定时在本地跑搜索 + git push。

### 2. 摘要获取机制

目前不使用 `cnki detail`（知网详情页反爬极强，验证码无法绕过）。改为通过 **AnySearch CLI 搜索论文标题**，从网页搜索结果片段中提取摘要文本。

**本地运行**时，依赖 AnySearch skill（位于 `~/.claude/skills/anysearch/`）。如果该 skill 不存在，摘要获取步骤自动跳过，搜索结果不含摘要。

**数据字段说明：** `radar.py` 目前为每篇文章保存以下字段：
- `title`, `authors`, `journal`, `journal_full`, `year` — 来自知网搜索
- `cited`, `downloads`, `url` — 来自知网搜索
- `abstract` — 来自网络搜索结果
- `paper_keywords`, `institutions`, `doi`, `fund` — **暂未获取**（知网详情页被拦截，这些字段留空）

### 3. cnki-search 二进制路径

- Windows: 硬编码为 `C:\Users\llo\Desktop\cnki-search\cnki.exe`
- Linux/macOS: 通过 `shutil.which("cnki")` 自动发现
- GitHub Actions: 通过 `go install github.com/ExquisiteCore/cnki-search/cmd/cnki@latest` 实时编译

## GitHub 配置

### 仓库
- URL: `https://github.com/lirsl3807-max/shijing-radar`
- 已设置 GitHub Pages（legacy 模式，main 分支根目录）
- 已配置个人访问令牌 (PAT) 用于 git push 认证

### GitHub Actions（radar.yml）
当前工作流因 #1 (知网屏蔽) 无法正常获取数据。修复前不应启用自动调度。

## 浏览器偏好

使用 Google Chrome，路径为：
`C:\Users\llo\AppData\Local\Google\Chrome\Application\chrome.exe`

## 开发偏好

- 用户使用 Windows 11 系统，Git Bash 终端
- Python 3.12+ 环境，Playwright 1.60.0 已安装
- Go 1.24 环境（用于编译 cnki-search）
- 搜索数据限定在 2026 年
- 用户需要 VPN 才能访问 GitHub
