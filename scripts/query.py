#!/usr/bin/env python3
"""query：查詢知識庫。給使用知識庫的 agent 和人用，不修改任何檔案。只用標準庫。

用法：python scripts/wiki.py query <指令> [參數]

  overview                                  有哪些主題、各有多少頁
  search <關鍵字...> [篩選]                  找頁。關鍵字可以用中、英、日文，會透過原子互相對應
  atom <名稱>                                查原子（詞條）：各語言名稱、上下位、用到它的頁
  get <代號>                                 一頁的全文、原件位置、附帶檔
  data <代號> [欄名=值 ...]                   查資料頁的表格；不給條件時列出全部
  figure <代號>                              一張圖：圖檔路徑、圖上原文、說明、對應的資料頁
  trace <代號>                               往上追：依據誰，一路到原件和位置
  impact <代號>                              往下追：誰依據它、誰引用它
  point <知識點> [--wiki <主題>]              一個知識點：入口檔、每一項（編號）在四種頁的位置
  review [--wiki <主題>] [--point <知識點>]   待確認的頁，依「先確認被依據的」順序排；技能排最後
  share [public|attribution|private]        每一頁和技能可不可以公開（由原件的 share 推算）

search 的篩選：
  --type note|data|figure|code（也可以寫 筆記、資料、圖、程式碼）
  --group 原理|做法|觀點        只找筆記的某一組（也可以寫 principle、method、view）
  --point <知識點>            只找這個知識點
  --kind <種類>               例如 detail、schedule、rule、review
  --wiki <主題>               只查這個主題（可以指定專案主題）
  --all                       連專案主題一起查（預設只查通用主題）
  --deep                      關鍵字也比對全文（比較慢）
  --limit <數量>              預設 15

全部指令都可以加 --json。
代號可以寫完整的（project-demo:figure/panel-joint-001-demo-fj1-lap-joint），也可以只寫檔名，
只寫名稱時會自動找；有同名的會列出來請你選。
"""
import json
import sys

import core
from core import TYPES

GROUP_ALIASES = {"原理": "principle", "做法": "method", "觀點": "view"}
TYPE_ALIASES = {"筆記": "note", "資料": "data", "圖": "figure", "程式碼": "code", "原件": "raw", "原子": "atom",
                "文": "note", "表": "data", "碼": "code"}
STATUS_ZH = {"draft": "草稿", "reviewed": "已確認", "retired": "已停用"}


def load():
    records = core.load_records()
    return {rid: r for rid, r in records.items() if "_load_error" not in r and r.get("type") in TYPES}


def find(records, ref, rtype=None):
    """用代號或檔名找一筆紀錄。rtype 給了的話，同名時只取那一種（例如同編號的筆記和資料）。"""
    ref = ref.strip()
    if ref in records:
        return records[ref]
    if f"atom:{ref}" in records and "/" not in ref and rtype in (None, "atom"):
        return records[f"atom:{ref}"]
    if f"skill:{ref}" in records and rtype in (None, "skill"):
        return records[f"skill:{ref}"]
    matches = [r for rid, r in records.items() if rid.endswith(":" + ref) or rid.endswith("/" + ref)]
    if rtype and len(matches) > 1:
        matches = [r for r in matches if r["type"] == rtype] or matches
    if len(matches) > 1 and len({(m["wiki"], m["name"]) for m in matches}) == 1:
        # 同一項（同編號、同檔名）的幾種頁：先取筆記，其次資料、圖、程式碼，並告訴使用者還有哪些
        order = {t: i for i, t in enumerate(core.SCHEMA["pages"])}
        matches.sort(key=lambda m: order.get(m["type"], 99))
        others = "、".join(m["id"] for m in matches[1:])
        print(f"（同編號還有 {others}；要看那一頁請寫完整代號）", file=sys.stderr)
        return matches[0]
    if len(matches) == 1:
        return matches[0]
    if not matches:
        sys.exit(f"找不到「{ref}」。先用 search 找代號。")
    sys.exit("有好幾筆符合，請寫完整代號：\n" + "\n".join(f"  {m['id']}" for m in matches))


