# init-001 內容契約：所有模式

由 [SKILL.md](../SKILL.md) 的 Phase 2 到 Phase 5 指過來。所有模式都要讀這一份；rhino-cadcraft 另讀 [mode-rhino-cadcraft.md](mode-rhino-cadcraft.md)，rhino-animation 另讀 [mode-rhino-animation.md](mode-rhino-animation.md)。

## Phase 2：共用文件內容契約

### README.md

標題使用已知專案名，未知時取目標資料夾名稱。寫明「此專案已建立 AI 工作空結構，尚未建立功能或交付成果」。既有專案則按盤點結果描述，不宣稱空白。

快速開始必須包含以下有效連結及步驟：

1. 閱讀 docs/PROJECT.md，提供目標與交付要求。
2. AI 依 docs/DEVELOPMENT.md 確認本次必要資訊。
3. 使用 docs/templates/plan.md 建立第一個計畫。
4. 依 docs/TESTING.md 執行並記錄證據。
5. 文件總入口為 docs/README.md。

附可用的首個任務說法：「請依 docs 工作，先整理我的需求及待確認事項，再建立計畫；我的目標是……」。說明無軟體連線仍可進行需求與計畫整理。

### AGENTS.md（使用 Codex 時）

和 CLAUDE.md 同一套規則與連結，給從根目錄讀 AGENTS.md 的 host。寫明 .claude/ 是 Claude Code 適配，不假設其他 host 會載入；skills 表只列這個 host 實際辨識到的項目，未確認寫「是否辨識待確認」。動畫模式的 skill 若放在 .agents/skills/，以實際路徑登記。

### CLAUDE.md

保持精簡，但包含以下規則及有效相對連結：

- 專案模式與目的讀取 docs/PROJECT.md。
- 每次開始先讀 docs/README.md、PROJECT.md、DEVELOPMENT.md；續作再讀當前計畫三份文件。
- 先補本次必要資訊，再執行；不得猜測指令、尺寸、公差、版本或工具名稱。
- 變更前記錄規格與任務，修改後驗收，未執行的檢查不得標通過。
- 成果存新版本，來源不覆寫；完成時同步 FEATURES、CHANGELOG 與計畫。
- 完成整個對話任務後自動 commit 本次變更，不自動 push；細則見 DEVELOPMENT。
- rhino-cadcraft 另讀 MODELING、DRAWING、DELIVERY。
- rhino-animation 另讀 MODELING、ASSEMBLY、ANIMATION、DELIVERY，並寫明「先在 Rhino 編號，使用者核准後才匯出」。
- Skills 表只列實際可用的名稱、路徑、用途；若無則寫「未登記；本空結構不依賴額外 skill」。
- 文件索引連到 docs/README.md；不重複數值或完整規範。

### docs/README.md

索引表逐一連結 PROJECT、ARCHITECTURE、DEVELOPMENT、FEATURES、TESTING、CHANGELOG、INIT-REPORT、FEEDBACK 和 templates，解釋各自用途。繪圖模式另加三份專用文件；動畫模式另加 MODELING、ASSEMBLY、ANIMATION、DELIVERY 四份。

提供工作入口：
- 新任務：PROJECT → DEVELOPMENT → templates。
- 續作：plans 中對應計畫 → specs → tasks 階段表 → 對應規範。
- 交付：TESTING → 驗收證據 → FEATURES／CHANGELOG。

### docs/PROJECT.md

建立「項目｜目前值｜來源／確認方式」表；已知才填，其餘寫待確認：

- 專案名稱（可取根資料夾名）、模式、目標、範圍、不包含事項。
- 最終交付、驗收方式、驗收人／角色、進度（新專案為尚未開始）。
- OS、AI host、技術／軟體版本、工具連線與操作入口、可用指令及證據。
- 來源目錄、工作目錄、交付目錄、命名與版本規則、案件資料是否進 git（開工時詢問，不預設排除）。
- 專案規格狀態：未確認／已確認；未知值不是預設值。

附待確認事項表：ID、問題、影響的工作、何時必須確認、狀態。尚無具體任務時記錄「開始首個任務前確認目標與交付」即可，不要求先填完所有未來可能需要的資料。

