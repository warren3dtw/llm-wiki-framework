# 文件入口

| 文件 | 用途 |
|---|---|
| [PROJECT](PROJECT.md) | 專案事實、環境與待確認事項的唯一來源 |
| [ARCHITECTURE](ARCHITECTURE.md) | 目錄、資料流與依賴 |
| [DEVELOPMENT](DEVELOPMENT.md) | 接任務、實作、驗收與歸檔流程 |
| [FEATURES](FEATURES.md) | 功能及成果狀態 |
| [TESTING](TESTING.md) | 驗收方法與結果定義 |
| [CHANGELOG](CHANGELOG.md) | 實際變更 |
| [INIT-REPORT](INIT-REPORT.md) | 初始化檢查與未驗證能力 |
| [plan 模板](templates/plan.md) | 目標與範圍 |
| [specs 模板](templates/specs.md) | 可判定規格 |
| [tasks 模板](templates/tasks.md) | 任務、證據與交接 |

新任務：PROJECT → DEVELOPMENT → templates。
續作：[plans](plans/) 中的對應計畫 → specs → tasks 階段表 → 對應規範。
交付：TESTING → 計畫驗收證據 → FEATURES／CHANGELOG。

所有問題與調整記入 [FEEDBACK](FEEDBACK.md)。Task 小調整不備份圖紙／模型；只有 spec 等級變更前備份一次，細則見 DEVELOPMENT。
