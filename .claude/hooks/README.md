# Hooks

目前沒有啟用任何 hook，`settings.json` 的 `hooks` 是空的，這是有效的狀態。

- hooks 是自動化機制，AGENTS.md、MAINTAINING.md 是行為規則，兩者不同：寫在規則裡的事情不會因為有 hook 才被遵守。
- 要啟用前，先確認 host 的事件名稱和參數、作業系統、腳本位置和輸出；腳本不存在就不要註冊。
- 適合的例子：修改 `wikis/`、`atoms/`、`skills/` 之後自動執行 `python scripts/wiki.py index`。啟用時要實際寫出腳本，並用模擬輸入測試過。
- 不用 hook 擋 `git push` 或改全域設定。