繪圖模式增加：Rhino 版本、Rhino MCP 實作／版本、CADCraft 版本與操作方式、單位、絕對公差、角度公差及其單位、座標原點、建模策略、2D 來源方式、DWG 交換版本、圖層對應、紙張／方向、模型與出圖比例、字型、CTB／STB、色彩、PDF 頁數與排序。建模策略初始值寫「點→線→面→體（預設，見 MODELING）」，不列為待確認。

動畫模式增加：Rhino 版本、Rhino MCP 實作／版本、單位、圖層路徑結構（分區、樓層、類別各在第幾層）、排序優先（樓層優先或分區優先）、組裝單元規則（預設普通 group）、交換資料格式與 schema 版本、動畫引擎與版本（例如 Node、Remotion、Three、React Three Fiber）、動畫引擎授權適用身分、Composition ID、畫面比例與像素、fps、每步幀數、尾段幀數、背景／HDRI 與授權、正式影片 codec。動畫引擎未選定時寫待確認，不預設 Remotion。

繪圖預設目錄 sources/、models/、drawings/、deliverables/。動畫預設目錄 sources/、models/、exports/、public/assembly/、deliverables/；out/ 只放測試影片。其餘工程數值不設通用預設。建模前確認單位與公差；形成 2D 前確認投影／剖面及比例；出 PDF 前確認紙張、樣式、字型及驗收要求。

### docs/ARCHITECTURE.md

列出實際目錄用途：docs 保存規範與事實、plans 保存任務與證據、.claude 保存工具適配；來源、工作檔、交付檔分工清楚。

general 初始資料流：「需求 → 規格 → 實作／作業 → 驗證 → 交付」。技術架構寫「尚未選定；首次選型時記錄組件、資料流、外部依賴與決策理由」。不憑空填 API、DB 或框架。

繪圖資料流：「來源參考（草圖、圖面或資料）→ Rhino 3D → 2D 圖面／DWG → CADCraft 排版與檢查 → PDF」。允許既有 2D 直接進入圖面流程，不必為 2D 任務製造 3D。3D 變更後重新判斷受影響的 2D 與 PDF，舊驗收不自動沿用。

動畫資料流：「需求 → plan／specs／tasks → Rhino GUID 與圖層盤點 → group 組裝單元 → Rhino 編號 → 使用者核准 → 同修訂 JSON＋GLB → 場景 → 逐格渲染 → 影片與配套驗收」。表列 sources、models、exports、public/assembly、src（既有才列）、out、deliverables 的用途。上游 group、GUID、幾何、圖層或排序規則變更使排序審核與下游驗收失效；只改運鏡或背景不必重編號，但要重驗畫面。

### docs/DEVELOPMENT.md

完整寫入以下日常流程：

1. 讀入口與專案資料；續作先定位既有計畫，不重建相同任務。
2. 區分已知需求與待確認資訊，只詢問影響本次操作的缺口。無法執行時可先做獨立的規格整理。
3. 複製 templates 三份文件到 docs/plans/YYYY-MM-DD-簡短名稱/；同日同名加流水號，日期使用當地實際日期。
4. plan 記目標／範圍；specs 每條規格編 S-001 等 ID，寫可判定驗收；tasks 每項關聯 spec ID。
5. 開始前確認來源、工作位置、工具、規格及案件資料是否進 git；依任務執行並更新 tasks。
6. 驗收記錄命令或操作、來源版本、預期、實際、證據位置及結果。失敗、未測、不適用分開。
7. FEATURES 更新成果與已知問題；CHANGELOG 記重要變更。待使用者驗收時設「待審查」，不提前標完成。
8. 符合規格並取得要求的驗收後，plan 設完成，整個資料夾移至 archive；取消則記原因日期再歸檔。修正相對證據連結。

命名：文件與計畫使用可讀名稱；交付初始命名規則為「名稱_vNN.副檔名」，實際專案可在 PROJECT 調整。版本選未使用的新值，不覆寫；最高版本不自動等於已核准版本。

變更規格先更新 specs 與影響項目，再重做相關驗收。未授權不擴充範圍，不自動 push 或更動全域 AI 設定。

