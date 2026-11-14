#!/usr/bin/env python3
"""ingest：把原件登記進來，擷取文字和圖。擷取結果放在 wikis/<主題>/raw/<原件代號>/，可以隨時重新產生。

用法（通常透過 python scripts/wiki.py ingest）：
  ingest raw   <主題> <原件代號> <原件檔名> --kind <種類> --format <格式> --lang <en,zh>
      登記原件：原件放在 wikis/<主題>/raw/<原件檔名>，這個指令寫出登記卡 raw/<原件代號>.md
      （含 sha256），內容再手動補齊。種類和格式見 schema.json 的 raw。
  ingest text  <主題> <原件代號> [--pages 1-5,9] [--ocr chi_tra+eng] [--dpi 150]
      每頁文字存成 pNNN.txt。沒有文字層的頁面，加 --ocr 用文字辨識（tesseract；日文用 jpn）。
  ingest page  <主題> <原件代號> <頁> [--dpi 100]
      整頁存成 pNNN.png（不進 git），用來看版面、決定要裁切的範圍。
  ingest find  <主題> <原件代號> <頁> <正規表示式>
      找出頁面上符合的文字和座標。用來定位細部圖的標題。
  ingest crop  <主題> <原件代號> <頁> <x> <y> <寬> <高> <輸出路徑> [--dpi 150] [--ocr 語言]
      裁切一塊範圍存成 PNG，並印出範圍內的文字。座標單位是 PDF 的點（1/72 吋），原點在左上角。
      輸出路徑相對於主題資料夾，例如 figure/panel-joint/panel-joint-001-demo-fj1-lap-joint.png。

原件的檔名讀自登記卡 raw/<原件代號>.md 的 original 欄位。

需要的外部工具（raw 以外的指令）：
  - poppler（pdftotext、pdftoppm、pdfinfo）；文字辨識另外需要 tesseract 和語言包
    Windows：可以用 scoop install poppler tesseract，或 conda 安裝
  - 這個 repo 的其他腳本都不需要這些工具
"""
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import core


def need(*tools):
    missing = [t for t in tools if not shutil.which(t)]
    if missing:
        sys.exit(f"需要外部工具：{'、'.join(missing)}。安裝方式見本檔開頭的說明。")


def source_pdf(wiki, source):
    base = core.ROOT / "wikis" / wiki
    card = base / "raw" / f"{source}.md"
    if not card.exists():
        sys.exit(f"找不到登記卡 {card.relative_to(core.ROOT)}。先用 ingest raw 登記原件。")
    fm, _ = core.parse_frontmatter(card.read_text(encoding="utf-8"))
    if not fm or not fm.get("original"):
        sys.exit("登記卡沒有填 original")
    pdf = base / "raw" / fm["original"]
    if not pdf.exists():
        sys.exit(f"找不到原件 {pdf.relative_to(core.ROOT)}。原件不進 git，請把檔案放到這個位置。")
    out = base / "raw" / source
    out.mkdir(parents=True, exist_ok=True)
    return base, pdf, out


def cmd_raw(args):
    if len(args) < 3:
        sys.exit(__doc__)
    wiki, source, original = args[:3]
    spec = core.TYPES["raw"]
    kind, fmt = option(args, "--kind", "book"), option(args, "--format", "pdf-text")
    langs = option(args, "--lang", "en")
    if kind not in spec["kinds"] or fmt not in spec["formats"]:
        sys.exit(f"--kind 應為 {'、'.join(spec['kinds'])}；--format 應為 {'、'.join(spec['formats'])}")
    base = core.ROOT / "wikis" / wiki
    if not base.exists():
        sys.exit(f"沒有主題 {wiki}。先建立 wikis/{wiki}/WIKI.md")
    card = base / "raw" / f"{source}.md"
    if card.exists():
        sys.exit(f"{card.relative_to(core.ROOT)} 已經存在")
    path = base / "raw" / original
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else ""
    card.parent.mkdir(parents=True, exist_ok=True)
    card.write_text(f"""---
title: {source}
title_en: ""
type: raw
kind: {kind}
format: {fmt}
lang: [{langs}]
region: any
summary: 一句話說明這份原件（待補）
original: "{original}"
sha256: {digest}
license: 待補
share: private
status: draft
origin: ingest
updated: {datetime.date.today().isoformat()}
---

出版資訊、頁數、取得日期（待補）。

## 可信度

- 待補

## 閱讀進度

| 範圍 | 狀態 | 產出 |
|---|---|---|
| 全部 | 未讀 | — |

## 已知問題

- 目前沒有。
""", encoding="utf-8")
    print(f"已寫出 {card.relative_to(core.ROOT)}" + ("" if digest else "（原件還不在這裡，sha256 之後再補）"))


def page_count(pdf):
    info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True, check=True).stdout
    return int(re.search(r"Pages:\s+(\d+)", info).group(1))


