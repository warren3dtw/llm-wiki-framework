#!/usr/bin/env python3
"""lint：檢查全部的頁。規則讀自 schema.json。只用標準庫。

用法（通常透過 python scripts/wiki.py lint）：
  python scripts/lint.py              檢查格式、連結、索引
  python scripts/lint.py -q           只印錯誤和統計

錯誤要修正，程式以代碼 1 結束。警告是提醒，不影響結束代碼。
"""
import csv
import re
import sys
from collections import Counter, defaultdict

import build_index
import core
from core import CODE_FENCE, LINK_RE, SCHEMA, TYPES

NUMBER_UNIT = re.compile(r"(?<![\w.])\d+(?:[.,]\d+)?\s?(?:mm|cm|m|kN|kPa|MPa|GPa|N|kg|kgf|°|%)(?![A-Za-z])")
FORMULA_SECTIONS = {"公式", "符號", "程式", "核對", "圖上原文", "推導", "步驟"}


def check(records, errors, warnings):
    colls = core.wikis()
    cited_sources, used_terms, used_records = set(), set(), set()

    for rid, rec in records.items():
        where = rec["rel"]
        if "_load_error" in rec:
            errors.append(f"{where}：{rec['_load_error']}")
            continue
        t = rec.get("type")
        if t not in TYPES:
            errors.append(f"{where}：type「{t}」不在 schema.json 裡")
            continue
        spec = TYPES[t]
        if rec["folder"] != spec["folder"]:
            errors.append(f"{where}：{t} 應該放在 {spec['folder']}/")
        if rec.get("_duplicate"):
            errors.append(f"{where}：代號 {rid} 和 {rec['_duplicate']} 重複（不同知識點資料夾也不能同名）")
        if t in SCHEMA["pages"]:
            check_point(rec, errors, where)
        if t not in SCHEMA["pages"] and not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", rec["name"]):
            errors.append(f"{where}：檔名只能用小寫英數和連字號")

        required = SCHEMA["common_required"] + spec.get("required", [])
        required += spec.get("required_by_kind", {}).get(rec.get("kind"), [])
        if rec.get("origin") == "fileback":
            required = [k for k in required if k != "raw"] + ["from"]
        if rec.get("origin") and rec["origin"] not in SCHEMA["origin"]:
            errors.append(f"{where}：origin 應為 {'、'.join(SCHEMA['origin'])}")
        for key in required:
            if not rec.get(key):
                errors.append(f"{where}：缺少欄位 {key}")
        if rec.get("kind") and rec["kind"] not in spec["kinds"]:
            errors.append(f"{where}：kind「{rec['kind']}」不合法，應為 {'、'.join(spec['kinds'])}")
        if rec.get("status") and rec["status"] not in SCHEMA["status"]:
            errors.append(f"{where}：status 應為 {'、'.join(SCHEMA['status'])}")
        if rec.get("region") and rec["region"] not in SCHEMA["region"]:
            errors.append(f"{where}：region「{rec['region']}」不合法，應為 {'、'.join(SCHEMA['region'])}")
        for lang in rec.get("lang", []):
            if lang not in SCHEMA["lang"]:
                errors.append(f"{where}：lang「{lang}」不合法")
        if len(rec.get("summary", "")) > SCHEMA["summary_max_chars"]:
            errors.append(f"{where}：summary 超過 {SCHEMA['summary_max_chars']} 字")
        for key in ("updated", "checked"):
            if rec.get(key) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", rec[key]):
                errors.append(f"{where}：{key} 要寫成 YYYY-MM-DD")

        needed = list(spec.get("sections", [])) + spec.get("sections_by_kind", {}).get(rec.get("kind"), [])
        for name in needed:
            if not rec["sections"].get(name):
                errors.append(f"{where}：缺少小節「## {name}」，或小節是空的")

        if spec.get("max_body_chars"):
            prose = LINK_RE.sub(lambda m: m.group(1), CODE_FENCE.sub("", rec["body"]))
            prose = "\n".join(l for l in prose.splitlines() if not l.lstrip().startswith("|"))
            if len(prose) > spec["max_body_chars"]:
                warnings["內文太長"].append(f"{where}（{len(prose)} 字，建議拆開）")

        if t == "raw":
            if rec.get("format") not in spec["formats"]:
                errors.append(f"{where}：format 應為 {'、'.join(spec['formats'])}")
            if rec.get("original"):
                original = rec["path"].parent / rec["original"]
                if not original.exists() and not rec.get("sha256"):
                    warnings["原件不在本機"].append(f"{where}（{rec['original']}；沒有 sha256，無法確認是同一份）")
        if t == "skill":
            check_skill(rec, records, colls, errors, warnings, where)
        if rec.get("share") and rec["share"] not in SCHEMA["share"]:
            errors.append(f"{where}：share 應為 {'、'.join(SCHEMA['share'])}")
        elif rec.get("share") and t != "raw":
            base = core.computed_share(rec, records, colls)
            if core.stricter(base, rec["share"]) != rec["share"]:
                errors.append(f"{where}：share 標成 {rec['share']}，但依據的原件或頁推算只能是 {base}（只能標得更嚴格）")
        if t == "raw" and not rec.get("share"):
            warnings["原件沒有標 share（當成 private）"].append(where)
        if t == "code" and rec.get("verified") not in spec["verified"]:
            errors.append(f"{where}：verified 應為 {'、'.join(spec['verified'])}")

        df = core.attached_file(rec)
        if t in ("data", "figure", "code"):
            if df is None or not df.exists():
                errors.append(f"{where}：找不到資料檔 {df.name if df else '（沒有填）'}")
            elif t == "figure" and df.suffix.lower() not in spec["image_ext"]:
                errors.append(f"{where}：圖要用通用格式（{'、'.join(spec['image_ext'])}），原始檔填在 original")
            elif t == "code" and df.suffix == ".md":
                errors.append(f"{where}：程式檔不能是 .md，提示詞用 .txt")
        if t == "figure" and rec.get("original"):
            if not (rec["path"].parent / rec["original"]).exists():
                warnings["原始檔不在本機"].append(f"{where}（{rec['original']}）")
        if t == "data" and df and df.exists():
            check_table(rec, errors, where)

        for field, allowed in SCHEMA["links"].items():
            for ref in rec.get(field, []):
                target = core.resolve(ref, rec.get("wiki"), records)
                if target is None:
                    errors.append(f"{where}：{field} 指向不存在的「{ref}」")
                    continue
                if records[target].get("type") not in allowed:
                    errors.append(f"{where}：{field} 不能指向 {records[target].get('type')}（{ref}）")
                    continue
                if target == rid:
                    errors.append(f"{where}：{field} 不能指向自己")
                tcoll = records[target].get("wiki")
                if field != "atoms" and tcoll and tcoll != rec.get("wiki"):
                    mine = colls.get(rec.get("wiki"), {}).get("kind")
                    theirs = colls.get(tcoll, {}).get("kind")
                    if mine == "general" and theirs == "project":
                        errors.append(f"{where}：通用主題不能引用專案主題（{ref}）")
                if field == "atoms":
                    used_terms.add(target)
                else:
                    used_records.add(target)
                if records[target].get("status") == "retired" and rec.get("status") != "retired":
                    warnings["引用了已停用的紀錄"].append(f"{where} → {target}")
        for key in ("kind-of", "part-of"):
            for ref in rec.get(key, []):
                target = core.resolve(ref, None, records)
                if target is None or records[target].get("type") != "atom":
                    errors.append(f"{where}：{key} 指向不存在的原子「{ref}」")
                else:
                    used_terms.add(target)

        if t not in ("raw", "atom"):
            sid, locator = core.raw_of(rec, records)
            if rec.get("raw") and sid is None:
                errors.append(f"{where}：raw 的原件代號不存在：「{rec['raw'].split(',')[0]}」")
            elif sid:
                cited_sources.add(sid)
                if colls.get(records[sid].get("wiki"), {}).get("kind") == "project" and \
                        (t == "skill" or colls.get(rec.get("wiki"), {}).get("kind") == "general"):
                    errors.append(f"{where}：通用主題和技能本體的 raw 不能是專案主題的原件（{sid}）")
                if not locator and records[sid].get("kind") not in ("experience",):
                    warnings["原件沒有寫位置"].append(where)

        mine_general = colls.get(rec.get("wiki"), {}).get("kind") == "general" or t == "skill"
        for target in link_targets(rec):
            dest = rec["path"].parent / target
            if not dest.exists():
                errors.append(f"{where}：內文連結不存在 {target}")
            elif mine_general:
                parts = dest.resolve().relative_to(core.ROOT).parts if dest.resolve().is_relative_to(core.ROOT) else ()
                if len(parts) > 1 and parts[0] == "wikis" and colls.get(parts[1], {}).get("kind") == "project":
                    errors.append(f"{where}：內文連到專案主題（{target}）；通用主題和技能本體不能引用專案主題")
        if t in SCHEMA["pages"]:
            seen = max(rec.get("updated", ""), rec.get("checked", ""))
            for key in ("from", "data"):
                for ref in rec.get(key, []):
                    target = core.resolve(ref, rec.get("wiki"), records)
                    if target and records[target].get("updated", "") > seen:
                        warnings["依據已更新，要重看"].append(
                            f"{where}（{target} 在 {records[target]['updated']} 改過；重看後不必改就填 checked）")

        if t == "note":
            loose = []
            for name, content in rec["sections"].items():
                if name in FORMULA_SECTIONS:
                    continue
                prose = CODE_FENCE.sub("", content)
                prose = re.sub(r"`[^`]*`", "", prose)
                prose = "\n".join(l for l in prose.splitlines() if not l.lstrip().startswith("|"))
                loose += NUMBER_UNIT.findall(prose)
            if loose and not rec.get("data") and "data/" not in rec["body"]:
                warnings["筆記裡有數據但沒有連到資料頁"].append(f"{where}（{'、'.join(loose[:4])}）")

    for rid, rec in records.items():
        if rec.get("status") == "retired":
            continue
        if rec.get("type") == "atom" and rid not in used_terms:
            warnings["沒有頁用到的原子"].append(rid)
        if rec.get("type") == "raw" and rid not in cited_sources:
            warnings["沒有頁引用的原件"].append(rid)