def is_project(rec, wikis):
    return wikis.get(rec.get("wiki"), {}).get("kind") == "project"


def line(rec):
    zh = TYPES[rec["type"]]["zh"]
    if rec["type"] == "note" and core.group_of_kind(rec.get("kind")):
        zh += "・" + TYPES["note"]["kind_groups"][core.group_of_kind(rec["kind"])]["zh"]
    kind = TYPES[rec["type"]]["kinds"].get(rec.get("kind"), rec.get("kind", ""))
    status = STATUS_ZH.get(rec.get("status"), rec.get("status", ""))
    return f"{rec['id']}\n    {zh}・{kind}｜{status}｜{rec.get('title', '')}\n    {rec.get('summary', '')}"


def brief(rec, records):
    sid, locator = core.raw_of(rec, records)
    af = core.attached_file(rec)
    return {"id": rec["id"], "type": rec["type"], "point": rec.get("point", ""), "item": rec.get("item", ""),
            "pair": rec.get("pair", []), "kind": rec.get("kind", ""),
            "title": rec.get("title", ""), "title_en": rec.get("title_en", ""), "summary": rec.get("summary", ""),
            "status": rec.get("status", ""), "origin": rec.get("origin", ""), "region": rec.get("region", ""),
            "raw": sid, "locator": locator, "path": rec["rel"],
            "file": af.relative_to(core.ROOT).as_posix() if af else ""}


def atom_matches(token, records):
    """關鍵字對到哪些原子（含下位原子）。完全相同的優先；沒有的話用包含。"""
    low = token.lower()
    exact, partial = set(), set()
    for rid, r in records.items():
        if r["type"] != "atom":
            continue
        names = [n.lower() for n in core.atom_names(r)]
        if low in names:
            exact.add(rid)
        elif len(low) >= 2 and any(low in n for n in names):
            partial.add(rid)
    hit = exact or partial
    out = set()
    for rid in hit:
        out |= core.descendants(rid, records)
    return out


def cmd_overview(records, args, as_json):
    path = core.ROOT / "index" / "OVERVIEW.md"
    if as_json:
        wikis = core.wikis()
        print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "path"} for k, v in wikis.items()},
                         ensure_ascii=False, indent=2))
    else:
        print(path.read_text(encoding="utf-8") if path.exists() else "還沒有索引，先執行 python scripts/wiki.py index")


def cmd_search(records, args, as_json):
    opts = {"type": None, "group": None, "point": None, "kind": None, "wiki": None, "limit": "15"}
    flags = set()
    words = []
    i = 0
    while i < len(args):
        a = args[i]
        if a.startswith("--") and a[2:] in opts:
            opts[a[2:]] = args[i + 1]
            i += 2
            continue
        if a.startswith("--"):
            flags.add(a[2:])
        else:
            words.append(a)
        i += 1
    if opts["type"]:
        opts["type"] = TYPE_ALIASES.get(opts["type"], opts["type"])
    wikis = core.wikis()
    if opts["group"]:
        opts["group"] = GROUP_ALIASES.get(opts["group"], opts["group"])
    if not words and not (opts["type"] or opts["group"] or opts["point"] or opts["kind"] or opts["wiki"]):
        sys.exit("search 後面要接關鍵字或篩選條件")
    expanded = {w: atom_matches(w, records) for w in words}
    results = []
    for rid, r in records.items():
        if r["type"] in ("atom", "raw") or r.get("status") == "retired":
            continue
        if opts["type"] and r["type"] != opts["type"]:
            continue
        if opts["group"] and (r["type"] != "note" or core.group_of_kind(r.get("kind")) != opts["group"]):
            continue
        if opts["point"] and r.get("point") != opts["point"]:
            continue
        if opts["kind"] and r.get("kind") != opts["kind"]:
            continue
        if opts["wiki"]:
            if r.get("wiki") != opts["wiki"]:
                continue
        elif "all" not in flags and is_project(r, wikis):
            continue
        rterms = {core.resolve(t, None, records) for t in r.get("atoms", [])}
        title = (r.get("title", "") + " " + r.get("title_en", "") + " " + r["name"]).lower()
        summary = r.get("summary", "").lower()
        extra = (r["sections"].get("圖上原文", "") + " " + r.get("sheet", "")).lower()
        if r["type"] == "data":
            try:
                rows = core.read_data(r)
                extra += " " + " ".join(rows[0].keys()) + " " + " ".join(str(v) for row in rows for v in row.values())
            except (OSError, IndexError):
                pass
        body = r["body"].lower() if "deep" in flags else ""
        score, ok = 0, True
        for w in words:
            lw = w.lower()
            s = 0
            if expanded[w] & rterms:
                s += 5
            elif r.get("point") and f"atom:{r['point']}" in expanded[w]:
                s += 4  # 知識點和原子同名：查原子時，這個知識點的頁都算
            if lw in title:
                s += 3
            if lw in summary:
                s += 2
            if lw in extra.lower():
                s += 1
            if body and lw in body:
                s += 1
            if s == 0:
                ok = False
                break
            score += s
        if ok:
            score += 1 if r.get("status") == "reviewed" else 0
            results.append((-score, rid, r))
    results.sort(key=lambda x: (x[0], x[1]))
    results = [r for _, _, r in results[: int(opts["limit"])]]
    if as_json:
        print(json.dumps([brief(r, records) for r in results], ensure_ascii=False, indent=2))
        return
    if not results:
        hint = "" if "all" in flags or opts["wiki"] else "（預設不查專案主題，要查請加 --all）"
        print(f"找不到{hint}。換個關鍵字、加 --deep 比對全文，或確定知識庫沒有這項內容。")
        return
    for r in results:
        print(line(r))