def parse_pages(spec, total):
    if not spec:
        return list(range(1, total + 1))
    pages = set()
    for part in spec.split(","):
        a, _, b = part.partition("-")
        pages.update(range(int(a), int(b or a) + 1))
    return sorted(p for p in pages if 1 <= p <= total)


def option(args, name, default=None):
    if name in args:
        i = args.index(name)
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def ocr(png, lang):
    need("tesseract")
    result = subprocess.run(["tesseract", str(png), "-", "-l", lang, "--psm", "4"],
                            capture_output=True, text=True)
    return result.stdout


def render(pdf, page, dpi, target, box=None):
    """把一頁（或一塊範圍）存成 PNG。box 是 (x, y, w, h)，單位是點。"""
    cmd = ["pdftoppm", "-png", "-r", str(dpi), "-f", str(page), "-l", str(page), "-singlefile"]
    if box:
        scale = dpi / 72
        x, y, w, h = (round(v * scale) for v in box)
        cmd += ["-x", str(x), "-y", str(y), "-W", str(w), "-H", str(h)]
    stem = str(target)[:-4] if str(target).endswith(".png") else str(target)
    subprocess.run(cmd + [str(pdf), stem], check=True)
    return Path(stem + ".png")


def cmd_text(args):
    need("pdftotext", "pdfinfo")
    lang = option(args, "--ocr")
    dpi = int(option(args, "--dpi", "150"))
    spec = option(args, "--pages")
    wiki, source = args[:2]
    coll, pdf, out = source_pdf(wiki, source)
    pages = parse_pages(spec, page_count(pdf))
    done_ocr = 0
    for p in pages:
        text = subprocess.run(["pdftotext", "-layout", "-f", str(p), "-l", str(p), str(pdf), "-"],
                              capture_output=True, text=True).stdout
        header = ""
        if len(text.strip()) < 20 and lang:
            with tempfile.TemporaryDirectory() as tmp:
                png = render(pdf, p, dpi, Path(tmp) / "page.png")
                text = ocr(png, lang)
            header = f"〔文字辨識 {lang}，未校對〕\n"
            done_ocr += 1
        (out / f"p{p:03d}.txt").write_text(header + text, encoding="utf-8")
    print(f"已擷取 {len(pages)} 頁到 {out.relative_to(core.ROOT)}，其中 {done_ocr} 頁用文字辨識")


def cmd_page(args):
    need("pdftoppm")
    dpi = int(option(args, "--dpi", "100"))
    wiki, source, page = args[:3]
    coll, pdf, out = source_pdf(wiki, source)
    png = render(pdf, int(page), dpi, out / f"p{int(page):03d}.png")
    print(png.relative_to(core.ROOT))


def cmd_find(args):
    need("pdftotext")
    wiki, source, page, pattern = args[:4]
    coll, pdf, out = source_pdf(wiki, source)
    html = subprocess.run(["pdftotext", "-bbox", "-f", page, "-l", page, str(pdf), "-"],
                          capture_output=True, text=True, check=True).stdout
    words = re.findall(r'<word xMin="([\d.]+)" yMin="([\d.]+)" xMax="([\d.]+)" yMax="([\d.]+)">([^<]*)</word>', html)
    rx = re.compile(pattern)
    for x0, y0, x1, y1, w in words:
        if rx.search(w):
            print(f"x={float(x0):8.1f} y={float(y0):8.1f}  {w}")


def cmd_crop(args):
    need("pdftoppm", "pdftotext")
    dpi = int(option(args, "--dpi", "150"))
    lang = option(args, "--ocr")
    wiki, source, page = args[:3]
    x, y, w, h = (float(v) for v in args[3:7])
    target = args[7]
    coll, pdf, out = source_pdf(wiki, source)
    dest = coll / target
    dest.parent.mkdir(parents=True, exist_ok=True)
    png = render(pdf, int(page), dpi, dest, (x, y, w, h))
    text = subprocess.run(["pdftotext", "-layout", "-f", page, "-l", page, "-x", str(int(x)), "-y", str(int(y)),
                           "-W", str(int(w)), "-H", str(int(h)), str(pdf), "-"],
                          capture_output=True, text=True).stdout
    if len(text.strip()) < 5 and lang:
        text = "〔文字辨識，未校對〕\n" + ocr(png, lang)
    print(f"# 圖檔：{png.relative_to(core.ROOT)}")
    print(f"# region_box: \"p{page}, x{int(x)} y{int(y)} w{int(w)} h{int(h)}\"")
    print(text.rstrip())


COMMANDS = {"raw": cmd_raw, "text": cmd_text, "page": cmd_page, "find": cmd_find, "crop": cmd_crop}


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] not in COMMANDS:
        sys.exit(__doc__)
    COMMANDS[args[0]](args[1:])


if __name__ == "__main__":
    main()
