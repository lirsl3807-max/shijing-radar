# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**诗经学文献雷达 (Academic Radar)** — 自动从知网 (CNKI) 追踪 CSSCI 期刊中的《诗经》研究动态。

- 覆盖 **111 种 CSSCI 期刊**（文学/语言学/历史学/考古学/社科综合/扩展版/集刊，全部在知网可搜）
- 使用用户指定的精确关键词列表过滤（标题匹配，非简单期刊匹配）
- 当前（2026 上半年）已收录 **21 篇** 相关论文，**全部有摘要**
- 部署在 GitHub Pages，手机可访问

## 技术栈

| 组件 | 说明 |
|------|------|
| **[cnki-search](https://github.com/ExquisiteCore/cnki-search)** | Go 编写的知网搜索 CLI，逆向 KNS8S HTTP API |
| **radar.py** (Python) | 搜索编排脚本——两阶段搜索（关键词+期刊）+ 网络摘要获取 |
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
│   └── radar.yml               # GitHub Actions 工作流（暂不能正常使用）
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
  策略1: 15 个关键词 × cnki search → 按期刊过滤 → 按标题关键词过滤 → 收集文章
  策略2: 111 种期刊 × cnki search (按 source 字段，分批20个/组，防限流) →
         按标题关键词过滤 → 收集文章（含重试机制）
      ↓
  fetch_article_details() → search_abstract_web() → 
    对每篇文章，用 AnySearch 搜索论文标题，从网页搜索结果中提取摘要
      ↓
  标题归一化（去《》内空格 + 繁转简）→ 去重 →
  保存为 data/academic_radar_data.json
      ↓
  index.html 读取 JSON → 展示（摘要可展开/折叠）

cnki-search 子进程调用:
  cnki search <关键词> --field=topic --type=journal --from=2026 --to=2026 --sort=date --size=100 --format=json
  cnki search <期刊名> --field=source --type=journal --from=2026 --to=2026 --sort=date --size=100 --format=json
```

## 限流防护

策略2 搜索 111 种期刊时，每 20 个期刊休息 5 秒，防止知网 KNS8S API 因请求过快限流。如果某期刊搜索返回 0 条，自动重试一次（等待 3 秒）。

## 去重逻辑

最终去重时做两级归一化：
1. **空格归一化**：去除《》内部所有空格（`《 诗经 》` → `《诗经》`，`《毛诗 正义》` → `《毛诗正义》`）
2. **繁简归一**：繁体标题转简体后再比较（`詩經` → `诗经`）

## 搜索与过滤逻辑详解

### 收录标准

文章必须同时满足两个条件才会被收录：
1. **期刊匹配**：文章来源必须在 `TARGET_JOURNALS` 列表中（95 种 CSSCI 期刊）
2. **标题关键词匹配**：文章标题必须包含用户指定的诗经学关键词之一

### 关键词列表

`RELEVANCE_KEYWORDS` 包含以下类别（精确匹配，非子串匹配）：

- 诗经基本名称：诗经
- 三家诗：三家诗、鲁诗、齐诗、韩诗、韩诗外传
- 毛诗系统：毛诗、毛传、郑笺、孔疏、诗序、诗谱、毛诗正义、毛诗传笺
- 诗学概念：风雅颂、赋比兴、诗教、诗言志、四始、六义、正变
- 专题研究：诗乐关系、诗礼关系、诗经用韵、诗经名物、诗经地理、诗经历史
- 出土文献：安大简·诗经、阜阳汉简·诗经、上博简·孔子诗论、清华简·周公之琴舞、郭店简·性自命出、海昏侯墓·诗经、敦煌诗经、熹平石经、出土诗论
- 历代诗经学著作：诗集传、吕氏家塾读诗记、诗缉、诗疑、诗经通论、诗经原始、诗毛氏传疏、毛诗传笺通释、诗三家义集疏、三家诗辑佚
- 补充关键词：诗经用韵、诗经名物、诗经地理、诗经历史、诗经学史、安大简、阜阳汉简、海昏侯、敦煌诗经、石经、出土诗论、诗乐、诗礼、国风、雅颂、二南、采诗、献诗、删诗、孔门诗教、先秦诗学、汉唐诗经、性自命出、郭店简、上博简、清华简

### 关键词误匹配已处理的特例

- `国风` 匹配 `中国风` → 已排除（如"被操纵的主体性"）
- `诗序` 匹配谢灵运诗歌序言 → 已排除（如"论谢灵运诗的制题艺术"）
- `诗谱` 匹配 `新诗谱` → 已排除（胡亮《新诗谱》是现代诗论，非郑玄《诗谱》）

### 收录历史

- 最初：28 篇（策略1未做标题过滤，混入无关文章）
- v2 (6/14)：18 篇（增加标题过滤 + 修正关键词误匹配）
- v3 (6/15)：21 篇（策略2覆盖全部111种CSSCI期刊 + 繁简通配）

## 摘要获取机制

不使用 `cnki detail`（知网详情页反爬极强，验证码无法绕过）。改为通过 **AnySearch CLI 搜索论文标题**，从网页搜索结果片段中提取摘要文本。

- 当前覆盖率：**21/21 篇（100%）**
- 即使搜不到摘要，文章仍会收录（abstract 字段留空）
- 依赖 AnySearch skill（位于 `~/.claude/skills/anysearch/`），不存在时自动跳过

## 繁简通配机制

2026-06-15 新增：所有关键词匹配和期刊名匹配均支持繁体中文。

- `check_relevance()` 使用 `zhconv` 库将标题转为简体后再做关键词子串匹配
- 策略1/策略2的期刊来源字段匹配同样做繁转简
- 去重阶段也做繁简归一，防止同一篇文章因繁简差异重复收录
- 依赖 `zhconv` Python 库（已安装）

## 期刊名称注意事项

所有 111 种目标期刊均已确认在知网可通过 `--field=source` 搜索（`经典与解释` 因知网无此刊已移除）。名称已修正的：

| CLAUDE.md 中的名称 | 知网实际名称 | 状态 |
|---|---|---|
| 中国诗学 | 中国诗学研究 | ✅ 已验证 |
| 中国古代文学理论研究 | 古代文学理论研究 | ✅ 已验证 |
| 其他集刊命名 | 知网使用与CSSCI基本一致 | ✅ 全部可搜 |

## 关键命令

```bash
# 运行完整搜索（搜索论文 + 获取摘要，约 10 分钟）
python3 radar.py

# 启动 Web 服务器
python3 server.py
# 访问 http://localhost:8081

# 推送到 GitHub Pages（需开 VPN）
git add .
git commit -m "更新说明"
git push

# cnki-search 手动测试
"C:\Users\llo\Desktop\cnki-search\cnki.exe" search 诗经 --format=json

# 测试某个期刊是否在知网可搜（不限年份）
"C:\Users\llo\Desktop\cnki-search\cnki.exe" search "中国经学" --field=source --size=3 --format=json
```

## 已知问题和限制

### 1. GitHub Actions 搜索返回 0 条结果（核心未解决）

**原因：** GitHub Actions（ubuntu-latest，美国 Azure 机房）IP 被知网屏蔽。

**当前变通方案：** 在本地手动运行 `python3 radar.py`，然后 git push。

**长期方案（未实施）：** 配置自托管 GitHub Actions Runner（Windows 电脑国内 IP），需配置 VPN 分流规则。

### 2. AnySearch 依赖

摘要获取依赖 AnySearch skill，这在 GitHub Actions 上不可用。如果将来要自动部署，需要在 GitHub Actions 上使用不同的摘要获取方式或跳过摘要步骤。

### 3. 集刊2026年卷尚未出版

大部分 CSSCI 集刊（中国经学、简帛、古典文献研究、经学文献研究集刊、文献语言学 等）为年刊/半年刊，2026年卷尚未出版。知网可搜到往年文章，但 2026 年暂无数据。预计下半年至年底陆续上线。

### 4. 知网详情页完全不可用

`cnki detail`、Python requests、Playwright/Chrome 所有方式均被知网详情页的验证码拦截。故 `paper_keywords`、`institutions`、`doi`、`fund` 等字段暂无法获取。

### 5. cnki-search 二进制路径

- Windows: `C:\Users\llo\Desktop\cnki-search\cnki.exe`
- Linux: `shutil.which("cnki")`
- GitHub Actions: `go install github.com/ExquisiteCore/cnki-search/cmd/cnki@latest`

## GitHub 配置

- 仓库: `https://github.com/lirsl3807-max/shijing-radar`
- GitHub Pages: legacy 模式，main 分支根目录
- 已配置 PAT 用于 git push 认证
- GitHub Actions 因知网 IP 屏蔽暂不可用

## 浏览器偏好

使用 Google Chrome：`C:\Users\llo\AppData\Local\Google\Chrome\Application\chrome.exe`

## 开发环境

- Windows 11 + Git Bash
- Python 3.12+
- Go 1.24（编译 cnki-search）
- Playwright 1.60.0 已安装
- 仅搜索 2026 年数据
- 访问 GitHub 需 VPN
