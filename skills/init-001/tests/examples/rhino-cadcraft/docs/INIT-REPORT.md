# 初始化驗收報告

- init 規格版本：2.3
- 模式：rhino-cadcraft
- 初次日期：2026-11-05
- 示例根目錄：tests/examples/rhino-cadcraft/（相對於 init-001 技能資料夾；原本在 Rhino-init 的 examples/rhino-cadcraft/）
- 結構初始化：完成（本次產出的示例）
- 外部作業能力：未驗證；未啟動或連接工具
- 既有資料：此為新建隔離示例，不搬移或修改正式專案
- 待確認事項：[PROJECT](PROJECT.md)
- 工作入口：[docs README](README.md)


## 檢查結果

| ID | 結果與證據 |
|---|---|
| I-01 | 通過：逐檔比對必要清單，general 23 檔、rhino-cadcraft 31 檔；.gitkeep 為空檔 |
| I-02 | 通過：逐檔比對 init 的內容契約；包含工作流程、待確認方式、驗收與結案步驟 |
| I-03 | 通過：掃描本地 Markdown 連結並檢查目標存在 |
| I-04 | 通過：JSON parser 可讀設定；Rhino 與 CADCraft CLI 依預設不詢問，其餘權限與空 hooks 沿用 host 機制 |
| I-05 | 通過：無假成果與未解析專案佔位符；計畫模板待填附填寫說明 |
| I-06 | 通過（文件走讀）：PROJECT → DEVELOPMENT → templates → TESTING → FEATURES／CHANGELOG → archive；繪圖另分 3D 與既有 2D 路徑 |
| I-07 | 通過（同輸入比對）：生成內容與磁碟逐檔比較一致，無須重寫；未以另一個 AI 執行第二次生成 |
| I-08 | 通過：在原先不存在的 examples 子目錄建立，未覆寫既有模型、交付或任務 |
| I-09 | 通過（基底狀態）：hooks 未啟用、外部工具未連線，明示未驗證；不代表執行能力已通過 |

## 首個任務走讀

- 未選技術的新功能：先記目標／交付，確認必要選型後建立 plan、specs、tasks。
- 3D 零件轉 PDF：建模前確認尺寸／單位／公差，預設點→線→面→體並保留元素；2D 前確認視圖／比例，由模型投影不手描；出圖前確認紙張／樣式；分別依 MODELING、DRAWING、DELIVERY（僅繪圖模式）。
- 既有 DWG 出 PDF：直接依 DRAWING／DELIVERY，不要求 3D 或額外 skill（僅繪圖模式）。
- 沒有軟體：可整理需求與計畫，依賴軟體的驗收標未執行。
- 草圖全流程：D1 至 D6 各有工作、存檔位置與完成條件；草圖須貼進 Rhino 校正比例、立面與構件範圍須向使用者確認、以規則重建比對殘差，判讀值須先確認。
- 中斷續作：從 tasks 階段表找到最新存檔點、核對 SHA256，從第一個未驗收的階段繼續。

此報告只驗證目前示例與文件走讀，不代表所有 AI 的生成結果或 Rhino／CADCraft 實際作業都已驗證。


## 2.1 調整

新增 FEEDBACK；task 不備份、spec 變更前備份一次；繪圖模式補 Layout 正式出圖與直接 PDF 驗收。未重新操作示例中的外部工具，實測證據保留在正式專案試跑計畫。

## 2.2 調整

新增階段存檔與續作、tasks 階段表；繪圖模式新增草圖起點與 D1 至 D6 全流程階段。新增完成對話任務後自動 commit（不自動 push）；明定 init 不寫 MCP 安裝步驟；繪圖模式預設 Rhino 與 CADCraft 不再詢問，這些工具可執行任意程式碼、覆寫檔案或丟棄未存內容，要恢復詢問時移除 settings.json 對應規則。繪圖模式補 D1 草圖判讀（貼進 Rhino 校正比例、立面向使用者確認、以規則重建比對殘差，不逐線描）與視圖截圖超過回傳上限的案例。開工時詢問案件資料是否進 git（詢問，不預設排除）。全流程後段補建模預設點→線→面→體並保留元素、建模檢查、構件範圍須使用者確認、參考圖只取表達方式、3D 轉 2D 與出圖檢查及版本案例；commit 指令以驗證結果為條件，驗證失敗就中止。文件走讀與文字一致性已檢查，未以 AI 從 init 重新生成，也未實際操作外部工具。

## 2.3 調整

本模式的必要清單與內容契約沒有變更。新增 rhino-animation 模式；使用 Codex 時所有模式另加 AGENTS.md，本示例只用 Claude Code，不建立。I-03 改寫成「只有 rhino-cadcraft 連 DRAWING」，本示例原本就符合。

## 生成清單

- .claude/agents/acceptance-reviewer.md
- .claude/agents/doc-maintainer.md
- .claude/hooks/README.md
- .claude/rules/delivery.md
- .claude/rules/drawing-workflow.md
- .claude/rules/workflow.md
- .claude/settings.json
- .gitignore
- CLAUDE.md
- deliverables/.gitkeep
- docs/ARCHITECTURE.md
- docs/CHANGELOG.md
- docs/DELIVERY.md
- docs/DEVELOPMENT.md
- docs/DRAWING.md
- docs/FEATURES.md
- docs/FEEDBACK.md
- docs/INIT-REPORT.md
- docs/MODELING.md
- docs/plans/.gitkeep
- docs/plans/archive/.gitkeep
- docs/PROJECT.md
- docs/README.md
- docs/templates/plan.md
- docs/templates/specs.md
- docs/templates/tasks.md
- docs/TESTING.md
- drawings/.gitkeep
- models/.gitkeep
- README.md
- sources/.gitkeep
