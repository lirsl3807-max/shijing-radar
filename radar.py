#!/usr/bin/env python3
"""
academic_radar v1 — 学术雷达：从知网搜索诗经学文章
策略：按关键词搜索 + 按目标期刊过滤
"""
import json, subprocess, sys, time, os
sys.stdout.reconfigure(encoding="utf-8")

CNKI_BIN = r"C:\Users\llo\Desktop\cnki-search\cnki.exe"

# 在 Linux/macOS 或 PATH 环境下，自动查找 cnki 命令
import shutil
if not os.path.exists(CNKI_BIN):
    CNKI_BIN = shutil.which("cnki") or CNKI_BIN

# AnySearch CLI 路径（用于网络搜索摘要）
ANYSEARCH_CLI = os.path.expanduser(r"~\AppData\Roaming\Claude\skills\anysearch\scripts\anysearch_cli.py")
if not os.path.exists(ANYSEARCH_CLI):
    ANYSEARCH_CLI = os.path.expanduser(r"~\.claude\skills\anysearch\scripts\anysearch_cli.py")
if not os.path.exists(ANYSEARCH_CLI):
    ANYSEARCH_CLI = shutil.which("anysearch") or ANYSEARCH_CLI

# 目标期刊（CSSCI 文学/语言学/历史学/考古学 正刊 + 扩展版 + 集刊）
# 来源：CSSCI（2025-2026）期刊列表
TARGET_JOURNALS = [
    # ═══ CSSCI 正刊 — 文学类 ═══
    "文学评论", "文学遗产", "文艺理论研究", "文艺理论与批评",
    "文艺争鸣", "民族文学研究", "中国比较文学", "中国文学批评",
    "中国文学研究", "中国诗学", "中国古代文学理论研究",

    # ═══ CSSCI 正刊 — 语言学类 ═══
    "中国语文", "当代语言学", "语言教学与研究", "语言科学",
    "语言文字应用", "语言研究", "语文研究", "汉语学报",
    "古汉语研究", "方言", "民族语文",

    # ═══ CSSCI 正刊 — 历史学类 ═══
    "历史研究", "中国史研究", "中国史研究动态", "史学月刊",
    "史学集刊", "史学理论研究", "史学史研究",
    "文史", "文献", "中华文史论丛", "史林",
    "古代文明", "国际汉学", "历史语言研究所集刊",
    "中国哲学史", "孔子研究", "民俗研究",

    # ═══ CSSCI 正刊 — 考古学类 ═══
    "考古", "考古学报", "考古与文物", "文物",
    "江汉考古", "故宫博物院院刊", "中原文物", "敦煌学辑刊",

    # ═══ CSSCI 正刊 — 综合性社科 & 高校学报 ═══
    "中国社会科学", "文史哲", "学术月刊", "社会科学战线",
    "社会科学研究", "学术研究", "思想战线", "江汉论坛",
    "贵州社会科学", "山东社会科学", "甘肃社会科学", "河北学刊",
    "中华文化论坛", "学术界",
    "北京大学学报(哲学社会科学版)", "北京大学学报(哲社版)",
    "清华大学学报(哲学社会科学版)", "清华大学学报(哲社版)",
    "中国人民大学学报", "北京师范大学学报(社会科学版)", "北京师范大学学报(社科版)",
    "复旦学报(社会科学版)", "复旦学报(社科版)",
    "南京大学学报(哲学·人文科学·社会科学)", "南京大学学报(哲·人文·社科)",
    "浙江大学学报(人文社会科学版)", "浙江大学学报(人文社科版)",
    "四川大学学报(哲学社会科学版)", "四川大学学报(哲社版)",
    "武汉大学学报(哲学社会科学版)", "武汉大学学报(哲社版)",
    "华东师范大学学报(哲学社会科学版)", "华东师范大学学报(哲社版)",
    "上海交通大学学报(哲学社会科学版)", "上海交通大学学报(哲社版)",
    "中山大学学报(社会科学版)", "中山大学学报(社科版)",
    "齐鲁学刊", "海岱学刊",
    "烟台大学学报(哲学社会科学版)", "烟台大学学报(哲社版)",

    # ═══ CSSCI 扩展版 ═══
    "中国典籍与文化", "民间文化论坛", "中国非物质文化遗产",
    "中国地方志", "历史教学", "历史教学问题", "历史评论",

    # ═══ CSSCI 集刊 ═══
    "出土文献", "简帛", "甲骨文与殷商史",
    "中国经学", "经学文献研究集刊", "经学研究",
    "历史文献研究", "古典文献研究",
    "文献语言学", "中国文字研究", "语言学论丛",
    "诸子学刊", "诗书画", "中国美学研究",
    "中国语言文学研究", "文学理论前沿",
    "孔学堂", "国际儒学(中英文)", "经典与解释",
    "文津学志", "古籍研究", "古籍保护研究",
    "敦煌研究", "汉语史研究集刊",
    "历史地理", "中国历史地理论丛",
    "唐宋历史评论", "宋史研究论丛",
]

