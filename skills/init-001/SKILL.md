---
name: init-001
title: 建立可由 AI 持續工作的空專案結構（通用、Rhino 繪圖、Rhino 組裝動畫）
summary: "開新專案或替既有資料夾補上 AI 工作規範：三種模式，附結構驗證腳本"
description: init-001：建立可由 AI 持續工作的完整空專案結構，支援通用專案、Rhino 3D／2D 與 CADCraft PDF 交付流程，以及 Rhino 模型編號、JSON／GLB 匯出與組裝動畫流程。開新專案、為既有資料夾補上 AI 工作規範，或重跑檢查結構時使用。
user-invocable: true
type: skill
kind: setup
version: 2.3.1
share: public
atoms: []
points: []
from: []
uses: []
raw: ""
status: draft
updated: 2026-11-14
checked:
---

# init-001 AI 專案初始化

## 目的與完成定義

依本文件在指定根目錄產生完整、可供新專案使用的空結構。空的是專案內容，不是操作流程：文件職責、工作步驟、驗收、交付及更新規則必須已寫好。

初始化完成須同時滿足：

1. 選定模式的所有必要路徑與初始內容均已建立，沒有遺漏或無效連結。
2. 尚無需求、原始碼、模型或繪圖軟體時，仍能完成初始化；不得虛構成果。
3. AI 能從入口找到規範，接收第一個需求，補齊必要資訊，建立計畫，執行、驗收、更新文件及歸檔。
4. 執行本文產出驗收，全部結構檢查通過；未測的外部能力明確列為未驗證。

「100% 產出」指必要清單與驗收項目全部符合，不代表保證任何 AI 或任何軟體環境都無錯誤。不得只憑檔案數量宣稱完成。

本技能是獨立入口，不依賴 frontend init.md、原作者電腦、案例檔案或另一份 init。可直接交給 AI 執行。主版本在知識庫的 `skills/init-001/`；裝到專案裡的是整個技能資料夾的輸出（本文加上 `references/` 的內容契約和 `scripts/` 的驗證腳本，缺一不可），在專案中發現的問題依同資料夾的 references/maintaining.md 帶回主版本。要以 Claude Code skill 使用時，把整個技能資料夾放進專案的 .claude/skills/（用知識庫的 install skill 指令）；同編號已存在時不可另建衝突版本。

## Skill 命名規則

所有新建或重新命名的 skill 統一使用「前綴-三位數」，例如 init-001、rhino-001。

- 前綴使用小寫英文字母，可含數字，用來表示用途或領域；例如 init、rhino、cadcraft。
- 三位數從 001 起算，同一前綴內依序分配，不重複使用；不同前綴各自編號。
- 完整 ID 是唯一識別。frontmatter `name` 與呼叫指令只用編號（`rhino-001`、`/rhino-001`）；標題、說明開頭及引用使用相同 ID，可另附全名。資料夾使用「編號-全名」。
- Skill 資料夾統一為「編號-全名」，例如 `.claude/skills/init-001-ai project init/`、`.claude/skills/rhino-001-rhino script/`，各自內含 `SKILL.md`。全名可包含空格；shell 存取時必須正確引用整個路徑。
- 指令為 /init-001、/rhino-001；只有安裝至對應 host 並確認可用後才列為可呼叫。
- 舊的工作專案裡可能還有單一檔案的 init.md（規格 2.2）；規格 2.3 之後以整個技能資料夾為準，主版本見上方。Rhino 基礎建模 skill 為 rhino-001。
- 新增前先檢查目前可讀取的專案與個人 skills，發現同名衝突先處理，不靜默覆寫。
- 重新命名時同步入口、規則、提醒及腳本識別文字，保留腳本相對路徑與實作。

## 模式與固定選擇

| 模式 | 適用範圍 | 產物 |
|---|---|---|
| general | 通用 AI 專案，包括尚未決定技術的專案 | 共用結構 |
| rhino-cadcraft | Rhino 建立／修改 3D、處理 2D 圖面，CADCraft 檢查排版並輸出 PDF | 共用結構＋繪圖擴充 |
| rhino-animation | 既有 Rhino 建築模型編組、排序、經使用者審核後匯出 JSON／GLB，再做成組裝動畫（例如 React Three Fiber＋Remotion） | 共用結構＋動畫擴充 |

