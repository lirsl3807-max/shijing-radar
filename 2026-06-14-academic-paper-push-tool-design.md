# 学术文献推流工具 — 设计文档

> 日期：2026-06-14
> 状态：设计讨论阶段

## 1. 项目概述

一个学术文献推流工具，支持用户选定关键词和领域，定时推送相关学术文章到微信/网页。类似 Perl（珀尔）或 arXiv Daily 的文献推送服务。

### 使用场景

- **个人自用** — 自己订阅关键词，每天接收推送
- **开源可自部署** — 他人也能 fork 部署，设计上考虑低门槛

## 2. 推送渠道

| 渠道 | 方案 | 备注 |
|------|------|------|
| **微信** | 企业微信机器人（Webhook） | GitHub Actions 在境外，企业微信机器人支持 webhook，不受服务器位置限制 |
| **网页** | GitHub Pages / 静态页面 | 推送到网页可浏览，手机也能访问 |

## 3. 数据源实测结果

### 3.1 国家哲学社会科学文献中心（ncpssd.org）⭐ 推荐

| 项目 | 结果 |
|------|------|
| 搜索接口 | `POST /searchHandler/search` |
| 无需鉴权 | ✅ 完全开放，curl 直调即可 |
| 返回摘要 | ✅ `remark` 字段直接返回摘要 |
| 数据量 | 2700 万+ 条 |
| 无反爬 | ✅ 实测通过 |
| 搜索参数 | `search`, `pageNum`, `pageSize`, `sort`, `sType` |
| 查询语法 | IKTE（题名/关键词）、IKCR（作者）、PQ 表达式 |
| 适用场景 | **推流主力数据源**，社科文献核心覆盖 |

示例请求：
```
POST https://www.ncpssd.org/searchHandler/search
Content-Type: application/x-www-form-urlencoded

search=(IKTE="诗经" OR IKPYTE="诗经" OR IKST="诗经" OR IKET="诗经" OR IKSE="诗经")
pageNum=1
pageSize=10
sort=synUpdateType|DESC,date|DESC,ik_subject|DESC,id|DESC
sType=0
```

### 3.2 知网 CNKI（kns.cnki.net）

| 项目 | 结果 |
|------|------|
| 搜索接口 | `kns8s/search`（通过 `cnki-search` Go 库/CLI） |
| 搜索反爬 | ✅ 轻，校园网 IP 下连续搜索正常 |
| 搜索返回 | 标题、作者、来源、年份、被引、下载数 |
| **摘要** | ❌ 搜索结果无摘要，详情页 `kcms2/article/abstract` 有 captcha 反爬 |
| 详情页反爬 | ❌ 严格，`captcha or anti-bot challenge detected` |
| 校园网 | ✅ 四川大学 IP 可访问，无需额外配置 |
| GitHub Actions | ❌ 云 IP 不在中国大学段，搜索可能直接 403 |

#### 关键发现：cnki-search Go 库

- GitHub: `github.com/ExquisiteCore/cnki-search`
- 方式：反向工程知网 HTTP 接口，无需浏览器
- 实测：搜索"诗经" 19763 条命中，毫秒级返回
- 格式：JSON / table / citation
- 字段：标题、作者、来源、年份、被引、下载
- **可以作为 Go 库直接集成，也可作为 CLI 子进程调用**
- 作为库调用比 CLI 更优（避免每次启动获取 session 的开销）

### 3.3 PubScholar 中科院公益学术平台

| 项目 | 结果 |
|------|------|
| API | `hky/open/resources/api/v1/articles` |
| 直接调用 | ❌ 403（需要页面会话凭证） |
| Playwright 加载后搜索 | ✅ 可用，返回摘要 |
| 搜索"诗经"结果 | 15,294 条 |
| 搜索结果 | 标题、作者、期刊、**摘要**、关键词、原文链接 |
| 部署依赖 | ⚠️ 需要浏览器环境（Playwright） |
| GitHub Actions | ⚠️ 可装 Playwright，可能可行 |

### 3.4 万方数据