# 诗经相关关键词
# 来源：用户指定的完整关键词列表
SHIJING_KEYWORDS = [
    # ── 诗经基本名称 ──
    "诗经",
    # ── 三家诗 ──
    "三家诗", "鲁诗", "齐诗", "韩诗", "韩诗外传",
    # ── 毛诗系统 ──
    "毛诗", "毛传", "郑笺", "孔疏", "诗序", "诗谱",
    "毛诗正义", "毛诗传笺",
    # ── 诗学概念 ──
    "风雅颂", "赋比兴", "诗教", "诗言志",
    "四始", "六义", "正变",
    # ── 专题研究 ──
    "诗乐关系", "诗礼关系", "诗经用韵",
    "诗经名物", "诗经地理", "诗经历史",
    # ── 出土文献与诗经 ──
    "安大简·诗经", "阜阳汉简·诗经",
    "上博简·孔子诗论", "清华简·周公之琴舞",
    "郭店简·性自命出", "海昏侯墓·诗经",
    "敦煌诗经", "熹平石经", "出土诗论",
    # ── 历代诗经学著作 ──
    "诗集传", "吕氏家塾读诗记",
    "诗缉", "诗疑", "诗经通论", "诗经原始",
    "诗毛氏传疏", "毛诗传笺通释",
    "诗三家义集疏", "三家诗辑佚",
]

# 标题级相关度过滤关键词（用于策略2的二次过滤 + 策略1的标题验证）
RELEVANCE_KEYWORDS = SHIJING_KEYWORDS + [
    "诗经用韵", "诗经名物", "诗经地理", "诗经历史", "诗经学史",
    "安大简", "阜阳汉简", "海昏侯", "敦煌诗经", "石经",
    "出土诗论",
    "诗乐", "诗礼",
    "国风", "雅颂", "二南",
    "采诗", "献诗", "删诗",
    "孔门诗教", "先秦诗学", "汉唐诗经",
    "性自命出", "郭店简",
    "上博简", "清华简",
]


def run_cnki_search(query, field="topic", year_from=2026, year_to=2026, size=100):
    """运行 cnki-search 并返回解析后的 JSON"""
    cmd = [
        CNKI_BIN, "search", query,
        f"--field={field}",
        "--type=journal",
        f"--from={year_from}",
        f"--to={year_to}",
        "--sort=date",
        f"--size={size}",
        "--format=json"
    ]
    r = subprocess.run(cmd, capture_output=True, timeout=90)
    if r.returncode != 0:
        return {"total_hits": 0, "results": []}
    try:
        raw = r.stdout.decode("utf-8", errors="surrogatepass").replace("\udca7", "")
        return json.loads(raw)
    except:
        raw = r.stdout.decode("gbk", errors="replace")
        import re
        raw = re.sub(r'[\ud800-\udfff]', '', raw)
        return json.loads(raw)


