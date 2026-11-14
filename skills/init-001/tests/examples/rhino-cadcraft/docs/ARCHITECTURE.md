# 架構與資料流

| 路徑 | 用途 |
|---|---|
| README.md | 人與 AI 的起點 |
| CLAUDE.md | Claude 工作入口 |
| docs/ | 專案事實、規範、成果與初始化報告 |
| docs/templates/ | 計畫原始模板 |
| docs/plans/ | 任務及驗收證據 |
| docs/plans/archive/ | 完成或取消的完整計畫 |
| .claude/ | 工具設定、規則、角色及 hooks 說明 |

來源供追溯，工作檔供編輯，交付檔保存已產出版本；三者不能混用。

資料流：來源參考（草圖、圖面或資料）→ Rhino 3D → 2D 圖面／DWG → CADCraft 排版與檢查 → PDF。
既有 2D 可直接進入圖面流程，不必建立 3D。3D 變更後重新判斷受影響 2D／PDF，舊驗收不自動沿用。

| 路徑 | 用途 |
|---|---|
| sources/ | 唯讀來源 |
| models/ | Rhino 3D 工作模型 |
| drawings/ | 2D／DWG 工作圖面 |
| deliverables/ | 版本化交付 |