- 使用者指定通用模式時選 general；指定 Rhino、2D／3D 或 CADCraft 時選 rhino-cadcraft；指定動畫、影片、組裝順序展示或 Remotion 時選 rhino-animation；同時要出圖與動畫時，先問主要交付，另一項寫進 PROJECT 的待確認；只要求執行本 init 時預設 rhino-cadcraft，於摘要明示。
- 不要求安裝框架、MCP、Rhino、CADCraft、Node、Remotion 或其他 skill 才能初始化。
- rhino-animation 不建立 Remotion 專案、src、package 或 Composition；既有就保留並記 SHA256。使用 Remotion 時在 PROJECT 記「授權適用身分」（個人、3 人以下公司、非營利或已購公司授權），未確認列待確認，不代為判斷。
- 使用 Codex 等從根目錄 AGENTS.md 讀取指示的 host 時，所有模式另加 AGENTS.md；只用 Claude Code 時不建立。
- init 不寫 MCP 安裝步驟；只盤點是否已連線，未連線標未驗證並繼續。
- Claude Code 使用 .claude/ 適配；其他 AI 從根目錄 README.md 進入 docs，不能假設會載入 Claude 設定。
- 不自動建立應用程式、模型、圖面、虛構任務或範例交付檔。
- Python／C# 建模實作留在實際使用的 skill 或程式中；docs 記錄用途、介面、依賴與限制，不複製整份實作。
- 建模方法預設點→線→面→體，規則寫在 MODELING，不依賴 skill；使用者另有指定才改。rhino-001 是可選輔助，只有已安裝才可載入，不得把未安裝的 skill 列為可用。
- 使用者已指定的工作方式優先；不主動要求換 AI 模型，不把某個模型當初始化依賴。

## Phase 0：唯讀盤點與輸出位置

1. 確認目標根目錄，讀取既有專案指示及 Git 狀態。不隨工作目錄變動重新推算專案根目錄。
2. 盤點 docs、AI 設定、skills、來源與成果；排除 .git/、依賴目錄、快取和二進位內容的全文讀取。
3. general 可由 manifest 偵測技術與指令，只記錄查證到的內容，不要求完整閱讀所有原始碼。
4. rhino-cadcraft 盤點 .3dm、.dwg、.dxf、.pdf、.ctb、.stb、字型或交換資料。Grasshopper 或 plugin 專案記為額外範圍，未授權不擴充。
5. rhino-animation 盤點 .3dm、既有 JSON／GLB、package.json 與 lockfile（Remotion、Three、React Three Fiber 版本）、remotion.config、src 的 Composition、HDRI／貼圖及其授權、已安裝的動畫或排序 skill；既有程式與 skill 記 SHA256，供 I-08 核對。
6. 探查可用工具名稱、說明及 schema；未提供就記未連線。Rhino 有 list_slots 時可先查，只有確認既有實例且不會自動啟動時才查文件摘要。不要為初始化啟動、匯入、修改或關閉文件。
7. 偵測 OS、AI host、shell；版本無法可靠取得時寫「待確認」，不要猜測。
8. 顯示目標路徑、模式、既有衝突及預計產物。已授權初始化即可建立缺檔；只有會覆蓋使用者內容或缺少必要位置資訊才詢問。

### 已有專案與重跑

若使用者明確授權淘汰舊規範，可移除被取代的規則、agents、hooks 及其註冊；先列清單並記錄遷移與驗證。不得把歷史交付或未完成計畫當成舊規範刪除。

- 不因 docs/ 已存在就跳過整個目錄，逐檔處理。
- 缺檔：新增；完全相同：不寫入；使用者已編輯：保留並提供具體差異。
- 不覆寫已填資料，不重置清單、任務、成果或日誌。本文空白初始值只適用於新檔。
- settings 採結構化合併：保留未知欄位，陣列去重；相同 hook 依事件、matcher、type、command、args 去重。不用文字附加 JSON。
- allow／ask／deny 出現同工具衝突時，不自行放寬；保留原設定，列出衝突待處理。
- 無變更重跑不新增日誌、時間戳、hook 或備份。失敗可補缺檔重跑；不遞迴刪除目標目錄。
- 有衝突而未滿足必要內容時，狀態是「部分完成」，不得宣稱完成。