def search_abstract_web(title, authors):
    """通过网络搜索论文摘要

    用论文标题在搜索引擎中查找，从搜索结果片段中提取摘要。
    需要安装 AnySearch CLI 工具。
    """
    if not os.path.exists(ANYSEARCH_CLI):
        return None

    # 清理标题中的特殊字符
    clean_title = title.replace("\udca7", "").replace('《', '').replace('》', '').strip()
    first_author = authors.split(';')[0].strip() if authors else ''

    # 多轮搜索策略
    queries = [
        f"{clean_title} {first_author} 摘要",
        f'"{title}" 摘要',
    ]

    best_abstract = ""
    for query in queries:
        if len(query) > 150:
            query = query[:150]

        cmd = [sys.executable, ANYSEARCH_CLI, "search", query]
        try:
            r = subprocess.run(cmd, capture_output=True, timeout=25)
        except:
            continue

        output = r.stdout.decode("utf-8", errors="replace")
        if not output:
            continue

        import re

        # 模式1: JSON "abstracts": "..." （sciencechain 等结构化数据）
        for m in re.finditer(r'["\']abstracts?["\']\s*:\s*["\']([^"\']{50,})["\']', output):
            txt = m.group(1).strip()
            if len(txt) > len(best_abstract):
                best_abstract = txt

        # 模式2: 搜索结果项中的 "摘要：" 文本
        for m in re.finditer(r'摘\s*[要：:]\s*([^\n]{30,}(?:\n[^\n]+){0,8})', output):
            txt = re.sub(r'<[^>]+>', '', m.group(1))
            txt = re.sub(r'https?://\S+', '', txt)
            txt = re.sub(r'\s+', ' ', txt).strip()
            if len(txt) > 50 and len(txt) > len(best_abstract):
                # 过滤掉明显不是摘要的内容
                if not any(kw in txt for kw in ['JavaScript', 'function', 'var ']):
                    best_abstract = txt

        # 模式3: 搜索结果项的长文本描述（>100字）
        items = re.split(r'### \d+\.', output)
        for item in items:
            lines = [l.strip() for l in item.split('\n')
                     if l.strip() and not l.startswith('- **URL') and not l.startswith('#')]
            for line in lines:
                # 跳过标题行
                if len(line) < 80 or '《' not in line:
                    continue
                text = re.sub(r'https?://\S+', '', line).strip()
                if len(text) > 80 and len(text) > len(best_abstract):
                    if any(kw in text for kw in ['摘要', 'Abstract', '研究', '分析', '本文', '论述', '探讨', '提出']):
                        best_abstract = text

        # 如果已经找到不错的摘要，停止搜索
        if len(best_abstract) > 100:
            break

    # 截断
    if len(best_abstract) > 600:
        best_abstract = best_abstract[:600]

    return best_abstract if len(best_abstract) > 40 else None


def check_relevance(title):
    """检查标题是否与诗经相关（使用扩展关键词列表）"""
    t = title.replace("\udca7", "").strip()
    for kw in RELEVANCE_KEYWORDS:
        if kw in t:
            # 特殊情况："诗序"可能是普通诗歌序言而非《毛诗序》
            if kw == "诗序" and "谢灵运诗序" in t:
                continue
            # 特殊情况："国风"可能匹配"中国风"（中国风格）
            if kw == "国风" and "中国风" in t:
                continue
            return True
    return False


