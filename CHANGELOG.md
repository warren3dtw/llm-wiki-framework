# 框架版本紀錄

框架（腳本、schema、規則、模板、技能層）的版本。只往上追加。版本號寫在 `schema.json` 的 `framework_version`，和這裡最上面一筆要相同，lint 會檢查。

- 主版本：改了檔案格式或欄位，舊的頁要跟著改。
- 次版本：加了新的功能、規則或模板，舊的頁不必改。
- 修正：修錯，行為不變。

知識內容的變動不記在這裡。

## 0.4.0（2026-11-14）

- 多次工作的計畫：`docs/plans/<日期-名稱>/` 和 `templates/plan/` 的 plan、specs、tasks，tasks 有階段與存檔點表。lint 檢查計畫資料夾的三份檔案。
- `docs/FEEDBACK.md` 記框架的問題和調整；本檔記框架的版本，版本號在 `schema.json`。
- `.claude/`：空的權限設定、唯讀的確認助手 `page-reviewer`、hooks 說明（不啟用）。
- MAINTAINING 新增「多次工作的計畫、存檔與 commit」。規則原文寫成知識點 `project-harness` 的筆記，init-001 依據它們。
- `export framework` 帶上版本號、本檔、計畫模板和 `.claude/`；技能依據的頁附在技能的 `references/`。

## 0.3.1（2026-11-14）

- 同編號有幾種頁時，只寫檔名先取筆記並提示其他頁。
- 輸出接到 `head` 時不印錯誤。
- 空框架的名稱替換支援正規表示式。
- `tests/mvp_test.py`：101 項 MVP 測試。

## 0.3.0（2026-11-14）

- 技能層：`skills/<代號>/`，用 `atoms`、`points`、`from`、`uses` 連到知識；`profiles/<專案主題>/` 放專案的慣例。
- 可見度：原件標 `share`，頁和技能用推算的；專案主題一律私人。
- 指令：`new wiki`、`new skill`、`ingest skill`、`export skill`、`install skill`、`export framework`、`query share`。
- 輸出前掃描：禁用字、本機路徑、Email、照抄的原件文字。
- lint：通用主題不能用內文連結或 raw 引用專案主題；依據更新後提醒重看。

## 0.2.0（2026-11-12）

- 改名：原件 raw、原子 atom、筆記 note、資料 data、圖 figure、程式碼 code。
- 四種頁依知識點分資料夾；檔名「知識點-編號-描述」，同編號就是同一項；每個知識點有入口 NOTE.md。

## 0.1.0（2026-11-11）

- 第一版 MVP：依形式分頁、多語原子、索引、ingest、query、fileback、lint、export。
