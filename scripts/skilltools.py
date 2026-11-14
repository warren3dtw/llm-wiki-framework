"""技能的輸出、安裝、匯入和新建。只用標準庫。

用法（透過 python scripts/wiki.py）：

  export skill <代號> --public [--draft]            公開版：profile 換成 profile.example，只附可以公開的頁，輸出前掃描
  export skill <代號> --profile <專案主題>           私人版：附上那個專案的 profile 和全部依據的頁
  export skill <代號> --bare                        私人版，不附 profile（技能沒有 profile 時用）
      共用選項：--out <資料夾>（預設 build/skills/<public|專案主題|bare>/）
                --folder full   資料夾寫成「代號-全名」（要有 full_name 欄位；預設資料夾就是代號，符合 Agent Skills 規格）

  install skill <代號> <工作專案路徑> --public | --profile <專案主題> | --bare  [--target claude|codex] [--force]
      輸出後放進專案的 .claude/skills/（codex 是 .agents/skills/），並寫 .wiki-source 記下版本和每個檔的雜湊。
      專案裡的技能在安裝後被改過時會拒絕，先用 ingest skill 帶回來，或加 --force

  ingest skill <技能資料夾> [--as <代號>] [--wiki <主題>] [--raw <主題>:raw/<原件代號>] [--kind workflow]
      資料夾裡有 .wiki-source：比對安裝後改了什麼，差異放到 skills/<代號>/incoming/<日期>-<專案>/，不自動合併
      沒有 .wiki-source：第一次匯入，建立 skills/<代號>/（draft、share: private）和原件登記卡

  new skill <代號> [--title 標題]                    從 templates/skill/ 建立一個新技能
  new wiki <名稱> --kind general|project [--title 標題] [--summary 摘要]   建立一個新主題

輸出的 SKILL.md 檔頭只留 Agent Skills 規格的欄位（name、description、metadata），知識庫用的欄位放進 metadata。
"""
import datetime
import difflib
import hashlib
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

import core
import scan

SKILLS = core.ROOT / core.TYPES["skill"]["folder"]
FILES = core.TYPES["skill"]["files"]
ENTRY = core.TYPES["skill"]["entry"]
PRIVATE_BLOCK = re.compile(r"<!--\s*private\s*-->.*?<!--\s*/private\s*-->\n?", re.S)
SKIP_DIRS = {FILES["profiles"], FILES["profile_example"], "incoming", "__pycache__"}
SOURCE_MARK = ".wiki-source"
ID_RE = re.compile(r"[a-z][a-z0-9]*-\d{3}")
KEEP_FIELDS = ("user-invocable", "disable-model-invocation", "allowed-tools", "license", "compatibility")


def option(args, name, default=None):
    if name in args:
        i = args.index(name)
        if i + 1 >= len(args):
            sys.exit(f"{name} 後面要接值")
        value = args[i + 1]
        del args[i:i + 2]
        return value
    return default


def flag(args, name):
    if name in args:
        args.remove(name)
        return True
    return False


def git_commit(path=core.ROOT):
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=path, capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return ""


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tree_hashes(folder):
    folder = Path(folder)
    return {p.relative_to(folder).as_posix(): sha256(p) for p in sorted(folder.rglob("*"))
            if p.is_file() and p.name != SOURCE_MARK and "__pycache__" not in p.parts}


def get_skill(records, sid):
    rid = sid if sid.startswith("skill:") else f"skill:{sid}"
    if rid not in records:
        names = "、".join(sorted(r["name"] for r in records.values() if r.get("type") == "skill"))
        sys.exit(f"找不到技能「{sid}」。目前有：{names or '（沒有）'}")
    return records[rid]


def mode_of(args):
    """回傳 (模式, profile 名稱)。模式是 public、profile 或 bare。"""
    public, bare, profile = flag(args, "--public"), flag(args, "--bare"), option(args, "--profile")
    if sum([public, bare, bool(profile)]) != 1:
        sys.exit("要指定一種：--public、--profile <專案主題> 或 --bare")
    return ("public" if public else "profile" if profile else "bare"), profile


def yaml_str(value):
    return '"' + str(value).replace("\\", "\\\\").replace('"', '\\"') + '"'