完成整個對話任務後自動 commit：只納入本次任務的變更，不含無關或來源不明的變更及敏感資料；沒有變更就不 commit。任務未完成或驗證失敗時不 commit，先回報。commit 指令要以驗證結果為條件，驗證失敗就中止（驗證工具不以退出碼回報失敗時，指令要自行判讀結果），不先提交再補救。commit 不代表驗收，待審查項目仍維持待審查。

開工時確認案件資料是否進 git：首次加入實際來源、工作檔或含其內容的證據前，先問使用者。這是詢問，不是預設排除；答案記入 PROJECT。決定不進 git 才把對應路徑加入 .gitignore，這些檔案沒有 git 版本歷史，階段存檔依磁碟與 SHA256；倉庫會公開時，追蹤的文件也不寫案名與客戶資料。未答覆前這些檔案先不納入 commit，也不寫入 .gitignore。專案不用 git 時不適用。

## 階段存檔與續作

工作可能跨多次對話，每個階段結束都要留下可接續的狀態。tasks 的「階段與存檔點」是進度的唯一來源。

- 建立計畫時在 tasks 列出階段，每階段對應 spec ID，並有輸入、輸出和完成條件。
- 存檔點四項缺一不可：工作檔已存到專案路徑；確認磁碟上的檔案存在並記 SHA256；記輸入來源版本與工具版本；寫下一步。軟體內未存的內容不算保存。
- 中途要停時同樣先存檔，階段維持「進行中」，並在下一步寫清楚做到哪裡。
- 狀態限未開始、進行中、已存檔（已保存但未驗收）、已驗收、需重驗。不適用的階段標不適用並寫原因。
- 上游產物變更時，下游已驗收的階段改為「需重驗」，舊驗收不沿用。
- 續作先核對表內 SHA256 與磁碟一致，不一致先記 FEEDBACK 並確認原因；再從第一個不是「已驗收」的階段繼續，不重做已驗收階段。同一工作檔跨階段時，只核對最新一列。
- 存檔點不是備份：各階段產物本來就是不同檔案或同一工作檔的正常存檔，不為此多複製；備份仍依下節。階段存檔本身不觸發 commit；commit 時機依對話任務完成的規則。

## 變更等級與備份

- **Task 等級**：在已確認 specs 範圍內完成任務、修正錯誤、微調排版／文字位置、調整實作；不改需求、範圍或驗收條件。直接修改工作圖紙／模型並正常存檔，不預先複製、不產生備份版本，也不逐 task 備份。
- **Spec 等級**：改變已確認需求、尺寸／單位／公差、交付範圍或驗收條件。先更新 specs 並記錄影響，再於第一次實際變更前備份受影響的工作圖紙／模型一次；記錄備份路徑、來源版本與原因，同一批 spec 變更下的 tasks 不重複備份。
- 任務關聯 S-001 等 spec ID、修改 tasks 勾選或修正文句不會自動升為 spec 等級。依實質變更判定；確實改變規格才備份。
- Task 沒有工作檔時可建立完成工作所需的檔案；若來源為不可覆寫的交付檔，建立一份工作檔供後續持續修改，這是工作輸入，不額外產生備份。不得藉此為每個 task 複製檔案。
- 正式交付維持新版本、不覆寫已發布成果；這是交付版本，不是作業前備份。沒有正式交付需求的小調整，不強制另存新版本。
- 每個問題與調整仍寫 FEEDBACK：變更等級、判定理由、影響規格／任務、是否備份（task 填「不需要」）、修改內容及驗證結果。規格新建且尚無工作檔時填「無可備份工作檔」，不製造空備份。


將以上階段存檔與備份規則完整寫入 DEVELOPMENT.md；MODELING、DRAWING、rules 與 agents 引用並遵守，不另立每次修改都備份的要求。

### docs/FEATURES.md

標題「功能與成果清單」。初始文字「目前無功能或成果紀錄；實際建立後新增，不把模板示例列為成果」。

空表欄位：ID、名稱、用途、來源／計畫、產物路徑與版本、狀態、驗收證據、已知問題。狀態限未開始、執行中、待審查、已接受、已取消。既有且僅盤點到的檔案註明驗收狀態待確認。正式成果補一段行為或內容描述。

### docs/TESTING.md

定義通過、失敗、未執行、不適用四種結果。無證據不得通過；不適用附理由。

每項任務至少驗證：來源正確、規格逐項對應、產物存在且可開啟、未修改受保護來源、文件與成果版本一致。驗收記錄寫在計畫 tasks 的驗收表，不編造測試命令。

