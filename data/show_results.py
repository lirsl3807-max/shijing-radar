#!/usr/bin/env python3
import json, sys
sys.stdout.reconfigure(encoding="utf-8")

with open("C:/Users/llo/Desktop/shi_jing_2026.json", "r", encoding="utf-8") as f:
    raw = f.read()
data = json.loads(raw)
print(f"总命中: {data['total_hits']}")
print(f"返回: {data['fetched']} 篇\n")

cssci = ["文史","文献","文学遗产","中华文史论丛","中国典籍与文化",
         "文史哲","出土文献","简帛","中国经学","孔子研究","中国哲学史",
         "历史研究","中国史研究","古典文献研究","文献语言学","敦煌研究",
         "中华文化论坛","考古","考古学报","文物"]
cssci_hits = 0
for p in data["results"]:
    src = p.get("source", "")
    matched = [j for j in cssci if j in src]
    if matched:
        cssci_hits += 1
        tag = "✅"
    else:
        tag = " "
    title = p["title"].replace("\udca7", "").strip()
    authors = "; ".join(p.get("authors", []))
    print(f"  {tag} [{p['year']}] {title[:55]}")
    print(f"     {authors[:50]}")
    print(f"     📰 {src}")
    if matched:
        print(f"     📖 {matched[0]}")
    print()

print(f"--- 其中目标期刊文章: {cssci_hits}/{data['fetched']} 篇 ---")
print(f"--- 总命中 108 篇，目前只返回了前30篇 ---")