## Phase 1：必要產物清單

### 所有模式

```text
README.md
CLAUDE.md
.gitignore
docs/
  README.md
  PROJECT.md
  ARCHITECTURE.md
  DEVELOPMENT.md
  FEATURES.md
  TESTING.md
  CHANGELOG.md
  INIT-REPORT.md
  FEEDBACK.md
  templates/
    plan.md
    specs.md
    tasks.md
  plans/
    .gitkeep
    archive/
      .gitkeep
.claude/
  settings.json
  rules/
    workflow.md
    delivery.md
  hooks/
    README.md
  agents/
    doc-maintainer.md
    acceptance-reviewer.md
```

### rhino-cadcraft 另加

```text
docs/
  MODELING.md
  DRAWING.md
  DELIVERY.md
.claude/rules/
  drawing-workflow.md
sources/.gitkeep
models/.gitkeep
drawings/.gitkeep
deliverables/.gitkeep
```

### rhino-animation 另加

```text
docs/
  MODELING.md
  ASSEMBLY.md
  ANIMATION.md
  DELIVERY.md
.claude/rules/
  animation-workflow.md
.claude/agents/
  README.md
  animation-reviewer.md
sources/.gitkeep
models/.gitkeep
exports/.gitkeep
public/assembly/.gitkeep
deliverables/.gitkeep
```

### 使用 Codex 時另加

```text
AGENTS.md
```

.gitkeep 為零位元檔。不要建立名稱含 YYYY、feature-name、模型名等假任務資料夾。既有專案使用不同用途目錄時，在 PROJECT 明確映射並保留現況，INIT-REPORT 記錄與預設樹的差異，不搬移成果。

### 全部文件寫入規則

- UTF-8、有效 Markdown、相對檔案連結。檔名不轉成 http://CLAUDE.md 之類網址。
- 不將反斜線跳脫過的 code fence、JSON 括號或 Markdown 連結寫入程式碼。
- 下列逐檔內容契約全部必須落實；可調整語句，不可只建立標題。
- 真正未知資料用「待確認」，不適用用「不適用：原因」，沒有紀錄用「目前無紀錄」。不留 {值}、{專案名稱}、TODO 這類未解析模板。
- 計畫模板可有「待填」，但須說明填寫時機；實際任務不能將待填驗收條件當成通過。
- 專案事實以 PROJECT 為唯一來源，數值不複製到 agents、rules、提醒腳本。
- 初始化完成與專案可以執行不同：未知公差不妨礙空結構完成，但阻擋依賴該公差的建模或驗收。
- 不把這份 init 自身當待填專案文件；本文件的路徑示例、格式示例不是生成產物。

## Phase 2 到 Phase 5：內容契約

每個必要檔案要寫什麼，放在 `references/`。依模式讀對應的檔案，逐檔落實；可以調整語句，不可以只建立標題。

| 階段 | 內容 | 讀哪一份 | 哪些模式要讀 |
|---|---|---|---|
| Phase 2 | 共用文件的內容契約，含階段存檔與續作、變更等級與備份 | [references/contracts-common.md](references/contracts-common.md) | 全部 |
| Phase 3 | 可直接複製的計畫模板（plan、specs、tasks） | 同上 | 全部 |
| Phase 4 | MODELING、DRAWING、DELIVERY | [references/mode-rhino-cadcraft.md](references/mode-rhino-cadcraft.md) | rhino-cadcraft |
| Phase 4B | MODELING、ASSEMBLY、ANIMATION、DELIVERY | [references/mode-rhino-animation.md](references/mode-rhino-animation.md) | rhino-animation（建模方法和 MCP 操作另見 Phase 4 那一份） |
| Phase 5 | .gitignore、settings、rules、agents、hooks | [references/contracts-common.md](references/contracts-common.md) | 全部 |