general：無執行環境時標未執行；選定技術後新增實際指令、前置條件與預期結果。「沒有測試」不是通過。

繪圖另加：幾何有效性、尺寸／公差、按用途要求的封閉性、隱藏／重複物件、DWG 重開檢查、PDF 頁數／尺寸／順序／裁切／字型／線寬／色彩。截圖不能替代數值或幾何檢查。草圖校正與 pattern 疊圖要有殘差數值，立面型式與構件範圍要有使用者答覆。3D 轉 2D 的線數與視埠比例要有數值，細則見 DRAWING。常見陷阱至少含重複匯入、隱藏物件漏查、截圖空白先查 metadata、模型單位與出圖比例混淆、字型替代、標註縮放、CTB 差異、未校正比例就依草圖建模、逐線描潦草草圖及把參考圖當規格。

動畫另加：排序核准證據、JSON 與 GLB 的 GUID 雙向對應、組內相對位置與最終姿態等於原模型、bounds 與單位方向、任意跳格同姿態、素材載入失敗會中止渲染、代表幀與短片、正式影片的 codec／尺寸／fps／幀數／時長。只讀程式不能宣稱畫面通過；build 產生 bundle 不等於影片。常見陷阱至少含漏查隱藏或鎖定物件、重疊或跨樓層 group 被自動合併、用累積 delta 或未固定亂數算動畫、JSON 與 GLB 混用修訂、審查用低精度網格被當成正式交換資料。

### docs/CHANGELOG.md

使用實際日期，首項記「建立 <模式> AI 工作空結構」，模式為 general、rhino-cadcraft 或 rhino-animation。不寫虛構功能成果。既有日誌保留，只在實際初始化變更時補一筆。

### docs/FEEDBACK.md

記錄所有問題與調整，不論是否發生錯誤。每項包含 ID、日期／計畫、預期與實際、證據、影響、原因確定程度、task／spec 等級及理由、備份路徑或不需要、調整內容及文件、驗證結果、狀態／下一步。無紀錄時明示目前無紀錄；關閉後保留。共通改法同步 init、示例與正式規範，個案資料只記 PROJECT 或計畫。

### docs/INIT-REPORT.md

記錄 init 規格版本 2.3、模式、目標根目錄（供人查看，不硬編碼入可攜設定）、初次日期、生成／保留／衝突檔案、逐項驗收結果、未驗證外部能力及下一個工作入口。

分開呈現「結構初始化：完成／部分完成」及「外部作業能力：已驗證／未驗證／不適用」。未知公差不算結構失敗，但必須能找到 PROJECT 的待確認事項。

## Phase 3：可直接複製的計畫模板

將下列三個 code block 分別寫入指定檔案，不填虛構實際計畫。

docs/templates/plan.md：

```markdown
# 計畫

狀態：草稿
建立日期：待填（建立實際計畫時必填）
完成／取消日期：不適用（結束時填寫）

## 使用者需求與目標
待填：誰需要什麼結果，以及為何需要。

## 範圍與不包含事項
待填：本次交付和不處理項目。

## 來源與依賴
待填：來源路徑／版本、工具與前置條件；沒有則寫無。

## 待確認與決策
待填：列出會阻擋執行的問題；沒有則寫無。

## 規格與任務
- [規格](specs.md)
- [任務及證據](tasks.md)

## 結案
尚未結案。完成時記錄驗收結果；取消時記錄原因。
```

docs/templates/specs.md：

```markdown
# 規格與驗收

開始執行前填寫；每條規格有唯一 ID。數值、單位和判定方式明確，不使用「看起來正常」作唯一條件。

| ID | 要求 | 輸入／輸出 | 驗收方法與通過條件 |
|---|---|---|---|

目前無規格。實際計畫從 S-001 開始新增。

## 規格變更
目前無變更。變更時記日期、原因、受影響任務及需重做的驗收。
```

docs/templates/tasks.md：