def cmd_atom(records, args, as_json):
    if not args:
        sys.exit("atom 後面要接名稱（中、英、日文或別名都可以）")
    hits = sorted(atom_matches(args[0], records) & {rid for rid, r in records.items() if r["type"] == "atom"})
    direct = [h for h in hits if args[0].lower() in [n.lower() for n in core.atom_names(records[h])]]
    hits = direct or hits
    if not hits:
        sys.exit("找不到這個原子")
    out = []
    for tid in hits:
        t = records[tid]
        users = [r for r in records.values() if tid in {core.resolve(x, None, records) for x in r.get("atoms", [])}]
        out.append({"id": tid, "zh": t.get("name_zh"), "en": t.get("name_en"), "ja": t.get("name_ja", ""),
                    "aliases": t.get("aliases", []), "class": t.get("kind"),
                    "definition": t["sections"].get("_lead", ""),
                    "kind_of": t.get("kind-of", []), "part_of": t.get("part-of", []),
                    "pages": [brief(u, records) for u in sorted(users, key=lambda u: u["id"])]})
    if as_json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
        return
    for o in out:
        print(f"{o['id']}｜{o['zh']}｜{o['en']}｜{o['ja']}｜別名：{'、'.join(o['aliases']) or '—'}")
        print(f"  類別：{TYPES['atom']['kinds'].get(o['class'], o['class'])}　是一種：{'、'.join(o['kind_of']) or '—'}　用於：{'、'.join(o['part_of']) or '—'}")
        print(f"  {o['definition']}")
        for u in o["pages"]:
            print(f"  - {u['id']}｜{u['title']}")


def cmd_get(records, args, as_json):
    if not args:
        sys.exit("get 後面要接代號")
    r = find(records, args[0])
    info = brief(r, records)
    info["atoms"] = r.get("atoms", [])
    info["from"] = r.get("from", [])
    info["against"] = r.get("against", [])
    info["data"] = r.get("data", [])
    info["pair"] = r.get("pair", [])
    info["sections"] = {k: v for k, v in r["sections"].items() if k != "_lead"}
    info["lead"] = r["sections"].get("_lead", "")
    if as_json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return
    print(line(r))
    print(f"  檔案：{info['path']}" + (f"　附帶檔：{info['file']}" if info["file"] else ""))
    if info["raw"]:
        print(f"  原件：{info['raw']}，{info['locator']}")
    if info["origin"] == "fileback":
        print("  這頁是查詢後回存的（fileback）。")
    if info["item"]:
        print(f"  知識點：{info['point']}　項目：{info['item']}（入口 wikis/{r['wiki']}/note/{info['point']}/NOTE.md）")
    for label, key in [("同編號", "pair"), ("原子", "atoms"), ("依據", "from"), ("反駁", "against"), ("資料", "data")]:
        if info[key]:
            print(f"  {label}：{'、'.join(info[key])}")
    if r.get("status") != "reviewed":
        print("  注意：還沒有經過擁有者確認。")
    print()
    print(r["body"].strip())


