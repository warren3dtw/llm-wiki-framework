#!/usr/bin/env python3
"""知識庫的單一入口。只用標準庫（ingest 的擷取指令另需 poppler、tesseract）。

用法：python scripts/wiki.py <動作> [參數]

  ingest    把原件登記進來，擷取文字和圖          ingest raw|text|page|find|crop ...
            從工作專案把技能帶進來               ingest skill <技能資料夾> [--as 代號]
  query     查詢：找頁、查原子、查資料、追依據      query search|atom|get|data|figure|trace|impact|review ...
  fileback  把查詢得到的答案存回成新的一頁        fileback <主題> <位置> <名稱> --title ... --from ...
  lint      檢查格式、連結、索引，並驗證公式      lint [-q]
  index     重建索引                             index
  export    輸出細部圖集或數據手冊               export atlas|datasheet [--wiki 主題]
            輸出技能（私人版或公開版）            export skill <代號> --public | --profile <專案主題> | --bare
            輸出空框架（不含任何個人內容）        export framework [--out 資料夾]
  install   把技能裝進工作專案                   install skill <代號> <專案路徑> --profile <專案主題> | --public | --bare
  new       建立新的主題、技能或計畫              new wiki <名稱> --kind general|project ／ new skill <代號> ／ new plan <名稱>

每個動作後面不接參數時，會印出它自己的說明。
"""
import os
import sys

ACTIONS = ("ingest", "query", "fileback", "lint", "index", "export", "install", "new")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ACTIONS:
        sys.exit(__doc__)
    action, rest = sys.argv[1], sys.argv[2:]
    sys.argv = [f"wiki.py {action}"] + rest
    if action == "ingest" and rest[:1] == ["skill"]:
        import skilltools
        skilltools.cmd_ingest(rest[1:])
    elif action == "ingest":
        import ingest
        ingest.main(rest)
    elif action == "export" and rest[:1] == ["skill"]:
        import skilltools
        skilltools.cmd_export(rest[1:])
    elif action == "export" and rest[:1] == ["framework"]:
        import framework
        framework.main(rest[1:])
    elif action == "install":
        import skilltools
        if rest[:1] != ["skill"]:
            sys.exit(skilltools.__doc__)
        skilltools.cmd_install(rest[1:])
    elif action == "new":
        import skilltools
        skilltools.cmd_new(rest)
    elif action == "query":
        import query
        query.main(rest)
    elif action == "fileback":
        import fileback
        fileback.main(rest)
    elif action == "index":
        import build_index
        build_index.main(rest)
    elif action == "export":
        import export
        export.main(rest)
    elif action == "lint":
        import lint
        import run_checks
        code = 0
        for step in (lint.main, run_checks.main):
            try:
                step()
            except SystemExit as exc:
                code = code or (exc.code if isinstance(exc.code, int) else 1)
        sys.exit(code)


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        # 輸出接到 head 這類只讀前幾行的程式時，對方先關掉了管線：安靜結束，不印錯誤
        devnull = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull, sys.stdout.fileno())
        sys.exit(0)