def check_skill(rec, records, colls, errors, warnings, where):
    """技能：skills/<代號>/SKILL.md。本體不能引用專案主題，專案的東西放 profiles/<專案主題>/。"""
    spec = TYPES["skill"]
    folder = rec["path"].parent
    if rec.get("declared_name") and rec["declared_name"] != rec["name"]:
        errors.append(f"{where}：name「{rec['declared_name']}」要和資料夾名稱 {rec['name']} 相同")
    if not re.fullmatch(r"[a-z][a-z0-9]*-\d{3}", rec["name"]):
        errors.append(f"{where}：技能代號要寫成「前綴-三位數」，例如 rhino-002")
    if rec.get("version") and not re.fullmatch(r"\d+\.\d+\.\d+", rec["version"]):
        errors.append(f"{where}：version 要寫成 主版本.次版本.修正，例如 0.1.0")
    if len(rec.get("description", "")) > spec["description_max_chars"]:
        errors.append(f"{where}：description 超過 {spec['description_max_chars']} 字")
    n_lines = rec["body"].count("\n") + 1
    if n_lines > spec["max_lines"]:
        warnings["SKILL.md 太長"].append(f"{where}（{n_lines} 行，建議 {spec['max_lines']} 行以內；細節搬到 references/）")
    if (folder / "incoming").is_dir() and any((folder / "incoming").iterdir()):
        warnings["技能有還沒併入的改動"].append(f"{where}（incoming/ 裡有從工作專案帶回來的差異）")
    for key in ("from", "uses"):
        for ref in rec.get(key, []):
            target = core.resolve(ref, None, records)
            if target and colls.get(records[target].get("wiki"), {}).get("kind") == "project":
                errors.append(f"{where}：技能本體不能引用專案主題（{ref}），專案的內容放 profiles/<專案主題>/")
    for ref in rec.get("points", []):
        wiki, _, point = ref.partition(":")
        if not point or (wiki, point) not in core.entries():
            errors.append(f"{where}：points 的「{ref}」不存在（寫成 主題:知識點）")
        elif colls.get(wiki, {}).get("kind") == "project":
            errors.append(f"{where}：技能本體不能引用專案主題的知識點（{ref}），放 profiles/<專案主題>/")
    files = spec["files"]
    if not (folder / files["tests"]).exists():
        warnings["技能沒有驗收題"].append(f"{where}（{files['tests']}）")
    if not (folder / files["changelog"]).exists():
        warnings["技能沒有版本紀錄"].append(f"{where}（{files['changelog']}）")
    for doc in sorted(folder.rglob("*.md")):
        rel = doc.relative_to(folder)
        if doc.name == spec["entry"] and len(rel.parts) == 1 or rel.parts[0] in ("tests", "incoming"):
            continue
        for target in link_targets({"body": doc.read_text(encoding="utf-8", errors="ignore")}):
            if target and not (doc.parent / target).exists():
                errors.append(f"{where}：{rel.as_posix()} 的連結不存在 {target}")
    profiles = folder / files["profiles"]
    if profiles.is_dir():
        for p in sorted(x for x in profiles.iterdir() if x.is_dir()):
            if p.name not in colls:
                errors.append(f"{where}：{files['profiles']}/{p.name} 不是既有的主題")
            elif colls[p.name].get("kind") != "project":
                warnings["profile 對應的不是專案主題"].append(f"{where}（{p.name}）")
        if not (folder / files["profile_example"]).is_dir():
            warnings["有 profile 卻沒有公開用的示範"].append(f"{where}（缺 {files['profile_example']}/）")
    seen = max(rec.get("updated", ""), rec.get("checked", ""))
    for ref in rec.get("from", []):
        target = core.resolve(ref, None, records)
        if target and records[target].get("updated", "") > seen:
            warnings["技能的依據已更新"].append(f"{where}（{target} 在 {records[target]['updated']} 改過）")