def cmd_data(records, args, as_json):
    if not args:
        sys.exit("data 後面要接代號")
    r = find(records, args[0], "data")
    if r["type"] != "data":
        sys.exit(f"{r['id']} 不是資料頁")
    rows = core.read_data(r)
    conds = {}
    for pair in args[1:]:
        if "=" not in pair:
            sys.exit(f"條件要寫成 欄名=值，收到「{pair}」")
        k, v = pair.split("=", 1)
        if rows and k not in rows[0]:
            sys.exit(f"沒有欄位「{k}」。欄位有：{'、'.join(rows[0])}")
        conds[k] = v

    def same(cell, want):
        if cell == want:
            return True
        try:
            return float(cell) == float(want)
        except ValueError:
            return False

    hits = [row for row in rows if all(same(row[k], v) for k, v in conds.items())]
    sid, locator = core.raw_of(r, records)
    if as_json:
        print(json.dumps({**brief(r, records), "columns": list(rows[0]) if rows else [], "rows": hits},
                         ensure_ascii=False, indent=2))
        return
    print(f"{r['title']}（{sid}，{locator}；{STATUS_ZH.get(r.get('status'))}；適用：{r.get('region')}）")
    if not hits:
        print("沒有符合條件的列。")
        return
    cols = list(hits[0].keys())
    print(" | ".join(cols))
    for row in hits:
        print(" | ".join(row[c] for c in cols))
    print(f"共 {len(hits)} 列。欄位的意思和單位見 {r['rel']} 的「欄位」小節。")


def cmd_figure(records, args, as_json):
    if not args:
        sys.exit("figure 後面要接代號")
    r = find(records, args[0], "figure")
    if r["type"] != "figure":
        sys.exit(f"{r['id']} 不是圖")
    info = brief(r, records)
    for key in ("sheet", "detail_no", "scale", "revision", "issue_status", "original", "region_box"):
        if r.get(key):
            info[key] = r[key]
    for name in ("圖上原文", "說明", "關鍵數據", "適用條件"):
        info[name] = r["sections"].get(name, "")
    info["data"] = [core.resolve(t, r["wiki"], records) for t in r.get("data", [])]
    if as_json:
        print(json.dumps(info, ensure_ascii=False, indent=2))
        return
    print(line(r))
    print(f"  圖檔：{info['file']}")
    for key, label in [("sheet", "圖紙"), ("detail_no", "細部編號"), ("scale", "比例"), ("revision", "版次"),
                       ("issue_status", "發行狀態")]:
        if info.get(key):
            print(f"  {label}：{info[key]}")
    for name in ("圖上原文", "說明", "關鍵數據", "適用條件"):
        print(f"\n## {name}\n{info[name]}")
    for t in info["data"]:
        if t:
            print(f"\n對應的資料頁：{t}（用 python scripts/wiki.py query data {t} 查）")