```markdown
# 任務與驗收證據

目前無任務。建立任務時使用核取方塊，標註任務 ID 與對應 spec ID；完成後才勾選。

## 階段與存檔點
| 階段 | Spec ID | 輸入與來源版本 | 輸出路徑 | SHA256 | 工具版本 | 狀態 | 下一步 |
|---|---|---|---|---|---|---|---|

目前無階段。建立計畫時列出階段；每階段結束或中途要停時更新本表，規則見 DEVELOPMENT。

## 任務

## 驗收記錄
| Spec ID | 操作／命令 | 輸入與產物版本 | 預期 | 實際 | 結果 | 證據路徑 |
|---|---|---|---|---|---|---|

目前尚未驗收。結果限通過、失敗、未執行、不適用；不適用須寫原因。

## 問題與交接
目前無紀錄。續作時記錄下一步、阻塞及已知問題。
```

## Phase 5：AI 適配、rules、agents 與 hooks

### .gitignore

追加缺少規則，保留原內容：

```gitignore
.claude/settings.local.json
.env
.env.*
!.env.example
```

繪圖另加 *.3dmbak、*.rhl。動畫另加 *.3dmbak、*.rhl、node_modules/、out/、__pycache__/、*.pyc；既有 package 的建置產物依它原本的設定。models/、exports/、public/assembly/、deliverables/ 不預設忽略，依 DEVELOPMENT 開工時詢問。不預設忽略模型、DWG、PDF 或套件 lockfile。大型二進位管理策略待專案決定，不自行啟用 Git LFS。使用者決定案件資料不進 git 時才追加對應路徑（見 DEVELOPMENT）；個案路徑不寫進空結構。

### .claude/settings.json

general 全新空結構有效基底：

```json
{
  "permissions": {
    "allow": [],
    "ask": [],
    "deny": []
  },
  "hooks": {}
}
```

這代表沿用 host 權限機制，不代表允許所有操作。不寫全域設定、不放寬 host 政策、不停用 sandbox；除下述 rhino-cadcraft 預設外，不預先允許任意程式碼。

rhino-cadcraft 預設 Rhino 與 CADCraft 都不再詢問，全新空結構的基底改為：

```json
{
  "permissions": {
    "allow": [
      "mcp__rhino",
      "Bash(*cadcraft-cli* *)",
      "PowerShell(*cadcraft-cli* *)"
    ],
    "ask": [],
    "deny": []
  },
  "hooks": {}
}
```

`mcp__rhino` 涵蓋整組 Rhino 工具，尚未連線時不生效。CADCraft CLI 的規則比對指令文字，不綁安裝路徑；指令中要直接寫出 cadcraft-cli，存成變數再呼叫不會符合。這些工具可執行任意程式碼、覆寫檔案或丟棄未存內容，也可能符合檔名含 cadcraft-cli 的其他指令，INIT-REPORT 須列明此風險；使用者要求恢復詢問時移除對應規則。

CADCraft 若另有 MCP，依當前 schema 查到實際名稱後加入 allow，不先寫不存在的名稱。其他工具未連線時不註冊，記錄後續啟用流程：連接工具、讀 schema、確認行為、合併設定、測試；不妨礙結構完成。

rhino-animation 使用 general 的空基底，不預先允許 Rhino、node 或 npm 指令。使用者要求免詢問時，依當前 schema 加入實際名稱，並在 INIT-REPORT 列風險。

sandbox 能力依 host 版本確認，不跨平台複製設定，不主動詢問是否放寬程式碼權限。

### Rules

全部不設 paths：工作流程和 MCP 不一定觸發檔案載入。正文使用專案根相對路徑說明，若用 Markdown 連結需依所在檔案修正：

- workflow.md：讀 PROJECT／DEVELOPMENT；規格先於執行；未知不是預設；開工時詢問案件資料是否進 git，不預設排除；驗收需證據；續作讀 plans 並從 tasks 階段表接續；每階段留存檔點；結束同步與歸檔；完成整個對話任務後自動 commit 本次變更，不自動 push。
- delivery.md：來源不覆寫、交付新版本、先確認路徑與未使用版本、待審查不得標已接受；依 TESTING 驗收。繪圖與動畫另連 DELIVERY；動畫另寫 JSON／GLB／設定／影片同修訂並記 SHA256，bundle 不等於影片。
- drawing-workflow.md（僅繪圖）：確認實例、文件與工具行為，讀 MODELING／DRAWING／DELIVERY；每階段留存檔點並記來源版本；草圖一定要貼進 Rhino 校正比例，立面向使用者確認，以規則重建比對殘差、不逐線描，細則見 DRAWING 的 D1；不複製模型數值到規則。
- animation-workflow.md（僅動畫）：操作 Rhino 前定位實例與文件並核對工具 schema，讀 MODELING／ASSEMBLY／ANIMATION；普通 group 作單元，重疊或跨樓層待釐清；先編號，使用者核准後才匯出；鋼木相依只提建議；逐格以絕對幀數計算，保持 GUID／單元對應、組內剛性與終態；上游變更撤回下游驗收；未要求不輸出影片。不複製製片數值到規則。