def flatten_links(text):
    """輸出的參考頁是單獨的檔案，原本的相對連結點不到，只留文字。"""
    return core.LINK_RE.sub(lambda m: m.group(1) if not re.match(r"^[a-z]+:", m.group(2)) else m.group(0), text)


def reference_page(rec, records, dest):
    """把一頁寫成 references/ 裡的檔案，附帶檔一起複製。回傳寫出的檔名清單。"""
    sid, locator = core.raw_of(rec, records)
    name = f"{rec['type']}-{rec['name']}"
    lines = [f"# {rec.get('title', rec['name'])}", "",
             f"- 代號：{rec['id']}",
             f"- 類型：{core.TYPES[rec['type']]['zh']}・{core.TYPES[rec['type']]['kinds'].get(rec.get('kind'), '')}",
             f"- 摘要：{rec.get('summary', '')}"]
    if sid:
        src = records[sid]
        lines.append(f"- 出處：{src.get('title', sid)}{'，' + locator if locator else ''}")
        if core.computed_share(src, records) == "attribution":
            lines.append(f"- 授權：{src.get('license', '')}（引用時要標出處並遵守這個條件）")
    if rec.get("status") != "reviewed":
        lines.append("- 狀態：草稿，還沒有經過作者確認")
    written = [f"{name}.md"]
    attached = core.attached_file(rec)
    if attached and attached.exists():
        target = f"{name}{attached.suffix}"
        shutil.copyfile(attached, dest / target)
        lines.append(f"- 附帶檔：{target}")
        written.append(target)
    (dest / f"{name}.md").write_text("\n".join(lines) + "\n\n" + flatten_links(rec["body"]).strip() + "\n",
                                     encoding="utf-8")
    return written


