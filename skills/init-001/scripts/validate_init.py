#!/usr/bin/env python3
"""檢查 init-001 產生的空結構。只用 Python 標準庫。

用法：
  python validate_init.py <專案根目錄> --mode general|rhino-cadcraft|rhino-animation [--codex]

--codex：這個專案也給 Codex 用，必須有根目錄的 AGENTS.md。

檢查 init-001 Phase 6 裡可以機械判斷的部分：
  I-01 必要路徑都存在，.gitkeep 是零位元檔
  I-02 文件不是空殼（除了標題至少要有一行內容），沒有未解析的佔位符（docs/templates/ 除外）
  I-03 本地 Markdown 連結都找得到；沒有連到其他模式的專用文件
  I-04 .claude/settings.json 可以解析，權限是陣列、沒有重複、沒有同一工具又允許又拒絕
另外確認 PROJECT 和 INIT-REPORT 寫的模式和 --mode 相同。
內容契約、空白語意、首個任務走讀（I-02 的其餘部分、I-05、I-06）仍要人工走讀，這支程式通過不等於驗收通過。
"""
import json
import re
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

COMMON = [
    "README.md", "CLAUDE.md", ".gitignore",
    *[f"docs/{n}.md" for n in ["README", "PROJECT", "ARCHITECTURE", "DEVELOPMENT", "FEATURES",
                               "TESTING", "CHANGELOG", "INIT-REPORT", "FEEDBACK"]],
    *[f"docs/templates/{n}.md" for n in ["plan", "specs", "tasks"]],
    "docs/plans/.gitkeep", "docs/plans/archive/.gitkeep",
    ".claude/settings.json", ".claude/rules/workflow.md", ".claude/rules/delivery.md",
    ".claude/hooks/README.md", ".claude/agents/doc-maintainer.md", ".claude/agents/acceptance-reviewer.md",
]
MODES = {
    "general": [],
    "rhino-cadcraft": [
        "docs/MODELING.md", "docs/DRAWING.md", "docs/DELIVERY.md", ".claude/rules/drawing-workflow.md",
        "sources/.gitkeep", "models/.gitkeep", "drawings/.gitkeep", "deliverables/.gitkeep",
    ],
    "rhino-animation": [
        "docs/MODELING.md", "docs/ASSEMBLY.md", "docs/ANIMATION.md", "docs/DELIVERY.md",
        ".claude/rules/animation-workflow.md", ".claude/agents/README.md", ".claude/agents/animation-reviewer.md",
        "sources/.gitkeep", "models/.gitkeep", "exports/.gitkeep", "public/assembly/.gitkeep",
        "deliverables/.gitkeep",
    ],
}
MODE_DOCS = {"docs/MODELING.md", "docs/DRAWING.md", "docs/DELIVERY.md", "docs/ASSEMBLY.md", "docs/ANIMATION.md",
             ".claude/rules/drawing-workflow.md", ".claude/rules/animation-workflow.md",
             ".claude/agents/animation-reviewer.md"}
PLACEHOLDER = re.compile(r"\bTODO\b|\{專案名稱\}|\{值\}")
LINK = re.compile(r"\[[^\]\n]+\]\(([^)\s]+)\)")
FENCE = re.compile(r"```.*?```", re.S)


def validate(root, mode, codex=False):
    """回傳問題清單；空清單代表通過。"""
    root = Path(root)
    problems = []
    required = COMMON + MODES[mode] + (["AGENTS.md"] if codex else [])
    for rel in required:
        path = root / rel
        if not path.exists():
            problems.append(f"I-01 缺少 {rel}")
        elif rel.endswith(".gitkeep") and path.stat().st_size != 0:
            problems.append(f"I-01 {rel} 不是零位元檔")

    forbidden = MODE_DOCS - set(MODES[mode])
    for rel in sorted(forbidden):
        if (root / rel).exists():
            problems.append(f"I-03 {mode} 不應該有 {rel}")

    for path in sorted(p for p in root.rglob("*.md") if p.is_file()):
        rel = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8")
        body = re.sub(r"(?s)^---\n.*?\n---\n", "", text)
        if rel in required and not any(line.strip() and not line.lstrip().startswith("#")
                                       for line in body.splitlines()):
            problems.append(f"I-02 {rel} 只有標題，沒有內容")
        if not rel.startswith("docs/templates/") and PLACEHOLDER.search(text):
            problems.append(f"I-02 {rel} 有未解析的佔位符")
        for href in LINK.findall(FENCE.sub("", text)):
            if re.match(r"^[a-z][a-z0-9+.-]*:", href) or href.startswith("#"):
                continue
            target = (path.parent / href.split("#")[0]).resolve()
            if not target.exists():
                problems.append(f"I-03 {rel} 的連結找不到：{href}")
                continue
            try:
                target_rel = target.relative_to(root.resolve()).as_posix()
            except ValueError:
                problems.append(f"I-03 {rel} 的連結指到專案外：{href}")
                continue
            if target_rel in forbidden:
                problems.append(f"I-03 {rel} 連到其他模式的文件 {target_rel}")

    settings = root / ".claude/settings.json"
    if settings.exists():
        try:
            data = json.loads(settings.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            problems.append(f"I-04 settings.json 無法解析：{exc}")
        else:
            perms = data.get("permissions", {})
            for key in ["allow", "ask", "deny"]:
                value = perms.get(key, [])
                if not isinstance(value, list):
                    problems.append(f"I-04 permissions.{key} 要是陣列")
                elif len(value) != len(set(value)):
                    problems.append(f"I-04 permissions.{key} 有重複項目")
            both = set(perms.get("allow", [])) & set(perms.get("deny", []))
            if both:
                problems.append(f"I-04 同時允許又拒絕：{'、'.join(sorted(both))}")
            if not isinstance(data.get("hooks", {}), dict):
                problems.append("I-04 hooks 要是物件")

    for rel, pattern in [("docs/PROJECT.md", rf"\|\s*模式\s*\|\s*{re.escape(mode)}\s*\|"),
                         ("docs/INIT-REPORT.md", rf"模式：{re.escape(mode)}\b")]:
        path = root / rel
        if path.exists() and not re.search(pattern, path.read_text(encoding="utf-8")):
            problems.append(f"{rel} 寫的模式不是 {mode}")
    return problems


def main():
    args = sys.argv[1:]
    codex = "--codex" in args
    args = [a for a in args if a != "--codex"]
    if "--mode" not in args or len(args) != 3:
        sys.exit(__doc__)
    i = args.index("--mode")
    mode = args[i + 1]
    root = [a for j, a in enumerate(args) if j not in (i, i + 1)][0]
    if mode not in MODES:
        sys.exit(f"模式只能是 {'、'.join(MODES)}")
    problems = validate(root, mode, codex)
    for p in problems:
        print(f"失敗：{p}")
    print(f"{mode}：{len(problems)} 個問題" if problems else f"{mode}：機械檢查通過（內容契約仍要人工走讀）")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
