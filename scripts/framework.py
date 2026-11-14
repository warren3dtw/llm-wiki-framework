"""export framework：輸出一份空的框架，只有程式、規則、模板和指定的技能，不含任何主題、原子、原件和個人資料。

用法（透過 python scripts/wiki.py）：
  export framework [--out 資料夾]      預設輸出到 build/framework/

做的事：
  1. 複製框架檔案：說明文件、schema.json、scripts/、templates/、docs/FRAMEWORK.md、.github/、.gitignore
  2. 複製 framework.json 的 skills 列出的技能（要能公開；專案的 profiles 不帶，raw 欄位清空）
  3. 依 framework.json 的 replace 把個人或專案名稱換成中性的寫法（開頭是 re: 的是正規表示式，照順序做）
  4. 放上空的 wikis/、atoms/、calc/，以及空白的 denylist.txt、framework.json、README.md
  5. 在輸出的資料夾裡重建索引、執行 lint，確認框架自己跑得起來
  6. 用禁用字、個人資訊、原件文字掃描整個輸出

第 5、6 步有任何問題就以代碼 1 結束，並保留輸出的資料夾和報告供檢查。只用標準庫。
"""
import datetime
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import core
import scan
import skilltools

FILES = ["AGENTS.md", "CLAUDE.md", "USING.md", "MAINTAINING.md", "GLOSSARY.md", "schema.json", ".gitignore",
         "docs/FRAMEWORK.md", "calc/__init__.py"]
FOLDERS = ["scripts", "templates", ".github"]
EMPTY = ["wikis", "atoms"]
SKIP_NAMES = {"__pycache__"}


def load_config():
    path = core.ROOT / "framework.json"
    if not path.exists():
        return {"skills": [], "replace": []}
    return json.loads(path.read_text(encoding="utf-8"))


def copy_tree(src, dst):
    for path in sorted(src.rglob("*")):
        if not path.is_file() or SKIP_NAMES & set(path.parts) or path.suffix == ".pyc":
            continue
        target = dst / path.relative_to(src)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(path, target)


def strip_skill(folder):
    """帶進框架的技能：拿掉專案的 profiles 和還沒併入的改動，raw 欄位清空（原件登記卡不在框架裡）。"""
    for name in (core.TYPES["skill"]["files"]["profiles"], "incoming"):
        shutil.rmtree(folder / name, ignore_errors=True)
    entry = folder / core.TYPES["skill"]["entry"]
    text = entry.read_text(encoding="utf-8")
    end = text.find("\n---", 4)
    head = re.sub(r"(?m)^raw:.*$", 'raw: ""', text[:end])
    entry.write_text(head + text[end:], encoding="utf-8")


