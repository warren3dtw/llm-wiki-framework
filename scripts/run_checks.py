#!/usr/bin/env python3
"""執行紀錄裡的核對區塊，確認 calc/ 的公式算出來的值和紀錄寫的相符。只用標準庫。

用法：python scripts/run_checks.py [-v]

核對區塊是內文裡標記為 check 的程式碼區塊，內容是 JSON：
  {"name": "說明", "calc": "timber.clt.gamma_value", "inputs": {...}, "expect": 0.954, "tolerance": 0.0005}
函式回傳多個值時，expect 寫成物件，只比對列出的項目。

另外檢查：
  - 內文提到的 calc/xxx.py::函式 真的存在
  - calc/ 每個函式的說明文字有「依據：紀錄代號」，紀錄存在
  - calc/ 每個函式至少被一個核對區塊驗證
  - 函式的參數全部是具名參數
  - 技能的 scripts/test_*.py 用 unittest 執行；檔案前三行有「# 需要外部軟體」的略過並列出
"""
import importlib
import inspect
import json
import re
import subprocess
import sys

import core

sys.path.insert(0, str(core.ROOT))
BLOCK = re.compile(r"```check\s*\n(.*?)\n```", re.S)
CALC_REF = re.compile(r"calc/([\w/]+)\.py::(\w+)")
BASIS = re.compile(r"依據：\s*(\S+)")
NEEDS_EXTERNAL = "# 需要外部軟體"


def run_skill_tests(failures, verbose):
    """執行每個技能 scripts/ 裡的 test_*.py。回傳 (跑了幾個, 略過的清單)。"""
    ran, skipped = 0, []
    for test in sorted((core.ROOT / core.TYPES["skill"]["folder"]).glob("*/scripts/test_*.py")):
        rel = test.relative_to(core.ROOT).as_posix()
        if NEEDS_EXTERNAL in test.read_text(encoding="utf-8").splitlines()[:3]:
            skipped.append(rel)
            continue
        ran += 1
        result = subprocess.run([sys.executable, "-B", "-m", "unittest", test.stem], cwd=test.parent,
                                capture_output=True, text=True, encoding="utf-8")
        if result.returncode != 0:
            tail = (result.stderr or result.stdout).strip().splitlines()[-5:]
            failures.append(f"{rel}：測試失敗\n      " + "\n      ".join(tail))
        elif verbose:
            print(f"  通過：{rel}")
    return ran, skipped


def load(dotted):
    module, func = dotted.rsplit(".", 1)
    return getattr(importlib.import_module(f"calc.{module}"), func)


def compare(result, expect, tol):
    if isinstance(expect, dict):
        if not isinstance(result, dict):
            return [f"預期多個值，實際回傳 {result!r}"]
        return [f"{k}：算出 {result.get(k)!r}，預期 {v}" for k, v in expect.items()
                if k not in result or abs(result[k] - v) > tol]
    if abs(result - expect) > tol:
        return [f"算出 {result:.6g}，預期 {expect}（容許差 {tol}）"]
    return []


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    verbose = "-v" in argv
    records = core.load_records()
    failures, covered = [], set()
    blocks = 0
    for rid, rec in records.items():
        text = rec["body"]
        for module, func in CALC_REF.findall(text):
            try:
                load(module.replace("/", ".") + "." + func)
            except (ImportError, AttributeError):
                failures.append(f"{rec['rel']}：提到的 calc/{module}.py::{func} 不存在")
        for i, raw in enumerate(BLOCK.findall(text), start=1):
            blocks += 1
            where = f"{rec['rel']} 第 {i} 個核對區塊"
            try:
                spec = json.loads(raw)
                result = load(spec["calc"])(**spec.get("inputs", {}))
                problems = compare(result, spec["expect"], spec.get("tolerance", 0))
            except Exception as exc:
                failures.append(f"{where}：無法執行（{type(exc).__name__}: {exc}）")
                continue
            covered.add(spec["calc"])
            if problems:
                failures += [f"{where}（{spec.get('name', '')}）：{p}" for p in problems]
            elif verbose:
                print(f"  通過：{where}（{spec.get('name', '')}）")
    functions = 0
    for path in sorted((core.ROOT / "calc").rglob("*.py")):
        if path.name == "__init__.py":
            continue
        dotted = ".".join(path.relative_to(core.ROOT / "calc").with_suffix("").parts)
        module = importlib.import_module(f"calc.{dotted}")
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name.startswith("_") or func.__module__ != module.__name__:
                continue
            functions += 1
            where = f"calc/{path.relative_to(core.ROOT / 'calc').as_posix()}::{name}"
            m = BASIS.search(inspect.getdoc(func) or "")
            if not m:
                failures.append(f"{where}：說明文字要有「依據：紀錄代號」")
            elif m.group(1) not in records:
                failures.append(f"{where}：依據的紀錄 {m.group(1)} 不存在")
            if f"{dotted}.{name}" not in covered:
                failures.append(f"{where}：沒有任何核對區塊驗證這個函式")
            if any(p.kind is not inspect.Parameter.KEYWORD_ONLY for p in inspect.signature(func).parameters.values()):
                failures.append(f"{where}：參數要全部是具名參數（定義用 * 開頭）")
    tests, skipped = run_skill_tests(failures, verbose)
    for s in skipped:
        print(f"略過（需要外部軟體）：{s}")
    for f in failures:
        print(f"失敗：{f}")
    print(f"{functions} 個函式，{blocks} 個核對區塊，{tests} 個技能測試檔，{len(failures)} 個失敗")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