general 只讀共用那一份，不建立任何模式專用文件。

## Phase 6：產出驗收與第一個任務演練

逐項執行並寫入 INIT-REPORT，不以勾選代替檢查：

| ID | 檢查 | 通過條件 |
|---|---|---|
| I-01 | 必要路徑 | 所選模式清單全存在；空目錄可被版本管理保留 |
| I-02 | 內容契約 | 每份有指定操作內容，非只有標題或未解析佔位符 |
| I-03 | 本地連結 | 實際檔案連結可解析；只有 rhino-cadcraft 連 DRAWING，general 不連任何模式專用文件；無假網址檔名 |
| I-04 | 設定 | JSON parser 可讀 settings；無重複 hook、虛構工具或未解決衝突（rhino-cadcraft 預設規則不算虛構工具） |
| I-05 | 空白語意 | 無假成果、假驗收；未知值有確認時機和影響說明 |
| I-06 | 首個任務 | 下列演練能從 docs 找到完整流程 |
| I-07 | 重跑 | 再比對生成結果，無實際變更則無差異，不重置資料 |
| I-08 | 既有內容 | 既有模型、交付、任務、規格及非本次設定保留 |
| I-09 | 工具與 hooks | 啟用項有實測證據；未連線／未啟用明確記錄，不冒稱可用 |

本技能附 scripts/validate_init.py：`python scripts/validate_init.py <根目錄> --mode <模式>` 檢查必要路徑、零位元 .gitkeep、文件不是空殼、未解析佔位符、本地連結、settings JSON 與模式之間不串連（I-01、I-03、I-04 的機械部分）。I-02、I-05 起仍要逐檔走讀，腳本通過不等於驗收通過。

演練使用隔離暫存位置或文件走讀，不在正式 plans 造假任務、不操作真模型：

- general：「建立新功能，但技術尚未選定」。能找到需求記錄、資訊確認、案件資料是否進 git 的詢問、三份模板、驗收與歸檔步驟。
- rhino-cadcraft：「建立 3D 零件並交付 2D PDF」。能指出建模前需尺寸／單位／公差、2D 前需視圖／比例、出圖前需紙張／樣式；知道建模預設點→線→面→體並保留元素、2D 由模型投影不手描、參考圖只取表達方式，以及兩套軟體責任及證據位置。
- 2D-only：「既有 DWG 排版出 PDF」。直接走 DRAWING／DELIVERY，不強迫建立 3D 或使用 rhino-001。
- rhino-animation：「既有建築模型做組裝影片」。能找到盤點模型與圖層、普通 group 作單元、Rhino 編號後等使用者核准才匯出、同修訂 JSON／GLB、A1 至 A6 的存檔與完成條件、絕對幀數，以及使用者未接受前維持待審查。
- 只改畫面（僅動畫）：「只改背景或運鏡」。依 ANIMATION 重驗畫面與影片，不重編號、不重匯出。
- 無軟體：「只有空資料夾」。完成空結構，外部能力標未驗證，可開始需求與計畫。
- 草圖全流程（僅繪圖）：「從草圖建模並出 PDF」。能指出 D1 至 D6 的工作、存檔位置與完成條件，以及草圖須貼進 Rhino 校正比例、立面與構件範圍須向使用者確認、以規則重建比對殘差而不逐線描、判讀值須先確認。
- 中斷續作：「上次做到一半」。能從 tasks 階段表找到最新存檔點、核對 SHA256，並從第一個未驗收的階段繼續。

走讀只證明流程涵蓋，不等於操作過外部工具。沒有權限檢查檔案或設定時回報未驗證，不宣稱完整驗收。

## Phase 7：完成回報

列出模式、根目錄、建立／保留／衝突摘要、I-01 至 I-09 結果、未驗證能力，以及 docs/README.md 入口。

結構驗收全通過可說：「空結構初始化完成，可以依 docs 接收第一個任務。」另列 Rhino、CADCraft、動畫引擎實際操作未驗證等限制；不要求先做完模型、填完尚未需要的參數或完成 PDF 才算 init 完成。
