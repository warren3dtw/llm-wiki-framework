"""export：把知識庫輸出成可以單獨開啟的 HTML 檔，放在 build/。

    python scripts/wiki.py export atlas [--wiki 主題] [--kind detail]   細部圖集
    python scripts/wiki.py export datasheet [--wiki 主題] [--kind 種類]  數據手冊

圖集：每張圖一節，含圖片（內嵌，不需要另外的檔案）、說明、關鍵數據、適用條件，
以及這張圖連到的資料頁。數據手冊：資料頁依主題和種類分組，每張表附欄位說明和原件位置。
輸出只用 Python 標準庫；HTML 可以直接用瀏覽器開，或另存成 PDF。
"""
import argparse
import base64
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from core import ROOT, load_records, read_data, resolve, raw_of, attached_file  # noqa: E402

MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".svg": "image/svg+xml"}
STYLE = """
body{font-family:"Noto Sans TC","Microsoft JhengHei",sans-serif;max-width:1000px;margin:2em auto;padding:0 1em;color:#222;line-height:1.6}
h1{border-bottom:2px solid #333}h2{margin-top:2.5em;border-bottom:2px solid #555;page-break-before:always}h3{margin-top:2em;border-bottom:1px solid #aaa}
h2:first-of-type{page-break-before:auto}
table{border-collapse:collapse;margin:.8em 0;font-size:.9em}th,td{border:1px solid #999;padding:3px 8px;text-align:left;vertical-align:top}
th{background:#eee}img{max-width:100%;border:1px solid #ccc}.meta{color:#666;font-size:.85em}
.draft{color:#a60}nav a{display:inline-block;margin-right:1em}
"""


def esc(s):
    return html.escape(str(s))


def inline(s):
    s = esc(s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    return re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)  # 連結只留文字，檔案是單獨開的