def cmd_trace(records, args, as_json):
    if not args:
        sys.exit("trace 後面要接代號")
    start = find(records, args[0])
    out, seen = [], set()

    def walk(rec, depth):
        for key in ("from", "data", "uses"):
            for ref in rec.get(key, []):
                rid = core.resolve(ref, rec["wiki"], records)
                if rid and rid not in seen:
                    seen.add(rid)
                    out.append((depth, key, records[rid]))
                    walk(records[rid], depth + 1)
        sid, locator = core.raw_of(rec, records)
        if sid:
            out.append((depth, "raw", {"id": sid, "title": records[sid].get("title", ""), "locator": locator,
                                       "type": "raw"}))

    walk(start, 1)
    if as_json:
        print(json.dumps([{"depth": d, "via": k, "id": r["id"], "title": r.get("title", ""),
                           "locator": r.get("locator", "")} for d, k, r in out], ensure_ascii=False, indent=2))
        return
    print(line(start))
    label = {"from": "依據", "data": "資料", "uses": "先用的技能", "raw": "原件"}
    for d, k, r in out:
        loc = f"，{r['locator']}" if r.get("locator") else ""
        print(f"{'  ' * d}└ {label[k]}：{r['id']} {r.get('title', '')}{loc}")


def cmd_impact(records, args, as_json):
    if not args:
        sys.exit("impact 後面要接代號")
    start = find(records, args[0])
    users = []
    for r in records.values():
        for key in ("atoms", "from", "against", "data", "see_also", "uses"):
            if start["id"] in {core.resolve(x, r.get("wiki"), records) for x in r.get(key, [])}:
                users.append((key, r))
        sid, _ = core.raw_of(r, records) if r["type"] not in ("atom", "raw") else (None, "")
        if sid == start["id"]:
            users.append(("raw", r))
        if r["type"] == "skill" and start.get("point") and start.get("wiki") and \
                f"{start['wiki']}:{start['point']}" in r.get("points", []) and ("from", r) not in users:
            users.append(("points", r))
    if as_json:
        print(json.dumps([{"via": k, **brief(r, records)} for k, r in users], ensure_ascii=False, indent=2))
        return
    print(line(start))
    for k, r in users:
        print(f"  ← {k}：{r['id']}｜{r.get('title', '')}")
    print(f"共 {len(users)} 筆")


def cmd_point(records, args, as_json):
    if not args:
        sys.exit("point 後面要接知識點名稱。全部的知識點見 index/OVERVIEW.md")
    point = args[0]
    wiki = args[args.index("--wiki") + 1] if "--wiki" in args else None
    entries = {k: v for k, v in core.entries().items() if k[1] == point and (not wiki or k[0] == wiki)}
    pages = [r for r in records.values() if r.get("point") == point and (not wiki or r.get("wiki") == wiki)]
    if not entries and not pages:
        sys.exit(f"找不到知識點「{point}」。全部的知識點見 index/OVERVIEW.md")
    items = {}
    for r in pages:
        items.setdefault(r["item"], []).append(r)
    if as_json:
        print(json.dumps({"point": point,
                          "entries": {k[0]: {"path": v["rel"], **v["meta"]} for k, v in entries.items()},
                          "items": {k: [brief(r, records) for r in sorted(v, key=lambda r: r["type"])]
                                    for k, v in sorted(items.items())}}, ensure_ascii=False, indent=2))
        return
    skills = [r for r in records.values() if r["type"] == "skill"
              and any(p.split(":", 1)[-1] == point for p in r.get("points", []))]
    for (w, _p), e in sorted(entries.items()):
        print(f"{point}（{w}）｜{e['meta'].get('title', '')}\n  {e['meta'].get('summary', '')}\n  入口：{e['rel']}")
    order = {t: i for i, t in enumerate(core.SCHEMA["pages"])}
    for item, group in sorted(items.items()):
        group.sort(key=lambda r: order[r["type"]])
        title = next((r["title"] for r in group if r["type"] in ("note", "figure")), group[0]["title"])
        print(f"\n{item}｜{title}")
        for r in group:
            print(f"  {line(r).splitlines()[1].strip()}\n    {r['id']}")
    if skills:
        print("\n用到這個知識點的技能：")
        for r in skills:
            print(f"  {r['id']}｜{r.get('title', '')}")


REVIEW_ORDER = [("raw", None), ("atom", None), ("data", None), ("figure", None), ("code", None),
                ("note", "principle"), ("note", "method"), ("note", "view"), ("skill", None)]


def review_key(r):
    return (r["type"], core.group_of_kind(r.get("kind")) if r["type"] == "note" else None)