def build(rec, records, mode, profile, out_root, folder_style="id", draft_ok=False):
    """把技能輸出到 out_root/<資料夾>/。回傳 (輸出資料夾, 報告文字, 會擋下輸出的問題)。"""
    colls = core.wikis()
    src = rec["path"].parent
    public = mode == "public"
    problems, notes = [], []
    effective = core.share_of(rec, records, colls)
    if public and effective == "private":
        base = core.computed_share(rec, records, colls)
        why = "技能自己標了 share: private" if base != "private" else "它的原件或依據的頁是 private"
        problems.append(f"這個技能不能公開輸出：{why}")
    if public and rec.get("status") != "reviewed" and not draft_ok:
        problems.append("技能還是草稿（status 不是 reviewed）。要輸出草稿請加 --draft，輸出檔會標示草稿")
    if mode == "profile":
        if not (src / FILES["profiles"] / profile).is_dir():
            have = sorted(p.name for p in (src / FILES["profiles"]).glob("*") if p.is_dir())
            problems.append(f"沒有 profiles/{profile}。這個技能有的 profile：{'、'.join(have) or '（沒有）'}")
    folder = rec["name"]
    if folder_style == "full":
        if rec.get("full_name"):
            folder = f"{rec['name']}-{rec['full_name']}"
        else:
            notes.append("沒有 full_name 欄位，資料夾仍用代號")
    out = Path(out_root) / folder
    if problems:
        return out, "", problems
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    # 技能資料夾裡的其他檔案
    for path in sorted(src.rglob("*")):
        rel = path.relative_to(src)
        if not path.is_file() or rel.as_posix() == ENTRY or SKIP_DIRS & set(rel.parts[:1]) \
                or "__pycache__" in rel.parts or (path.name == ".gitkeep" and len(rel.parts) == 2):
            continue
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        if public and scan.is_text(path):
            text = path.read_text(encoding="utf-8", errors="ignore")
            target.write_text(PRIVATE_BLOCK.sub("", text), encoding="utf-8")
        else:
            shutil.copyfile(path, target)

    # profile
    picked = None
    if public and (src / FILES["profile_example"]).is_dir():
        picked = src / FILES["profile_example"]
    elif mode == "profile":
        picked = src / FILES["profiles"] / profile
    if picked:
        for path in sorted(p for p in picked.rglob("*") if p.is_file()):
            if path.name == "denylist.txt":
                continue
            target = out / "profile" / path.relative_to(picked)
            target.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == ".md":
                target.write_text(flatten_links(path.read_text(encoding="utf-8")), encoding="utf-8")
            else:
                shutil.copyfile(path, target)
        notes.append(f"profile/ 來自 {picked.relative_to(src).as_posix()}/")
    elif (src / FILES["profiles"]).is_dir() and mode != "bare":
        notes.append("技能有 profiles 但沒有 profile.example，公開版沒有附 profile")

    # 依據的頁
    refs, skipped = [], []
    ref_dir = out / "references"
    wanted = []
    for ref in rec.get("from", []):
        target = core.resolve(ref, None, records)
        if target and target not in wanted:
            wanted.append(target)
    for target in list(wanted):  # 依據的頁用到的資料頁和同編號的頁也一起附上
        for key in ("data", "pair"):
            for ref in records[target].get(key, []):
                extra = core.resolve(ref, records[target].get("wiki"), records)
                if extra and extra not in wanted:
                    wanted.append(extra)
    for target in wanted:
        page = records[target]
        share = core.share_of(page, records, colls)
        if public and share == "private":
            skipped.append(target)
            continue
        ref_dir.mkdir(exist_ok=True)
        files = reference_page(page, records, ref_dir)
        refs.append((target, page.get("title", ""), files[0], share))

    # calc 函式
    for module, _func in sorted(set(re.findall(r"calc/([\w/]+)\.py::(\w+)", rec["body"]))):
        source = core.ROOT / "calc" / f"{module}.py"
        if source.exists():
            target = out / "scripts" / "calc" / f"{module}.py"
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
            notes.append(f"附上 calc/{module}.py（放在 scripts/calc/）")

    # SKILL.md
    body = rec["body"]
    if public:
        body = PRIVATE_BLOCK.sub("", body)
    head = ["---", f"name: {rec['name']}", f"description: {rec.get('description', '')}"]
    for key in KEEP_FIELDS:
        if rec.get(key):
            head.append(f"{key}: {rec[key]}")
    commit = git_commit()
    head += ["metadata:", f"  version: {yaml_str(rec.get('version', ''))}",
             f"  export: {yaml_str('public' if public else (profile or 'bare'))}",
             f"  status: {yaml_str(rec.get('status', ''))}"]
    if commit:
        head.append(f"  wiki-commit: {yaml_str(commit)}")
    head.append("---")
    parts = ["\n".join(head), ""]
    if rec.get("status") != "reviewed":
        parts += ["> 草稿：這個技能還沒有經過作者確認。", ""]
    parts.append(body.strip())
    if refs or skipped:
        parts += ["", "## 依據的頁", "", "規則後面寫的代號對應到下面的檔案。", ""]
        parts += [f"- `{rid}`：{title}（[references/{file}](references/{file})）" for rid, title, file, _ in refs]
        if skipped:
            parts.append(f"- 另有 {len(skipped)} 頁依據因為授權不能隨附。")
    (out / ENTRY).write_text("\n".join(parts) + "\n", encoding="utf-8")

    # 掃描
    findings = []
    if public:
        findings = scan.scan_tree(out, denylist=scan.all_denylists(rec["name"]), shingles=scan.raw_shingles(records))
        problems += scan.format_findings(scan.blocking(findings))
    lines_count = (out / ENTRY).read_text(encoding="utf-8").count("\n")
    report = [f"# 輸出報告：{rec['name']} {rec.get('version', '')}", "",
              f"- 日期：{datetime.date.today().isoformat()}",
              f"- 模式：{'公開版' if public else '私人版'}（{profile or mode}）",
              f"- 知識庫 commit：{commit or '不明'}",
              f"- 技能狀態：{rec.get('status', '')}；可見度：{effective}",
              f"- 輸出位置：{out}",
              f"- 檔案數：{len(tree_hashes(out))}；SKILL.md {lines_count} 行", ""]
    report += ["## 附上的依據", ""] + ([f"- {rid}（{share}）" for rid, _, _, share in refs] or ["- 沒有"])
    report += ["", "## 沒有附上的依據（授權不能公開）", ""] + ([f"- {x}" for x in skipped] or ["- 沒有"])
    report += ["", "## 說明", ""] + ([f"- {n}" for n in notes] or ["- 沒有"])
    if public:
        binary = [f for f in findings if f[2].startswith("二進位檔")]
        report += ["", "## 掃描", "",
                   f"- 禁用字規則 {len(scan.all_denylists(rec['name']))} 條；個人資訊（本機路徑、Email）；和不能公開的原件比對文字",
                   f"- 擋下的問題：{len(scan.blocking(findings))} 個"]
        report += [f"  - {x}" for x in scan.format_findings(scan.blocking(findings))]
        report += [f"- 沒有掃內容的二進位檔：{len(binary)} 個"] + [f"  - {f[0]}" for f in binary]
    return out, "\n".join(report) + "\n", problems