def link_targets(rec):
    body = CODE_FENCE.sub("", rec["body"])
    for _, target in LINK_RE.findall(body):
        if re.match(r"^[a-z][a-z0-9+.-]*:", target) or target.startswith("#"):
            continue
        yield target.split("#")[0]


def check_table(rec, errors, where):
    rows_path = rec["path"].with_suffix(".csv")
    with rows_path.open(encoding="utf-8", newline="") as f:
        reader = list(csv.reader(f))
    if not reader:
        errors.append(f"{where}：CSV 是空的")
        return
    header = reader[0]
    for name in header:
        if not re.fullmatch(r"[a-z][a-z0-9_]*", name):
            errors.append(f"{where}：欄名「{name}」只能用英文小寫、數字和底線")
        if f"`{name}`" not in rec["sections"].get("欄位", ""):
            errors.append(f"{where}：欄位「{name}」沒有在「## 欄位」小節說明")
    if len(set(header)) != len(header):
        errors.append(f"{where}：欄名重複")
    for n, row in enumerate(reader[1:], start=2):
        if len(row) != len(header):
            errors.append(f"{where}：CSV 第 {n} 列有 {len(row)} 欄，應該是 {len(header)} 欄")
    if len(reader) < 2:
        errors.append(f"{where}：CSV 沒有資料列")


