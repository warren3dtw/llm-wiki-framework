#!/usr/bin/env python3
"""fileback：把一次查詢得到的答案存回知識庫，成為新的一頁。只用標準庫。

用法（通常透過 python scripts/wiki.py fileback）：
  fileback <主題> <類型> <知識點> <描述> --title 標題 --summary 摘要 --from 頁1,頁2 [選項] < 內文.md

  類型：note 或 data
  知識點：放在哪個知識點資料夾。知識點還沒有入口檔時，會建立一份待補的 NOTE.md
  描述：檔名的描述部分，英文小寫和連字號，例如 fj1-vs-fj8
  --from      必填。這個答案依據哪些頁（代號，逗號分隔）。lint 會檢查它們存在
  --kind      筆記不填時是 claim（觀點・主張）；data 一定要填
  --item      要跟既有的項目同編號時填，例如 panel-joint-001（另一種頁已經有這個編號）。
              檔名沿用那一項，兩邊的 pair 自動互相加上
  --atoms     用到的原子，逗號分隔。不填時取多數依據頁共有的原子
  --csv       類型是 data 時必填：資料的 CSV 檔
  --region    不填時：依據頁的地區都相同就沿用，否則 any
  --lang      預設 zh
  內文從標準輸入讀；也可以用 --body 檔案

寫出的頁一律是 status: draft、origin: fileback，等擁有者確認。
編號自動取這個知識點的下一個（全部主題共用一套）。寫完會把頁加進 NOTE.md、重建索引、檢查這一頁。
"""
import datetime
import os
import re
import shutil
import sys
from collections import defaultdict
from pathlib import Path

import build_index
import core
import lint


def option(args, name, default=None):
    if name in args:
        i = args.index(name)
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def add_pair(path, ref):
    """在既有頁的 pair 欄位加上一個代號。"""
    text = path.read_text(encoding="utf-8")
    m = re.search(r"^pair:\s*\[(.*?)\]\s*$", text, re.M)
    if m:
        items = [x.strip() for x in m.group(1).split(",") if x.strip()]
        if ref not in items:
            items.append(ref)
        text = text[:m.start()] + f"pair: [{', '.join(items)}]" + text[m.end():]
        path.write_text(text, encoding="utf-8")


def register(entry, page_path, title, today):
    """把新頁加進知識點的入口檔，放在「回存」小節。"""
    link = f"- [{title}]({os.path.relpath(page_path, entry.parent)})（fileback，{today}）"
    if not entry.exists():
        point = entry.parent.name
        entry.parent.mkdir(parents=True, exist_ok=True)
        entry.write_text(f"---\ntitle: {point}\npoint: {point}\nsummary: 待補：這個知識點是什麼\n"
                         f"updated: {today}\n---\n\n待補：這個知識點是什麼、適用範圍、閱讀順序。\n", encoding="utf-8")
    text = entry.read_text(encoding="utf-8").rstrip("\n")
    if "\n## 回存\n" not in text:
        text += "\n\n## 回存\n\n查詢後存回的頁，還沒排進上面的表。\n"
    entry.write_text(text.rstrip("\n") + "\n" + link + "\n", encoding="utf-8")


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    opts = {k: option(args, f"--{k}") for k in
            ("title", "summary", "from", "atoms", "kind", "item", "csv", "region", "lang", "body")}
    if len(args) < 4 or not opts["title"] or not opts["summary"] or not opts["from"]:
        sys.exit(__doc__)
    wiki, rtype, point, desc = args[:4]
    base = core.ROOT / "wikis" / wiki
    if not (base / "WIKI.md").exists():
        sys.exit(f"沒有主題 {wiki}")
    if rtype not in ("note", "data"):
        sys.exit("類型要是 note 或 data")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", point) or not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", desc):
        sys.exit("知識點和描述只能用英文小寫、數字和連字號")
    records = core.load_records()

    kind = opts["kind"] or ("claim" if rtype == "note" else None)
    if not kind or kind not in core.TYPES[rtype]["kinds"]:
        sys.exit(f"--kind 應為 {'、'.join(core.TYPES[rtype]['kinds'])}")
    if rtype == "data" and not opts["csv"]:
        sys.exit("data 要給 --csv")

    partners = []
    if opts["item"]:
        item = opts["item"]
        partners = [r for r in records.values() if r.get("item") == item]
        if not partners:
            sys.exit(f"沒有編號 {item} 的頁")
        if any(r["type"] == rtype for r in partners):
            sys.exit(f"編號 {item} 已經有 {rtype} 頁了")
        if partners[0]["wiki"] != wiki or partners[0]["point"] != point:
            sys.exit(f"編號 {item} 屬於 {partners[0]['wiki']} 的 {partners[0]['point']}")
        name = partners[0]["name"]
    else:
        item = core.next_item(point, records)
        name = f"{item}-{desc}"
    rid = f"{wiki}:{rtype}/{name}"

    sources = [s.strip() for s in opts["from"].split(",") if s.strip()]
    targets = [records[t] for t in (core.resolve(ref, wiki, records) for ref in sources) if t]
    atoms = [a.strip() for a in (opts["atoms"] or "").split(",") if a.strip()]
    if not atoms and targets:
        counts = defaultdict(int)
        for t in targets:
            for a in t.get("atoms", []):
                counts[a] += 1
        atoms = [a for a, n in counts.items() if n * 2 >= len(targets)] or list(targets[0].get("atoms", []))
    regions = {t.get("region") for t in targets if t.get("region")}
    region = opts["region"] or (regions.pop() if len(regions) == 1 else "any")
    body = Path(opts["body"]).read_text(encoding="utf-8") if opts["body"] else sys.stdin.read()
    today = datetime.date.today().isoformat()

    def listing(items):
        return "[" + ", ".join(items) + "]"

    folder = base / core.TYPES[rtype]["folder"] / point
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{name}.md"
    pair = [f"{r['type']}/{r['name']}" for r in partners]
    path.write_text(f"""---
title: {opts['title']}
type: {rtype}
kind: {kind}
point: {point}
item: {item}
pair: {listing(pair)}
summary: {opts['summary']}
atoms: {listing(atoms)}
from: {listing(sources)}
origin: fileback
lang: [{opts['lang'] or 'zh'}]
region: {region}
status: draft
updated: {today}
---

{body.strip()}
""", encoding="utf-8")
    if rtype == "data":
        shutil.copyfile(opts["csv"], path.with_suffix(".csv"))
    for r in partners:
        add_pair(r["path"], f"{rtype}/{name}")
    register(base / "note" / point / core.ENTRY, path, opts["title"], today)
    rel = path.relative_to(core.ROOT).as_posix()
    print(f"已回存：{rid}（{rel}）")

    build_index.main()
    records = core.load_records()
    errors, warnings = [], defaultdict(list)
    lint.check(records, errors, warnings)
    lint.check_items(records, errors)
    lint.check_entries(records, errors, warnings)
    mine = [e for e in errors if rel in e or item in e or f"/{point}/" in e]
    for e in mine:
        print(f"  錯誤：{e}")
    for kind_name, items in warnings.items():
        for it in items:
            if it.startswith(rel):
                print(f"  提醒：{kind_name}：{it}")
    if mine:
        print("請修正上面的錯誤，再執行 python scripts/wiki.py lint。")
        sys.exit(1)


if __name__ == "__main__":
    main()