def search_all():
    """主搜索流程"""
    all_articles = []
    seen = set()

    # 策略1: 按关键词搜（诗经相关关键词逐一搜索）
    print("策略1: 关键词搜索 + 期刊过滤")
    # 挑选代表性关键词进行搜索（避免关键词过多导致总耗时太长）
    search_keywords = ["诗经", "毛诗", "三百篇", "诗序", "三家诗",
                       "风雅颂", "赋比兴", "诗教", "诗言志",
                       "孔子诗论", "诗集传", "诗经原始",
                       "诗乐关系", "诗礼关系", "诗经名物"]
    for kw in search_keywords:
        print(f"  搜索关键词: {kw}...", end=" ", flush=True)
        data = run_cnki_search(kw)
        n = 0
        for p in data.get("results", []):
            src = p.get("source", "")
            # 检查是否匹配目标期刊
            matched_journal = None
            for j in TARGET_JOURNALS:
                if j in src:
                    matched_journal = j
                    break
            if not matched_journal:
                continue
            title = p["title"].replace("\udca7", "").strip()
            if title in seen:
                continue
            # 策略1也做标题相关度过滤
            if not check_relevance(title):
                continue
            seen.add(title)
            all_articles.append({
                "title": title,
                "authors": "; ".join(p.get("authors", [])),
                "journal": matched_journal,
                "journal_full": src,
                "year": p.get("year", ""),
                "cited": p.get("cited", 0),
                "downloads": p.get("downloads", 0),
                "url": p.get("url", ""),
                "keyword": kw,
                "source_api": "知网",
                "abstract": "",
                "paper_keywords": [],
                "institutions": [],
                "doi": "",
                "fund": "",
            })
            n += 1
        print(f"命中{data['total_hits']}条, 目标期刊{n}篇")
        time.sleep(1.5)

    # 策略2: 按期刊名搜（对产出高的期刊单独搜索）
    print("\n策略2: 重点期刊单独搜索")
    key_journals = [
        "文史", "文献", "文学遗产", "中华文史论丛",
        "出土文献", "简帛", "中国经学", "孔子研究",
        "古典文献研究", "中国典籍与文化",
        "文学评论", "文艺研究", "文史哲", "历史研究",
        "中国史研究", "文物", "考古", "敦煌学辑刊",
        "文献语言学", "中国文字研究", "经学文献研究集刊",
        "文津学志", "古籍研究", "中国诗学",
    ]
    for jname in key_journals:
        print(f"  搜索期刊: {jname}...", end=" ", flush=True)
        data = run_cnki_search(jname, field="source")
        n = 0
        for p in data.get("results", []):
            if jname not in p.get("source", ""):
                continue
            title = p["title"].replace("\udca7", "").strip()
            if not check_relevance(title):
                continue
            if title in seen:
                continue
            seen.add(title)
            all_articles.append({
                "title": title,
                "authors": "; ".join(p.get("authors", [])),
                "journal": jname,
                "journal_full": p.get("source", ""),
                "year": p.get("year", ""),
                "cited": p.get("cited", 0),
                "downloads": p.get("downloads", 0),
                "url": p.get("url", ""),
                "keyword": f"期刊_{jname}",
                "source_api": "知网",
                "abstract": "",
                "paper_keywords": [],
                "institutions": [],
                "doi": "",
                "fund": "",
            })
            n += 1
        print(f"总{data['total_hits']}篇, 诗经相关{n}篇")
        time.sleep(1.5)

    return all_articles


def fetch_article_details(articles):
    """通过网络搜索逐一获取论文摘要"""
    print("\n获取论文摘要 (通过网络搜索)...")
    total = len(articles)
    n_found = 0
    for i, a in enumerate(articles):
        title = a.get("title", "")
        authors = a.get("authors", "")
        print(f"  [{i+1}/{total}] {title[:40]}...", end=" ", flush=True)

        abstract = search_abstract_web(title, authors)
        if abstract:
            a["abstract"] = abstract
            n_found += 1
            abs_len = len(abstract)
            print(f"✅ 摘要{abs_len}字")
        else:
            print("⚠️  未找到")
        # 避免请求过快
        time.sleep(1)

    print(f"\n摘要获取完成: {n_found}/{total} 篇")
    return articles


if __name__ == "__main__":
    print("=" * 60)
    print("学术雷达 v1 — 诗经学文献追踪")
    print("=" * 60)

    articles = search_all()

    # 获取摘要等详情
    articles = fetch_article_details(articles)

    # 去重
    unique = []
    seen_titles = set()
    for a in articles:
        if a["title"] not in seen_titles:
            seen_titles.add(a["title"])
            unique.append(a)

    # 保存
    output = {
        "source": "知网-CNKI",
        "year": "2026",
        "total": len(unique),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "articles": unique,
    }
    # 保存到 data/ 目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(script_dir, "data", "academic_radar_data.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'=' * 60}")
    print(f"完成！共找到 {len(unique)} 篇")
    has_abs = sum(1 for a in unique if a.get("abstract"))
    print(f"其中有摘要: {has_abs} 篇")
    print()
    for a in unique:
        abs_icon = "📄" if a.get("abstract") else "❌"
        print(f"  {abs_icon} [{a['journal']}] {a['authors'][:30]}: {a['title'][:50]}")
    print(f"\n已保存: {path}")