def cmd_review(records, args, as_json):
    """待確認的頁。先列被依據的（原件、原子、資料、圖、程式碼），再列原理、做法、觀點。

    同一層裡，被越多頁依據的排越前面：先確認它，依據它的頁才站得住。
    """
    opts = {"wiki": None, "point": None, "limit": "30"}
    for i, a in enumerate(args):
        if a.startswith("--") and a[2:] in opts and i + 1 < len(args):
            opts[a[2:]] = args[i + 1]
    used = {}
    for r in records.values():
        for key in ("atoms", "from", "against", "data", "see_also", "uses"):
            for x in r.get(key, []):
                rid = core.resolve(x, r.get("wiki"), records)
                if rid:
                    used[rid] = used.get(rid, 0) + 1
        if r["type"] not in ("atom", "raw"):
            sid, _ = core.raw_of(r, records)
            if sid:
                used[sid] = used.get(sid, 0) + 1
    rank = {k: i for i, k in enumerate(REVIEW_ORDER)}
    todo = [r for r in records.values() if r.get("status") == "draft"
            and (not opts["wiki"] or r.get("wiki") == opts["wiki"])]
    if opts["wiki"]:
        todo += [records[a] for a in {core.resolve(x, None, records) for r in todo for x in r.get("atoms", [])}
                 if a and records[a].get("status") == "draft"]
    todo = list({r["id"]: r for r in todo}.values())
    if opts["point"]:
        todo = [r for r in todo if r.get("point") == opts["point"]]
    todo.sort(key=lambda r: (rank[review_key(r)], -used.get(r["id"], 0), r["id"]))
    total = len(todo)
    todo = todo[: int(opts["limit"])]
    if as_json:
        print(json.dumps([{**brief(r, records), "used_by": used.get(r["id"], 0)} for r in todo],
                         ensure_ascii=False, indent=2))
        return
    current = None
    for r in todo:
        g = review_key(r)[1]
        group = TYPES[r["type"]]["zh"] + (f"・{TYPES['note']['kind_groups'][g]['zh']}" if g else "")
        if group != current:
            current = group
            print(f"\n== {group}")
        print(f"  {r['id']}（被 {used.get(r['id'], 0)} 頁引用）｜{r.get('title', '')}")
    print(f"\n待確認共 {total} 頁，這裡列出前 {len(todo)} 頁。確認後由擁有者把 status 改成 reviewed。")


def cmd_share(records, args, as_json):
    """列出每筆紀錄推算出來的可見度。不給值時印統計和還沒標 share 的原件。"""
    colls = core.wikis()
    want = args[0] if args and args[0] in core.SCHEMA["share"] else None
    rows = [(core.share_of(r, records, colls), r) for r in records.values() if r["type"] != "atom"]
    if as_json:
        print(json.dumps([{"id": r["id"], "share": s, "type": r["type"]} for s, r in rows if not want or s == want],
                         ensure_ascii=False, indent=2))
        return
    if want:
        for s, r in sorted(rows, key=lambda x: x[1]["id"]):
            if s == want:
                print(f"{r['id']}｜{r.get('title', '')}")
        return
    for value, zh in core.SCHEMA["share"].items():
        print(f"{value}（{zh}）：{sum(1 for s, _ in rows if s == value)} 筆")
    unset = [r for _, r in rows if r["type"] == "raw" and not r.get("share")]
    if unset:
        print("\n還沒標 share 的原件（當成 private，它底下的頁也都是 private）：")
        for r in unset:
            print(f"  {r['id']}｜{r.get('title', '')}｜license：{r.get('license', '')}")


COMMANDS = {"overview": cmd_overview, "share": cmd_share, "search": cmd_search, "atom": cmd_atom, "get": cmd_get,
            "data": cmd_data, "figure": cmd_figure, "trace": cmd_trace, "impact": cmd_impact,
            "point": cmd_point, "review": cmd_review}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    as_json = "--json" in args
    args = [a for a in args if a != "--json"]
    if not args or args[0] not in COMMANDS:
        sys.exit(__doc__)
    COMMANDS[args[0]](load(), args[1:], as_json)


if __name__ == "__main__":
    main()
