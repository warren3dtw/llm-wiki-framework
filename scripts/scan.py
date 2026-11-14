"""輸出前的掃描：找出不該出現在公開輸出裡的東西。只用標準庫。

檢查四種：
  禁用字    根目錄的 denylist.txt 管全部的公開輸出；技能 profiles/<專案主題>/denylist.txt 只管那個技能的
            公開輸出。一行一個；以 re: 開頭的是正規表示式；# 開頭是註解。比對不分大小寫
  個人資訊  本機絕對路徑（C:\\...、/Users/...、/home/...）、Email
  版權      和不能公開的原件（share 不是 public）的擷取文字連續相同超過 OVERLAP 個字
  二進位檔  不掃內容，只列出來提醒

給 export skill --public 和 export framework 用。結構分離是主要的防線，這裡只是擋關。
"""
import re
from pathlib import Path

import core

TEXT_EXT = {".md", ".txt", ".py", ".json", ".jsonl", ".js", ".mjs", ".ts", ".tsx", ".jsx", ".ps1", ".csv", ".yml",
            ".yaml", ".toml", ".html", ".css", ".sh", ".bat", ".cfg", ".ini", ""}
PERSONAL = [
    ("本機路徑", re.compile(r"\b[A-Za-z]:[\\/](?:Users|Documents|[\w\-. ]+[\\/])[^\s\"'`)]*")),
    ("本機路徑", re.compile(r"/(?:Users|home)/[\w.\-]+/[^\s\"'`)]*")),
    ("Email", re.compile(r"\b[\w.+\-]+@[\w\-]+(?:\.[\w\-]+)+\b")),
]
ALLOWED_EMAIL = {"noreply@anthropic.com"}
OVERLAP = 40
STEP = 8


def read_denylist(path):
    """回傳 [(顯示文字, 編譯好的正規式)]。"""
    out = []
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("re:"):
            out.append((line, re.compile(line[3:], re.I)))
        else:
            out.append((line, re.compile(re.escape(line), re.I)))
    return out


def all_denylists(skill=None):
    """根目錄的 denylist.txt；給了技能代號時，再加上那個技能每份 profile 裡的 denylist.txt。"""
    rules = read_denylist(core.ROOT / "denylist.txt")
    if skill:
        folder = core.ROOT / core.TYPES["skill"]["folder"] / skill
        for path in sorted(folder.glob("profiles/*/denylist.txt")):
            rules += read_denylist(path)
    seen, out = set(), []
    for label, rx in rules:
        if label not in seen:
            seen.add(label)
            out.append((label, rx))
    return out


def _squash(text):
    return re.sub(r"\s+", "", text)


def raw_shingles(records=None):
    """不能公開的原件，擷取文字裡每 OVERLAP 個字的雜湊。回傳 {雜湊: 原件代號}。"""
    records = records if records is not None else core.load_records()
    out = {}
    for rid, rec in records.items():
        if rec.get("type") != "raw" or core.computed_share(rec, records) == "public":
            continue
        folder = rec["path"].with_suffix("")
        if not folder.is_dir():
            continue
        for path in sorted(folder.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_EXT:
                continue
            text = _squash(path.read_text(encoding="utf-8", errors="ignore"))
            for i in range(0, max(0, len(text) - OVERLAP + 1)):
                out.setdefault(hash(text[i:i + OVERLAP]), rid)
    return out


def is_text(path):
    return path.suffix.lower() in TEXT_EXT


def scan_tree(root, denylist=None, shingles=None, skip=()):
    """掃 root 底下所有檔案。回傳 [(相對路徑, 行號, 種類, 內容)]。"""
    root = Path(root)
    denylist = all_denylists() if denylist is None else denylist
    findings = []
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        if any(rel == s or rel.startswith(s.rstrip("/") + "/") for s in skip):
            continue
        for label, rx in denylist:
            if rx.search(rel):
                findings.append((rel, 0, "禁用字（檔名）", label))
        if not is_text(path):
            findings.append((rel, 0, "二進位檔（沒有掃內容）", path.suffix or "無副檔名"))
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            findings.append((rel, 0, "二進位檔（沒有掃內容）", "不是 UTF-8"))
            continue
        for n, line in enumerate(text.splitlines(), start=1):
            for label, rx in denylist:
                m = rx.search(line)
                if m:
                    findings.append((rel, n, "禁用字", m.group(0)))
            for kind, rx in PERSONAL:
                for m in rx.finditer(line):
                    if kind == "Email" and m.group(0).lower() in ALLOWED_EMAIL:
                        continue
                    findings.append((rel, n, kind, m.group(0)[:80]))
        if shingles:
            flat = _squash(text)
            hit = None
            for i in range(0, max(0, len(flat) - OVERLAP + 1), STEP):
                source = shingles.get(hash(flat[i:i + OVERLAP]))
                if source:
                    hit = (source, flat[i:i + OVERLAP])
                    break
            if hit:
                findings.append((rel, 0, "和不能公開的原件文字相同", f"{hit[0]}：「{hit[1]}…」"))
    return list(dict.fromkeys(findings))


def blocking(findings):
    """會擋下輸出的項目（二進位檔只是提醒）。"""
    return [f for f in findings if not f[2].startswith("二進位檔")]


def format_findings(findings):
    return [f"{rel}{f'：第 {n} 行' if n else ''}｜{kind}｜{what}" for rel, n, kind, what in findings]