def md(text):
    """很小的 Markdown 轉換：段落、清單、管線表格、標題。"""
    out, lines, i = [], text.strip().splitlines(), 0
    while i < len(lines):
        line = lines[i].rstrip()
        if line.startswith("|"):
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.fullmatch(r":?-+:?", c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append(table_html(rows[0], rows[1:]))
            continue
        if re.match(r"^\s*([-*]|\d+\.)\s", line):
            items = []
            while i < len(lines) and re.match(r"^\s*([-*]|\d+\.)\s", lines[i]):
                items.append(re.sub(r"^\s*([-*]|\d+\.)\s", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline(x)}</li>" for x in items) + "</ul>")
            continue
        if line.startswith("```"):
            i += 1
            block = []
            while i < len(lines) and not lines[i].startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            out.append(f"<pre>{esc(chr(10).join(block))}</pre>")
            continue
        if line.startswith("#"):
            out.append(f"<h4>{inline(line.lstrip('#').strip())}</h4>")
        elif line and not line.startswith("!["):
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    return "\n".join(out)


def table_html(header, rows):
    head = "".join(f"<th>{inline(h)}</th>" for h in header)
    body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><tr>{head}</tr>{body}</table>"


def csv_html(rec):
    rows = read_data(rec)
    if not rows:
        return "<p>（表格是空的）</p>"
    header = list(rows[0].keys())
    return table_html(header, [[r[h] for h in header] for r in rows])


def meta_line(rec, records):
    sid, loc = raw_of(rec, records)
    src = records[sid]["title"] if sid else rec.get("raw", "")
    status = rec.get("status", "")
    flag = "" if status == "reviewed" else f' <span class="draft">〔{esc(status)}，未經擁有者確認〕</span>'
    return f'<p class="meta">{esc(rec["id"])}｜來源：{esc(src)} {esc(loc)}{flag}</p>'


def pick(records, rtype, args):
    out = []
    for rec in records.values():
        if rec.get("type") != rtype or rec.get("status") == "retired":
            continue
        if args.wiki and rec["wiki"] != args.wiki:
            continue
        if args.kind and rec.get("kind") != args.kind:
            continue
        out.append(rec)
    return sorted(out, key=lambda r: r["id"])


def page(title, parts, nav):
    links = "".join(f'<a href="#{esc(a)}">{esc(t)}</a>' for a, t in nav)
    return (f'<!DOCTYPE html><html lang="zh-Hant"><head><meta charset="utf-8"><title>{esc(title)}</title>'
            f"<style>{STYLE}</style></head><body><h1>{esc(title)}</h1><nav>{links}</nav>"
            + "\n".join(parts) + "</body></html>")


def anchor(rec):
    return re.sub(r"[^a-z0-9]+", "-", rec["id"].lower())


def atlas(records, args):
    """細部圖集：依知識點分章，每章開頭是入口檔的標題和摘要，每張圖一節。"""
    from core import entries
    figs = sorted(pick(records, "figure", args), key=lambda r: (r["wiki"], r.get("point", ""), r["id"]))
    ents = entries()
    parts, nav, current = [], [], None
    for rec in figs:
        key = (rec["wiki"], rec.get("point", ""))
        if key != current:
            current = key
            meta = ents.get(key, {}).get("meta", {})
            gid = re.sub(r"[^a-z0-9]+", "-", f"{key[0]}-{key[1]}")
            parts.append(f'<h2 id="{gid}">{esc(meta.get("title", key[1]))}</h2>'
                         f'<p class="meta">知識點 {esc(key[1])}｜{esc(key[0])}</p><p>{esc(meta.get("summary", ""))}</p>')
            nav.append((gid, meta.get("title", key[1])))
        img = attached_file(rec)
        uri = ""
        if img and img.exists():
            uri = f"data:{MIME[img.suffix.lower()]};base64," + base64.b64encode(img.read_bytes()).decode()
        secs = rec["sections"]
        part = [f'<h3 id="{anchor(rec)}">{esc(rec.get("item", ""))}　{esc(rec["title"])}</h3>', meta_line(rec, records),
                f"<p>{esc(rec.get('summary', ''))}</p>"]
        part.append(f'<img src="{uri}" alt="{esc(rec["title"])}">' if uri
                    else "<p>〔圖檔不在 repo 裡，請用 wiki.py ingest crop 從原件重新裁切〕</p>")
        for name in ("說明", "關鍵數據", "適用條件"):
            if secs.get(name):
                part.append(f"<h4>{name}</h4>" + md(secs[name]))
        for ref in rec.get("data", []):
            tid = resolve(ref, rec["wiki"], records)
            if tid:
                part.append(f"<h4>{esc(records[tid]['title'])}</h4>" + csv_html(records[tid]))
        parts.append("\n".join(part))
    return "細部圖集", parts, nav, len(figs)


def datasheet(records, args):
    tabs = pick(records, "data", args)
    parts, nav, current = [], [], None
    for rec in sorted(tabs, key=lambda r: (r["wiki"], r.get("kind", ""), r["id"])):
        group = f'{rec["wiki"]}／{rec.get("kind", "")}'
        if group != current:
            current = group
            gid = re.sub(r"[^a-z0-9]+", "-", group.lower()) or "g"
            parts.append(f'<h2 id="{gid}">{esc(group)}</h2>')
            nav.append((gid, group))
        secs = rec["sections"]
        parts.append(f'<h3 id="{anchor(rec)}">{esc(rec["title"])}</h3>' + meta_line(rec, records)
                     + f"<p>{esc(rec.get('summary', ''))}</p>" + csv_html(rec)
                     + ("<h4>欄位</h4>" + md(secs["欄位"]) if secs.get("欄位") else ""))
    return "數據手冊", parts, nav, len(tabs)


def main(argv=None):
    ap = argparse.ArgumentParser(description="輸出細部圖集或數據手冊")
    ap.add_argument("what", choices=["atlas", "datasheet"])
    ap.add_argument("--wiki")
    ap.add_argument("--kind")
    ap.add_argument("--out", help="輸出檔名，預設 build/<what>[-集合].html")
    args = ap.parse_args(argv)
    records = load_records()
    title, parts, nav, n = (atlas if args.what == "atlas" else datasheet)(records, args)
    if args.wiki:
        title += f"：{args.wiki}"
    out = Path(args.out) if args.out else ROOT / "build" / (
        args.what + (f"-{args.wiki}" if args.wiki else "") + ".html")
    out.parent.mkdir(exist_ok=True)
    out.write_text(page(title, parts, nav), encoding="utf-8")
    print(f"{title}：{n} 筆，寫到 {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out}")


if __name__ == "__main__":
    main()
