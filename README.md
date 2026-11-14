# LLM Wiki 框架

版本 0.4.0，改了什麼見 [`CHANGELOG.md`](CHANGELOG.md)。

一個用純文字和 git 管理的個人知識庫框架，設計給人和 AI agent 一起維護、一起使用。

- 原件（raw）整理成四種頁：筆記（note）、資料（data）、圖（figure）、程式碼（code）。
- 四種頁都依知識點分資料夾，同編號就是同一項；每個知識點有入口 NOTE.md。
- 用多語的原子（atom）把頁串起來，產生索引給 agent 快速檢索。
- 技能（skill）把頁打包成 agent 可以照著做的工作，可以輸出成私人版或公開版，也可以裝進工作專案再把改進帶回來。
- 全部從 `python scripts/wiki.py` 進入，只用 Python 標準庫。

這是空的框架：沒有任何主題、原子或頁，只附一個技能 `init-001`（建立 AI 工作專案的空結構）。

## 開始

```bash
python scripts/wiki.py new wiki <名稱> --kind general --title "主題的標題"
python scripts/wiki.py new plan <英文名稱> --title "第一份原件"
python scripts/wiki.py index
python scripts/wiki.py lint
```

接下來讀：

- 整體設計：[`docs/FRAMEWORK.md`](docs/FRAMEWORK.md)
- 給 agent 的入口：[`AGENTS.md`](AGENTS.md)
- 怎麼查和用：[`USING.md`](USING.md)
- 怎麼新增和維護：[`MAINTAINING.md`](MAINTAINING.md)
- 用語：[`GLOSSARY.md`](GLOSSARY.md)
- 一次做不完的工作怎麼開計畫、怎麼續作：`MAINTAINING.md` 第 10 節

說明文件裡的範例代號（例如 `project-demo`、`bearing-connection`）只是示範，這個空框架裡沒有這些頁。

## 放進自己的內容之前

- 有著作權的原件不進 git（`.gitignore` 已經排除），登記卡要填授權和 `share`。
- 專案的內容放在 `project-` 開頭的主題；repo 要不要公開，取決於你放了什麼。
- 根目錄的 `denylist.txt` 填上不能出現在公開輸出裡的字。