def check_point(rec, errors, where):
    """頁的位置、檔名、point、item 要一致：<類型>/<知識點>/<知識點>-<編號>-<描述>.md。"""
    parts = core.split_item(rec["name"])
    folder = rec.get("point_folder")
    if not folder:
        errors.append(f"{where}：頁要放在 {rec['folder']}/<知識點>/ 底下")
        return
    if parts is None or parts[0] != folder:
        errors.append(f"{where}：檔名要寫成 {folder}-<{SCHEMA['point']['digits']} 位數編號>-<描述>")
        return
    item = f"{parts[0]}-{parts[1]:0{SCHEMA['point']['digits']}d}"
    if rec.get("point") and rec["point"] != folder:
        errors.append(f"{where}：point 是「{rec['point']}」，但放在 {folder}/ 資料夾")
    if rec.get("item") and rec["item"] != item:
        errors.append(f"{where}：item 是「{rec['item']}」，和檔名的 {item} 不同")


def check_items(records, errors):
    """同編號的頁：全部主題共用一套編號，四種頁之間檔名相同，pair 互相列出。"""
    by_item = defaultdict(list)
    for r in records.values():
        if r.get("type") in SCHEMA["pages"] and r.get("item"):
            by_item[r["item"]].append(r)
    for item, group in by_item.items():
        wikis = {r["wiki"] for r in group}
        if len(wikis) > 1:
            errors.append(f"編號 {item} 同時用在 {'、'.join(sorted(wikis))}：編號全部主題共用一套，請改用下一個編號")
        types = [r["type"] for r in group]
        for t in set(types):
            if types.count(t) > 1:
                errors.append(f"編號 {item} 在 {t} 有 {types.count(t)} 頁：同一種頁裡一個編號只能有一頁")
        names = {r["name"] for r in group}
        if len(names) > 1:
            errors.append(f"編號 {item} 的檔名不一致（{'、'.join(sorted(names))}）：同一項的描述要寫得一模一樣")
        for r in group:
            want = {o["id"] for o in group if o is not r}
            have = {core.resolve(x, r.get("wiki"), records) for x in r.get("pair", [])}
            if want != have:
                missing = sorted(want - have)
                extra = sorted(x or "?" for x in have - want)
                msg = (f"少了 {'、'.join(missing)}" if missing else "") + (f" 多了 {'、'.join(extra)}" if extra else "")
                errors.append(f"{r['rel']}：pair 要列出同編號的其他頁，{msg.strip()}")