### Agents

固定建立兩個文件角色，建立不代表自動委派。以下 frontmatter 原樣寫入，再加上指定正文。

doc-maintainer.md：

```yaml
---
name: doc-maintainer
description: 根據已查證的任務結果維護 docs，整理待確認事項與交接。
tools: Read, Glob, Grep, Write, Edit
---
```

正文要求：先讀 PROJECT、DEVELOPMENT 及相關計畫；只寫已查證事實；區分未測與通過；維護 FEATURES、CHANGELOG、索引；不修改模型、交付檔或工具設定。工具／版本無來源記待確認。數值只維護 PROJECT。

acceptance-reviewer.md：

```yaml
---
name: acceptance-reviewer
description: 依 specs 與 TESTING 唯讀審查驗收證據，列出缺口與待確認事項。
tools: Read, Glob, Grep
---
```

正文要求：逐條比對 spec、版本及證據；回報 spec ID、結果、證據和缺口；不因勾選或檔名存在宣告通過；無法讀二進位時承認限制，不宣稱驗證過幾何或 PDF 畫面；不修改檔案。

不固定 model、color。Rhino 操作由主流程完成；確有需要才增專用 agent，其工具須足以完成狀態查詢、定位和驗證。

rhino-animation 另建 animation-reviewer.md：

```yaml
---
name: animation-reviewer
description: 唯讀審查組裝單元、逐格時序、運鏡與畫面驗收證據。
tools: Read, Glob, Grep
---
```

正文要求：先讀 PROJECT、DEVELOPMENT、ASSEMBLY、ANIMATION 與任務規格；核對 group 單元規則、GUID 對應、核准關卡、絕對幀數與素材載入等待；依證據檢查運鏡、終態與修訂一致；回報 spec ID、證據與待補代表幀；不能只讀程式就宣稱畫面、陰影、HDRI 或 GPU 渲染通過；不操作 Rhino、不修改檔案，不推定結構或施工安全。

rhino-animation 另建 .claude/agents/README.md：角色表（名稱、用途）；寫明建立角色不代表自動委派；Rhino 寫入與動畫製作由主流程負責，避免多個 agent 同時修改作用中文件；角色不能取代使用者的順序核准。

維護 init 來源的倉庫可另設 init-maintainer，把可通用的回饋併入 init 與示例；它不屬於必要產物，不生成到新專案。

### Hooks

必要檔 .claude/hooks/README.md 必須寫明：

- 空結構預設未啟用 hook，settings 的 hooks 為空是有效狀態。
- hooks 是自動化機制，rules 是行為指示，不可混稱強制保護。
- 啟用前確認 host 事件／參數、OS、執行環境、腳本位置及輸出；不存在腳本不註冊。
- 交付保護從固定根目錄或腳本位置解析交付位置，不用隨 cd 改變的 cwd 當根目錄。
- 相對路徑基準必須與工具一致，未確認則要求絕對路徑。測試根目錄、子目錄、空白／中文路徑、新檔及既有檔。
- 只攔截 save_doc 的 hook 無法保護 run_command、腳本或 CADCraft 寫檔，須列明範圍；其他操作仍依權限與流程檢查。
- Compact 提醒讀既有入口或規範，不另存公差副本。
- 格式化、測試與通知只有具備實際命令且需要時才啟用，不虛構命令或改全域通知。

既有 hook 不因重跑而刪除／停用；缺腳本、錯路徑或權限衝突寫入 INIT-REPORT，修復後驗收。使用者要求可執行 hook 時，必須實際產生腳本並用模擬輸入測試，不可只交 README。這是按能力啟用的擴充，不改變基底必要檔案清單。
