# 驗收題

機械部分由 `scripts/test_validate_init.py` 自動檢查（三個示例都要通過，壞掉的結構要被抓到）。下面幾題要換一個 agent，只給它 SKILL.md，在暫存資料夾試跑。

## 1. 只說「執行 init」

- 情況：空資料夾，使用者只說「執行 init-001」。
- 應該：選 rhino-cadcraft 並在摘要說明這是預設；產生的結構通過 `validate_init.py --mode rhino-cadcraft`。
- 不應該：建立假的模型、圖面或任務資料夾。

## 2. 要做組裝動畫

- 情況：空資料夾，使用者說「我要把 Rhino 模型做成組裝動畫」。
- 應該：選 rhino-animation；通過 `validate_init.py --mode rhino-animation`；PROJECT 的動畫規格全部是待確認，含動畫引擎授權適用身分。
- 不應該：建立 Remotion 專案或 package.json；產生 DRAWING.md；在 settings 預先允許 npm 或 Rhino。

## 3. 既有動畫專案補結構

- 情況：資料夾裡已經有 package.json、src/ 和一個已安裝的動畫 skill，沒有 docs。
- 應該：保留既有檔案並記 SHA256；ASSEMBLY 連到已安裝的 skill；INIT-REPORT 列出保留的檔案。
- 不應該：覆寫 src/ 或 skill；把沒安裝的 skill 列為可用。

## 4. 同時用 Codex

- 情況：使用者說這個專案也會用 Codex。
- 應該：另建 AGENTS.md，內容和 CLAUDE.md 同一套規則；通過 `validate_init.py --mode <模式> --codex`。
- 不應該：在 AGENTS.md 說 Codex 會讀 .claude/ 的設定。

## 5. 重跑

- 情況：對已初始化而且使用者改過 PROJECT 的專案再跑一次。
- 應該：逐檔比對；已填的資料保留；沒有變更就不新增日誌或時間戳。
- 不應該：重置 PROJECT、FEATURES 或計畫。