def check_entries(records, errors, warnings):
    """每個知識點在每個主題都要有 note/<知識點>/NOTE.md，列出這個知識點的全部頁，連結都點得到。"""
    entries = core.entries()
    pages = defaultdict(list)
    for r in records.values():
        if r.get("type") in SCHEMA["pages"] and r.get("point_folder"):
            pages[(r["wiki"], r["point_folder"])].append(r)
    for key, group in pages.items():
        if key not in entries:
            errors.append(f"wikis/{key[0]}/note/{key[1]}/{core.ENTRY} 不存在：每個知識點都要有入口檔")
            continue
        entry = entries[key]
        linked = set()
        for target in link_targets({"body": entry["body"]}):
            path = (entry["path"].parent / target).resolve()
            if not path.exists():
                errors.append(f"{entry['rel']}：連結 {target} 不存在")
            linked.add(path)
        for r in group:
            if r["path"].resolve() not in linked:
                errors.append(f"{entry['rel']}：沒有列出 {r['rel']}")
    for key, entry in entries.items():
        for field in SCHEMA["point"]["entry_required"]:
            if not entry["meta"].get(field):
                errors.append(f"{entry['rel']}：缺少欄位 {field}")
        if entry["meta"].get("point") and entry["meta"]["point"] != key[1]:
            errors.append(f"{entry['rel']}：point 是「{entry['meta']['point']}」，但資料夾是 {key[1]}")
        if key not in pages:
            warnings["知識點沒有任何頁"].append(entry["rel"])


def check_wiki_pages(errors):
    """主題說明（WIKI.md）不是頁，但裡面的連結也要能點。"""
    for meta in core.wikis().values():
        path = meta["path"] / "WIKI.md"
        if path.exists():
            for target in link_targets({"body": path.read_text(encoding="utf-8")}):
                if target and not (path.parent / target).exists():
                    errors.append(f"{path.relative_to(core.ROOT).as_posix()}：連結 {target} 不存在")


def main():
    quiet = "-q" in sys.argv
    records = core.load_records()
    errors, warnings = [], defaultdict(list)
    check(records, errors, warnings)
    check_items(records, errors)
    check_entries(records, errors, warnings)
    check_wiki_pages(errors)
    for name, text in build_index.make_index(records).items():
        path = core.ROOT / "index" / name
        if not path.exists() or path.read_text(encoding="utf-8") != text:
            errors.append(f"index/{name} 不是最新的，請執行 python scripts/wiki.py index")
    counts = Counter((r.get("wiki") or "（共用）", r.get("type")) for r in records.values())
    for coll in sorted({c for c, _ in counts}):
        parts = [f"{TYPES[t]['zh']} {counts[(coll, t)]}" for t in TYPES if counts[(coll, t)]]
        print(f"== {coll}：{'、'.join(parts)}")
    for e in errors:
        print(f"  錯誤：{e}")
    if not quiet:
        for name, items in warnings.items():
            print(f"  {name}（{len(items)}）")
            for item in items[:12]:
                print(f"    - {item}")
            if len(items) > 12:
                print(f"    …還有 {len(items) - 12} 項")
    print(f"共 {len(records)} 頁（含原子、原件），{len(errors)} 個錯誤，{sum(len(v) for v in warnings.values())} 個警告")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