def main(argv=None):
    args = list(sys.argv[1:] if argv is None else argv)
    out = Path(skilltools.option(args, "--out") or core.ROOT / "build" / "framework").resolve()
    if out == core.ROOT or core.ROOT.is_relative_to(out):
        sys.exit("輸出資料夾不能是知識庫本身或它的上層")
    config = load_config()
    records = core.load_records()
    colls = core.wikis()
    problems, notes = [], []

    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for rel in FILES:
        src = core.ROOT / rel
        if src.exists():
            (out / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(src, out / rel)
        else:
            problems.append(f"框架檔案不存在：{rel}")
    for rel in FOLDERS:
        if (core.ROOT / rel).is_dir():
            copy_tree(core.ROOT / rel, out / rel)
    for name in ("README.md", "denylist.txt", "framework.json"):
        src = core.ROOT / "templates" / "framework" / name
        if src.exists():
            shutil.copyfile(src, out / name)
    for name in EMPTY:
        (out / name).mkdir(exist_ok=True)
        (out / name / ".gitkeep").touch()

    skills_dir = out / core.TYPES["skill"]["folder"]
    skills_dir.mkdir(exist_ok=True)
    for sid in config.get("skills", []):
        rid = f"skill:{sid}"
        if rid not in records:
            problems.append(f"framework.json 列的技能 {sid} 不存在")
            continue
        rec = records[rid]
        share = core.share_of(rec, records, colls)
        if share == "private":
            problems.append(f"技能 {sid} 是 private，不能放進空框架")
            continue
        copy_tree(rec["path"].parent, skills_dir / sid)
        strip_skill(skills_dir / sid)
        if rec.get("status") != "reviewed":
            notes.append(f"技能 {sid} 還是草稿（{rec.get('status')}）")
    if not any(skills_dir.iterdir()):
        (skills_dir / ".gitkeep").touch()

    replaced = 0
    pairs = [(re.compile(a[3:]) if a.startswith("re:") else a, b) for a, b in config.get("replace", [])]
    for path in sorted(p for p in out.rglob("*") if p.is_file() and scan.is_text(p)):
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        new = text
        for a, b in pairs:
            new = a.sub(b, new) if hasattr(a, "sub") else new.replace(a, b)
        if new != text:
            path.write_text(new, encoding="utf-8")
            replaced += 1

    checks = []
    for step in (["index"], ["lint"]):
        result = subprocess.run([sys.executable, "-B", str(out / "scripts" / "wiki.py")] + step, cwd=out,
                                capture_output=True, text=True, encoding="utf-8")
        tail = (result.stdout + result.stderr).strip().splitlines()[-3:]
        checks.append((step[0], result.returncode, tail))
        if result.returncode != 0:
            problems.append(f"輸出的框架執行 wiki.py {step[0]} 失敗：{' / '.join(tail)}")
    for cache in list(out.rglob("__pycache__")):
        shutil.rmtree(cache, ignore_errors=True)

    findings = scan.scan_tree(out, shingles=scan.raw_shingles(records))
    blocking = scan.blocking(findings)
    problems += scan.format_findings(blocking)

    n_files = sum(1 for p in out.rglob("*") if p.is_file())
    report = [f"# 空框架輸出報告", "",
              f"- 日期：{datetime.date.today().isoformat()}",
              f"- 知識庫 commit：{skilltools.git_commit() or '不明'}",
              f"- 輸出位置：{out}",
              f"- 檔案數：{n_files}",
              f"- 帶進去的技能：{'、'.join(config.get('skills', [])) or '沒有'}",
              f"- 替換了 {replaced} 個檔案裡的字（規則 {len(pairs)} 條，見 framework.json）", "",
              "## 沒有帶進去的", "",
              "- 全部主題（wikis/）、原子（atoms/）、原件和擷取文字",
              "- 其他技能、技能的 profiles",
              "- calc/ 的公式（依據的頁不在框架裡）",
              "- docs/ 裡的討論紀錄（只帶 FRAMEWORK.md）",
              "- 根目錄的 denylist.txt 和 framework.json（換成空白的）", "",
              "## 框架自己跑得起來嗎", ""]
    report += [f"- wiki.py {name}：{'通過' if code == 0 else '失敗'}（{' / '.join(tail)}）" for name, code, tail in checks]
    report += ["", "## 掃描", "",
               f"- 禁用字規則 {len(scan.all_denylists())} 條；個人資訊（本機路徑、Email）；和不能公開的原件比對文字",
               f"- 擋下的問題：{len(blocking)} 個"]
    report += [f"  - {x}" for x in scan.format_findings(blocking)]
    binary = [f for f in findings if f[2].startswith("二進位檔")]
    report += [f"- 沒有掃內容的二進位檔：{len(binary)} 個"] + [f"  - {f[0]}" for f in binary]
    report += ["", "## 說明", ""] + ([f"- {n}" for n in notes] or ["- 沒有"])
    report_path = out.parent / f"{out.name}.report.md"
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

    if problems:
        print(f"空框架有 {len(problems)} 個問題，不要拿給別人：")
        for p in problems[:40]:
            print(f"  - {p}")
        print(f"輸出保留在 {out} 供檢查。報告：{report_path}")
        sys.exit(1)
    print(f"已輸出空框架到 {out}（{n_files} 個檔案）。")
    for n in notes:
        print(f"  注意：{n}")
    print(f"報告：{report_path}")


if __name__ == "__main__":
    main()