| 项目 | 结果 |
|------|------|
| 开放平台 API | `https://open.wf.pub` 提供 REST API |
| 需要 | AppKey + AppSecret（注册申请） |
| 摘要 | ✅ 官方 API 返回 `Abstract` 字段 |
| Python SDK | `wfdata-open-skills`（GitHub 官方开源） |
| 状态 | ⏳ 待注册测试 |

### 3.5 其他未详细测试的源

| 数据源 | 说明 |
|--------|------|
| 维普 CQVIP | 无公开免费 API，需机构订阅 |
| 读秀/超星 | 图书为主，反爬未知 |
| 上海图书馆开放数据平台 | 有 API 文档，需申请 key |

## 4. 数据源推荐策略

| 优先级 | 数据源 | 原因 | 部署兼容 |
|:-----:|--------|------|:-------:|
| **①** | **国社科 ncpssd** | 完全开放、有摘要、无反爬、简单 curl 调用 | 本地 ✅ GitHub Actions ✅ |
| **②** | **知网 CNKI** | 搜索量大、覆盖全（含理工）、cnki-search 库可集成 | 本地 ✅（需校园网）❌ GitHub Actions |
| **③** | **PubScholar** | 中科院平台、有摘要、覆盖理工商社 | 本地 ✅ GitHub Actions ⚠️ |
| **④** | **万方** | 注册 AppKey 后可作为补充 | 本地 ✅ GitHub Actions ✅ |

## 5. 反爬策略总结

| 数据源 | 反爬级别 | 应对策略 |
|--------|:-------:|---------|
| 国社科 | 无 | 直接调 API，无需特殊处理 |
| 知网搜索 | 轻 | 校园网 IP 下正常，控制频率即可（日 15 篇远低于阈值） |
| 知网详情 | 重 | **放弃**，推流不依赖摘要，用户点击原文链接查看 |
| PubScholar | 中 | 需要浏览器会话，Playwright 可解决 |
| 万方 API | 无（需 key） | 正常 API 调用 |

## 6. 部署架构

### 方案 A：GitHub Actions 为主（推荐）

```
GitHub Actions（定时触发，如每天早上 8 点）
  │
  ├── 国社科 API 直调 ──────────→ 带摘要的结果
  ├── [可选] PubScholar Playwright → 带摘要的结果
  │
  ├── 合并去重
  │
  ├── 生成推送内容
  │
  ├── 企业微信 Webhook ─────────→ 微信推送
  └── GitHub Pages 更新 ────────→ 网页查看
```

- ✅ 完全免费
- ✅ 开源友好（fork 即用）
- ✅ 支持 Playwright
- ⚠️ 知网不可用（非校园网 IP）

### 方案 B：本地 + GitHub Actions 混合

```
本地（校园网，定时任务）
  ├── 知网 cnki-search ──→ 元数据
  └── 推送结果到 GitHub Repo

GitHub Actions
  ├── 国社科 API ──→ 带摘要
  ├── [可选] PubScholar
  ├── 合并两份结果
  └── 推送微信 + Pages
```

- ✅ 知网数据可用
- ❌ 需要本地常开机

## 7. 技术选型初探

| 组件 | 候选 |
|------|------|
| 语言 | Go（cnki-search 是 Go 库，可集成）或 Python（生态丰富） |
| 知网获取 | `github.com/ExquisiteCore/cnki-search` 作为 Go 库集成 |
| 国社科获取 | 直接 HTTP POST |
| 自动搜索 | Playwright（PubScholar 可选） |
| 微信推送 | 企业微信机器人 Webhook |
| 定时调度 | GitHub Actions cron 或本地 cron / 任务计划程序 |
| 网页展示 | GitHub Pages / 静态页面 |
| 配置管理 | 关键词 + 领域 的配置文件（YAML/JSON） |

## 8. 待定问题

- 推送频率：每日 / 每周 / 用户自定义？
- 关键词管理方式：配置文件 / Web 界面？
- 是否支持其他源扩展（如 arXiv / OpenAlex / CrossRef）？
- 是否做去重（同一篇文章在多个源出现）？
- 是否全文检索语义推荐，还是仅关键词匹配？