def cmd_export(args):
    if not args:
        sys.exit(__doc__)
    sid = args.pop(0)
    mode, profile = mode_of(args)
    draft_ok = flag(args, "--draft")
    style = option(args, "--folder", "id")
    out_root = option(args, "--out")
    records = core.load_records()
    rec = get_skill(records, sid)
    label = "public" if mode == "public" else (profile or "bare")
    out_root = Path(out_root) if out_root else core.ROOT / "build" / "skills" / label
    out, report, problems = build(rec, records, mode, profile, out_root, style, draft_ok)
    report_path = Path(out_root) / f"{rec['name']}.report.md"
    if report:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(report, encoding="utf-8")
    if problems:
        if out.exists():
            shutil.rmtree(out)
        print(f"沒有輸出 {rec['name']}：")
        for p in problems:
            print(f"  - {p}")
        if report:
            print(f"報告：{report_path}")
        sys.exit(1)
    print(f"已輸出 {rec['name']} {rec.get('version', '')}（{'公開版' if mode == 'public' else '私人版'}）到 {out}")
    print(f"報告：{report_path}")
    return out


def cmd_install(args):
    if len(args) < 2:
        sys.exit(__doc__)
    sid, project = args.pop(0), Path(args.pop(0)).expanduser().resolve()
    mode, profile = mode_of(args)
    target = option(args, "--target", "claude")
    force, draft_ok = flag(args, "--force"), flag(args, "--draft")
    style = option(args, "--folder", "id")
    if target not in ("claude", "codex"):
        sys.exit("--target 要是 claude 或 codex")
    if not project.is_dir():
        sys.exit(f"找不到工作專案 {project}")
    records = core.load_records()
    rec = get_skill(records, sid)
    label = "public" if mode == "public" else (profile or "bare")
    staging = core.ROOT / "build" / "skills" / label
    out, report, problems = build(rec, records, mode, profile, staging, style, draft_ok)
    if problems:
        print(f"沒有安裝 {rec['name']}：")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)
    base = project / (".claude" if target == "claude" else ".agents") / "skills"
    dest = base / out.name
    existing = [p.parent for p in base.glob(f"*/{SOURCE_MARK}")
                if json.loads(p.read_text(encoding="utf-8")).get("skill") == rec["name"]] if base.is_dir() else []
    for old in existing + ([dest] if dest.exists() and dest not in existing else []):
        mark = old / SOURCE_MARK
        if not mark.exists():
            if not force:
                sys.exit(f"{old} 已經存在，而且不是從知識庫安裝的。先用 ingest skill 匯入，或加 --force 覆蓋")
        else:
            recorded = json.loads(mark.read_text(encoding="utf-8")).get("files", {})
            if recorded != tree_hashes(old) and not force:
                sys.exit(f"{old} 在安裝後被改過。先執行 python scripts/wiki.py ingest skill \"{old}\" 把改動帶回來，"
                         "或加 --force 覆蓋")
        shutil.rmtree(old)
    base.mkdir(parents=True, exist_ok=True)
    shutil.copytree(out, dest)
    (dest / SOURCE_MARK).write_text(json.dumps({
        "skill": rec["name"], "version": rec.get("version", ""), "mode": mode, "profile": profile or "",
        "wiki_commit": git_commit(), "installed": datetime.date.today().isoformat(),
        "files": tree_hashes(dest)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"已安裝 {rec['name']} {rec.get('version', '')} 到 {dest}")
    print(f"在專案裡改了之後，用 python scripts/wiki.py ingest skill \"{dest}\" 帶回來。")


def first_heading(body):
    m = re.search(r"^# (.+)$", body, re.M)
    return m.group(1).strip() if m else ""


def cmd_ingest(args):
    if not args:
        sys.exit(__doc__)
    folder = Path(args.pop(0)).expanduser().resolve()
    if not (folder / ENTRY).exists():
        sys.exit(f"{folder} 裡沒有 {ENTRY}")
    if (folder / SOURCE_MARK).exists():
        return ingest_changes(folder)
    return ingest_new(folder, args)


def project_of(folder):
    """技能資料夾所在的工作專案（往上找到 .claude 或 .agents 的上一層）。"""
    for parent in folder.parents:
        if parent.name in (".claude", ".agents"):
            return parent.parent
    return folder.parent


def ingest_changes(folder):
    mark = json.loads((folder / SOURCE_MARK).read_text(encoding="utf-8"))
    records = core.load_records()
    rec = get_skill(records, mark["skill"])
    now, then = tree_hashes(folder), mark.get("files", {})
    changed = sorted(k for k in now if k in then and now[k] != then[k])
    added = sorted(k for k in now if k not in then)
    removed = sorted(k for k in then if k not in now)
    if not (changed or added or removed):
        print(f"{folder} 和安裝時相同，沒有要帶回來的改動。")
        return
    project = project_of(folder)
    today = datetime.date.today().isoformat()
    dest = rec["path"].parent / "incoming" / f"{today}-{project.name}"
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    staging = core.ROOT / "build" / "skills" / "_compare"
    fresh, _, problems = build(rec, records, mark.get("mode", "bare"), mark.get("profile") or None, staging,
                               "id", True)
    lines = [f"# 從 {project.name} 帶回來的改動：{rec['name']}", "",
             f"- 日期：{today}",
             f"- 安裝時的版本：{mark.get('version', '')}（知識庫 commit {mark.get('wiki_commit', '不明')}，"
             f"{mark.get('mode', '')}{'：' + mark['profile'] if mark.get('profile') else ''}）",
             f"- 知識庫現在的版本：{rec.get('version', '')}（commit {git_commit() or '不明'}）",
             f"- 專案的 commit：{git_commit(project) or '不明'}", ""]
    if mark.get("wiki_commit") != git_commit():
        lines += ["知識庫在安裝之後也改過。下面的差異是「專案現在的檔案」對「知識庫現在重新輸出的檔案」，兩邊的改動都在裡面。", ""]
    lines += ["## 怎麼處理", "",
              "逐條判斷每個改動屬於哪一層，再手動併進知識庫（規則見 MAINTAINING 的「技能」）：", "",
              "1. 工具知識、領域知識：改 `SKILL.md` 或 `scripts/`；會被別的技能用到或會被反駁的，寫成通用主題的頁。",
              "2. 專案的慣例、參數：放 `profiles/<專案主題>/`。專案裡的 `profile/` 對應到這裡。",
              "3. 案件事實：放 `profiles/<專案主題>/cases.md` 或專案主題的頁、inbox。",
              "4. 併完後升版本、寫 CHANGELOG，刪掉這個資料夾，再重新 install。", "",
              "## 檔案", ""]
    lines += [f"- 改過：{k}" for k in changed] + [f"- 新增：{k}" for k in added] + [f"- 刪除：{k}" for k in removed]
    for rel in changed + added:
        source = folder / rel
        target = dest / "files" / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        base = fresh / rel if not problems else None
        if scan.is_text(source):
            new = source.read_text(encoding="utf-8", errors="ignore").splitlines()
            old = base.read_text(encoding="utf-8", errors="ignore").splitlines() if base and base.exists() else []
            diff = list(difflib.unified_diff(old, new, f"知識庫/{rel}", f"專案/{rel}", lineterm="", n=2))
            if diff:
                lines += ["", f"### {rel}", "", "```diff"] + diff[:400] + ["```"]
                if len(diff) > 400:
                    lines.append(f"（差異共 {len(diff)} 行，只列前 400 行；完整檔案在 files/{rel}）")
    (dest / "DIFF.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    shutil.rmtree(staging, ignore_errors=True)
    print(f"改過 {len(changed)} 個、新增 {len(added)} 個、刪除 {len(removed)} 個檔案。")
    print(f"差異和檔案放在 {dest.relative_to(core.ROOT).as_posix()}/，照 DIFF.md 的說明併進知識庫。")


def ingest_new(folder, args):
    wiki = option(args, "--wiki", "agent")
    raw_ref = option(args, "--raw")
    kind = option(args, "--kind", "workflow")
    sid = option(args, "--as")
    if kind not in core.TYPES["skill"]["kinds"]:
        sys.exit(f"--kind 應為 {'、'.join(core.TYPES['skill']['kinds'])}")
    fm, body = core.parse_frontmatter((folder / ENTRY).read_text(encoding="utf-8"))
    fm = fm or {}
    original_name = fm.get("name", folder.name)
    sid = sid or original_name
    if not ID_RE.fullmatch(sid):
        sys.exit(f"「{sid}」不是「前綴-三位數」的代號。用 --as 指定，例如 --as rhino-003")
    dest = SKILLS / sid
    if dest.exists():
        sys.exit(f"skills/{sid} 已經存在")
    colls = core.wikis()
    if wiki not in colls:
        sys.exit(f"沒有主題 {wiki}")
    project = project_of(folder)
    today = datetime.date.today().isoformat()
    commit = git_commit(project)
    records = core.load_records()
    if raw_ref:
        if raw_ref not in records or records[raw_ref].get("type") != "raw":
            sys.exit(f"找不到原件 {raw_ref}")
    else:
        code = re.sub(r"[^a-z0-9]+", "-", project.name.lower()).strip("-") + "-" + today
        raw_ref = f"{wiki}:raw/{code}"
        card = colls[wiki]["path"] / "raw" / f"{code}.md"
        if raw_ref not in records:
            card.parent.mkdir(parents=True, exist_ok=True)
            card.write_text(f"""---
title: "{project.name} 工作專案快照（{today}）"
title_en: "{project.name} project snapshot"
type: raw
kind: project
format: none
lang: [zh]
region: any
summary: "工作專案 {project.name} 的技能，匯入成知識庫的技能"
edition: "commit {commit or '不明'}"
license: 待補
share: private
status: draft
origin: ingest
updated: {today}
---

從工作專案 {project.name} 匯入的技能。檔案本身在 `skills/` 底下，這張卡只記出處。

## 可信度

- 待補：這些技能在哪些環境實測過。

## 閱讀進度

| 範圍 | 狀態 | 產出 |
|---|---|---|

## 已知問題

- 目前沒有。
""", encoding="utf-8")
            print(f"已建立原件登記卡 {card.relative_to(core.ROOT).as_posix()}（share: private，授權待補）")
    rel_in_project = folder.relative_to(project).as_posix() if folder.is_relative_to(project) else folder.name

    shutil.copytree(folder, dest, ignore=shutil.ignore_patterns("__pycache__", SOURCE_MARK, "*.pyc"))
    description = fm.get("description", "").strip()
    title = first_heading(body) or description[:40]
    summary = re.split(r"[。；]", re.sub(rf"^{re.escape(original_name)}[：:]\s*", "", description))[0][:78]
    full_name = folder.name[len(original_name) + 1:] if folder.name.startswith(original_name + "-") else ""
    head = ["---", f"name: {sid}", f"title: {title}", f"summary: {yaml_str(summary)}",
            f"description: {description}"]
    for key in KEEP_FIELDS:
        if fm.get(key):
            head.append(f"{key}: {fm[key]}")
    head += ["type: skill", f"kind: {kind}", "version: 0.1.0", "share: private"]
    if full_name:
        head.append(f"full_name: {full_name}")
    if original_name != sid:
        head.append(f"original_name: {original_name}")
    head += ["atoms: []", "points: []", "from: []", "uses: []",
             f"raw: {yaml_str(raw_ref + ', ' + rel_in_project + '/' + ENTRY)}",
             "status: draft", f"updated: {today}", "checked:", "---"]
    (dest / ENTRY).write_text("\n".join(head) + "\n\n" + body.lstrip("\n"), encoding="utf-8")
    changelog = dest / FILES["changelog"]
    if not changelog.exists():
        changelog.write_text(f"# 版本紀錄\n\n只往上追加。每筆寫版本、日期、改了什麼、回饋從哪裡來。\n\n"
                             f"## 0.1.0（{today}）\n\n- 從工作專案 {project.name}（commit {commit or '不明'}，"
                             f"`{rel_in_project}`）匯入，內容沒有改。原本的名稱是 `{original_name}`。\n", encoding="utf-8")
    print(f"已匯入成 skills/{sid}/（draft、share: private）。")
    findings = scan.blocking(scan.scan_tree(dest, denylist=scan.all_denylists(sid)))
    if findings:
        print(f"\n掃到 {len(findings)} 處可能要搬到 profile 的內容（禁用字、本機路徑、Email）：")
        for line in scan.format_findings(findings)[:30]:
            print(f"  - {line}")
        if len(findings) > 30:
            print(f"  …還有 {len(findings) - 30} 處")
    print("\n接下來：補 tests.md；把專案的慣例搬到 profiles/<專案主題>/；填 atoms、points、from；"
          "再執行 python scripts/wiki.py index 和 lint。")


def cmd_new(args):
    if len(args) < 2 or args[0] not in ("skill", "wiki"):
        sys.exit(__doc__)
    what, name = args.pop(0), args.pop(0)
    today = datetime.date.today().isoformat()
    title = option(args, "--title")
    if what == "skill":
        if not ID_RE.fullmatch(name):
            sys.exit("技能代號要寫成「前綴-三位數」，例如 rhino-002")
        dest = SKILLS / name
        if dest.exists():
            sys.exit(f"skills/{name} 已經存在")
        shutil.copytree(core.ROOT / "templates" / "skill", dest)
        for keep in dest.rglob(".gitkeep"):
            if any(p for p in keep.parent.iterdir() if p.name != ".gitkeep"):
                keep.unlink()
        entry = dest / ENTRY
        text = entry.read_text(encoding="utf-8")
        text = text.replace("name: 前綴-001 ", f"name: {name} ", 1).replace("description: 前綴-001：", f"description: {name}：", 1)
        text = text.replace("updated: YYYY-MM-DD", f"updated: {today}", 1)
        if title:
            text = re.sub(r"^title: 標題 ", f"title: {title} ", text, count=1, flags=re.M)
        entry.write_text(text, encoding="utf-8")
        log = dest / FILES["changelog"]
        log.write_text(log.read_text(encoding="utf-8").replace("YYYY-MM-DD", today), encoding="utf-8")
        print(f"已建立 skills/{name}/。填好 SKILL.md 和 tests.md 後執行 python scripts/wiki.py index 和 lint。")
        return
    kind = option(args, "--kind")
    summary = option(args, "--summary")
    if kind not in core.SCHEMA["wiki_kinds"]:
        sys.exit(f"--kind 應為 {'、'.join(core.SCHEMA['wiki_kinds'])}")
    if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name):
        sys.exit("主題名稱只能用英文小寫、數字和連字號")
    if kind == "project" and not name.startswith("project-"):
        sys.exit("專案主題的名稱要以 project- 開頭")
    dest = core.ROOT / "wikis" / name
    if dest.exists():
        sys.exit(f"wikis/{name} 已經存在")
    dest.mkdir(parents=True)
    title = title or name
    summary = summary or "待補：這個主題的範圍"
    rule = ("通用主題：不屬於特定專案的知識。不能引用專案主題。" if kind == "general" else
            "專案主題：只屬於這個專案的內容。可以引用通用主題。不記業主名稱、合約金額等機密，內容不能拿到這個 repo 以外的地方用。")
    (dest / "WIKI.md").write_text(f"""---
title: {title}
kind: {kind}
summary: {yaml_str(summary)}
---

{summary}

{rule}

## 工作情境

| 代號 | 情境 | 需要哪些知識 |
|---|---|---|
| S1 | 待補 | 待補 |
""", encoding="utf-8")
    (dest / "inbox.md").write_text(f"""# 收件匣：{name}

想法、經驗、疑問、想研究的題目，一行一則，不必分類。
使用 agent 發現知識庫答不出來或有錯時，也寫在這裡，開頭加〔agent〕。

格式：`- YYYY-MM-DD｜內容`

## 待處理
""", encoding="utf-8")
    print(f"已建立 wikis/{name}/（{core.SCHEMA['wiki_kinds'][kind]}）。原件放進 wikis/{name}/raw/ 後用 ingest raw 登記。")
