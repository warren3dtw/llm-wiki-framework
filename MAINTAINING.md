# 維護知識庫（ingest、lint、確認）

給新增、修改頁的 agent 和人。類型和欄位的正式定義在 [`schema.json`](schema.json)，空白樣板在 [`templates/`](templates/)。

## 1. 目錄

```
AGENTS.md  CLAUDE.md  USING.md  MAINTAINING.md  GLOSSARY.md  CHANGELOG.md
schema.json                   類型、種類、必填欄位、必要小節、知識點規則、框架版本
docs/FRAMEWORK.md             整體設計
docs/FEEDBACK.md              框架的問題和調整紀錄
docs/plans/<日期-名稱>/        多次工作的計畫：plan、specs、tasks（第 10 節）；結束後移到 archive/
.claude/                      Claude Code 的設定、唯讀確認助手、hooks 說明
atoms/                        原子（詞條），全部主題共用
skills/<代號>/                 技能，全部主題共用（第 9 節）
  SKILL.md                    本體
  scripts/  tests.md  CHANGELOG.md
  profiles/<專案主題>/          這個專案的慣例、參數、案件經驗（私人）
  profile.example/            去識別化的示範，公開輸出時用
wikis/<主題>/
  WIKI.md                     範圍、種類（general 通用 / project 專案）、工作情境
  inbox.md                    收件匣：待處理、待查證、發現的問題
  raw/                        原件（不進 git）、登記卡 <代號>.md、擷取結果 <代號>/pNNN.txt
  note/<知識點>/NOTE.md         知識點的入口
  note/<知識點>/*.md            筆記
  data/<知識點>/*.md + .csv     資料
  figure/<知識點>/*.md + 影像    圖
  code/<知識點>/*.md + 程式檔    程式碼
calc/                         可執行的公式
templates/                    頁、技能、計畫（plan/）的空白樣板
index/                        索引（wiki.py index 產生，不要手改）
scripts/wiki.py               單一入口；其他 .py 是各動作的實作
build/                        輸出成品（不進 git）
```

## 2. 知識點和編號

- **知識點**依知識領域命名，不依專案或圖紙命名：`bearing-connection`，不是 `s301`。以後別的專案的擱置接合也放進同一個知識點。
- 檔名 `<知識點>-<三位數編號>-<描述>`。**編號全部主題共用一套**：示範案用了 `bearing-connection-001`、`002`，示範案二的下一個擱置接合就是 `003`。查已經用到哪裡：`wiki.py query point <知識點>`。
- **同編號就是同一項**。一個細部的圖和配置表、一個概念的筆記和範例程式，用同一個編號，檔名一模一樣，只差在放在哪一種資料夾。同一種頁裡一個編號只能有一頁；同一項有兩張表時，第二張用新編號，再用 `data` 欄位連起來。
- 檔頭寫 `point`、`item`、`pair`。`pair` 列出同編號的其他頁，兩邊都要寫。
- 每個知識點在每個主題都要有 `note/<知識點>/NOTE.md`，表格列出每一項在四種頁的連結（樣板見 `templates/NOTE.md`）。lint 會檢查它列出了全部的頁。
- 知識點太大時（超過二三十項）再拆。拆的時候要整項改名：資料夾、檔名、`point`、`item`、`pair` 一起改，再用 lint 確認連結。

## 3. 輸入流程（ingest）

```
原件 → 登記 → 擷取 → 起草頁 → 更新 NOTE.md → lint → 擁有者確認
```

1. **登記**：原件放進 `wikis/<主題>/raw/`，執行 `wiki.py ingest raw <主題> <代號> <原件檔名> --kind ... --format ... --lang ...`，寫出含 sha256 的登記卡，再補齊授權（`license`、`share`）、可信度。
2. **擷取**：

   | 原件格式 `format` | 文字怎麼來 | 圖怎麼來 |
   |---|---|---|
   | `pdf-vector` 向量圖說 | `ingest text` 取文字層 | `ingest find` 找標題位置，`ingest crop` 裁切；同時輸出範圍內的文字 |
   | `pdf-text` 排版文件 | `ingest text` | `ingest page` 或 `crop` |
   | `pdf-image` 網頁印成的 PDF、掃描檔 | `ingest text --ocr chi_tra+eng`（日文加 `jpn`） | `crop` |
   | `web` 網頁 | 網頁讀取工具；能存快照就印成 PDF 放進 raw | 截圖 |

3. **起草頁**：從 `templates/` 複製。先決定知識點，再取下一個編號；成對的內容（圖和配置表）用同一個編號。
4. **更新 NOTE.md**：在內容表加一列。
5. **檢查**：`python scripts/wiki.py index && python scripts/wiki.py lint`，零錯誤才算完成。
6. 新頁一律 `status: draft`。

## 4. 每種頁的規則

### 筆記

- 一頁只講一件事，本文 900 字以內（連結網址不算）。
- **不放數據**。要提到數值時連到資料頁；算例的輸入和結果也放資料頁。
- 種類：原理 `concept`、`rule`；做法 `procedure`、`example`；觀點 `claim`、`review`。
- 規則要寫「成立條件」「不適用的情況」；算例要寫「輸入」「結果」；步驟要寫「步驟」；審查一定要用 `against` 指向被審查的頁。

### 資料

- 數據放同名 `.csv`，欄名用英文小寫、數字、底線，單位寫在欄名裡（`t_mm`、`f_mpa`）。
- `## 欄位` 小節逐欄說明意思和單位。
- 原件的錯不改，寫在 `## 轉錄注意` 並記到 inbox。

### 圖

- 影像和 `.md` 同名，放在同一個資料夾。向量 PDF 用 150 dpi 裁切，記 `region_box`。
- 四個必要小節：`圖上原文`（照原件，不翻譯不修正）、`說明`（整理者的中文說明）、`關鍵數據`（連到資料頁）、`適用條件`。
- 細部圖的配置表用**同編號**的資料頁；其他用到的表寫在 `data` 欄位。

### 程式碼

- 程式放同名的程式檔。`verified`：`ran` 實際跑過、`transcribed` 照原件轉錄未執行、`untested`。
- 從圖片轉錄的程式要對照圖片逐字確認；補上去的部分標 `〔待查證〕`。

### 原子

- 檔名用英文小寫加連字號。必填 `name_zh`、`name_en`，有日文就填 `name_ja`；同義詞放 `aliases`，跨語言查詢靠這裡。
- 上下位：`kind-of`（是一種）、`part-of`（是一部分）。

## 5. 可不可以公開（share）

原件登記卡用 `share` 標授權，其他的頁和技能用推算的：

| 值 | 意思 | 例子 |
|---|---|---|
| `public` | 可以公開 | 擁有者自己寫的規格、公開授權的文件 |
| `attribution` | 可以公開，但要標出處並遵守授權條件 | Eloquent JavaScript（CC BY-NC，不得商用） |
| `private` | 不能拿出這個 repo | 專案圖說、付費課程、授權不明的網頁 |

- 原件沒標 `share` 的，一律當成 `private`。lint 會列出還沒標的原件。
- 頁的可見度取它的 `raw` 原件和 `from` 依據裡最嚴格的。專案主題的頁一律 `private`。
- 頁或技能可以自己標 `share`，但只能比推算結果更嚴格，標得比較寬 lint 會報錯。
- 索引的每一行有 `share`，輸出時照它決定放不放。

## 6. 擁有者確認（review）

```bash
python scripts/wiki.py query review --wiki project-demo
python scripts/wiki.py query review --point bearing-connection
```

確認順序是「先確認被依據的」，因為依據沒確認，依據它的頁也站不住：

1. **原件登記卡**：版次、授權、`share`、可信度對不對。
2. **原子**：名稱和定義對不對。被越多頁用到的排越前面。
3. **資料**：對照原件逐列核對，這是最花時間、也最重要的一步。
4. **圖**：圖上原文和原件一致，說明沒有講錯。
5. **程式碼**：跑得動、輸出符合。
6. **筆記**：原理 → 做法 → 觀點。
7. **技能**：依據的頁都確認過；驗收題換一個 agent 試跑過。

實際操作時，以**知識點**為單位最順：打開 `NOTE.md`，照內容表一列一列看，同一項的圖、表、筆記一起確認。確認後由擁有者把 `status` 改成 `reviewed`。

## 7. 主題

- 通用主題不能引用專案主題；專案主題可以引用通用主題。
- 專案的內容要變成通用知識，必須有通用的原件（規範、手冊），在通用主題另寫一頁，不要直接搬。
- 專案主題不記業主名稱、合約金額等機密。

## 8. 公式

- 函式放 `calc/<主題>/`，參數只能用關鍵字，單位寫在參數名稱。
- 說明裡要有 `依據：<頁的代號>`，那一頁要有 ```check 區塊核對這個函式：

  ```check
  {"name": "說明", "calc": "calc/timber/clt.py::design_strength",
   "inputs": {"f_k_mpa": 28.2, "k_mod": 0.8, "gamma_m": 1.25}, "expect": 18.048, "tolerance": 0.001}
  ```

## 9. 技能（skill）

技能是 agent 可以直接載入、照著做的能力包：何時用、規則、步驟、腳本、驗收題。它把筆記、資料、圖、程式碼打包成一件工作的做法。知識點的 NOTE.md 是**知識領域**的入口；技能是**一件工作**的入口，通常會用到好幾個知識點。整體設計見 [`docs/FRAMEWORK.md`](docs/FRAMEWORK.md)。

從 `templates/skill/` 複製整個資料夾到 `skills/<代號>/`。

- **代號**：前綴加三位數（`rhino-002`），等於資料夾名稱和檔頭的 `name`。同一前綴從 001 起算，不重複。輸出成 Claude Code 的技能時，資料夾名稱寫成「編號-全名」。
- **`description`**：agent 靠它判斷什麼時候載入。寫做什麼、什麼時候用，一行，1024 字以內。
- **`version`**：主版本.次版本.修正。改規則升次版本、修錯字升修正、改輸入輸出格式升主版本。每次升版在 `CHANGELOG.md` 寫一筆。
- **關聯**：
  - `atoms`：講到哪些原子。
  - `points`：用到哪些知識點，寫成 `主題:知識點`。`query point` 會列出用到這個知識點的技能。
  - `from`：依據哪些頁，寫完整代號。這些頁改了，lint 標「技能的依據已更新」；重看後不必改就填 `checked`。
  - `uses`：要先用哪些技能。
- **技能本體不能引用專案主題**，和「通用主題不能引用專案主題」同一條規則。專案的圖號規則、編號族、圖層命名、案件經驗、人名，放在 `profiles/<專案主題>/`，那裡面可以連到專案主題的頁。SKILL.md 和 `scripts/` 寫成「見 profile 的 conventions.md」，不寫死；腳本的參數預設值不能是專案的值。
- 一個技能可以有好幾份 profile，一個專案一份。有 profile 就要有 `profile.example/`。
- **規則和步驟**：每條後面註明依據的頁。從工作專案匯入的技能可以先標〔經驗〕，之後再拆成頁。只拆會被兩個以上技能用到、或會被反駁的規則。
- **腳本**：能在一般 Python 跑的邏輯寫 `scripts/test_*.py`，`wiki.py lint` 會執行。只能在 Rhino 等外部軟體裡跑的測試，檔案前三行寫 `# 需要外部軟體`。公式還是放 `calc/`，技能的腳本呼叫它，不另外抄一份。
- **從工作專案匯入**：原檔快照放 `wikis/<主題>/raw/<專案>-<日期>/`，登記卡用 `kind: project`，`edition` 寫專案的 commit。技能的 `raw` 寫 `主題:raw/<代號>, 位置`。案件資料（模型、圖面、交付檔、含案件內容的證據）不放進來。

**技能的指令**

```bash
python scripts/wiki.py new skill <代號> --title "標題"                    # 從模板建立
python scripts/wiki.py ingest skill <工作專案裡的技能資料夾> [--as <代號>]   # 第一次匯入，或帶回改動
python scripts/wiki.py export skill <代號> --public [--draft]              # 公開版
python scripts/wiki.py export skill <代號> --profile <專案主題>             # 私人版
python scripts/wiki.py install skill <代號> <工作專案路徑> --profile <專案主題> [--target codex]
```

- **第一次匯入**：建立 `skills/<代號>/`（`draft`、`share: private`）和一張原件登記卡，並列出掃到的禁用字和本機路徑。名稱不是「前綴-三位數」的用 `--as` 指定。匯入後要做：專案的慣例搬到 `profiles/<專案主題>/`、補 `tests.md`、填 `atoms`、`points`、`from`。
- **帶回改動**：專案裡的技能有 `.wiki-source` 時，差異放到 `skills/<代號>/incoming/<日期>-<專案>/`。照 `DIFF.md` 逐條判斷屬於工具知識、領域知識、慣例還是案件事實，手動併入，升版本、寫 CHANGELOG，再刪掉 incoming 的資料夾並重新 install。lint 會提醒還沒併入的改動。
- **公開輸出的條件**：推算的可見度不是 `private`；`status` 是 `reviewed`（草稿要加 `--draft`，輸出檔會標示）；掃描沒有命中。掃描用根目錄的 `denylist.txt`，加上這個技能每份 profile 的 `denylist.txt`。
- 輸出的 SKILL.md 檔頭只留 Agent Skills 規格的欄位（`name`、`description`、`metadata`），`from` 的頁會整理成 `references/` 裡的檔案。資料夾名稱預設等於代號；要寫成「代號-全名」時在檔頭填 `full_name` 並加 `--folder full`。

**空框架**

`python scripts/wiki.py export framework` 輸出只有程式、規則、模板和 `framework.json` 列出的技能的空框架，並在輸出的資料夾裡執行 index 和 lint、做掃描。`framework.json` 的 `replace` 把說明文件裡的個人和專案名稱換成中性的寫法。新增說明文件或腳本時，如果範例用到新的專案名稱或人名，要同時加進 `denylist.txt` 和 `framework.json`。

## 10. 多次工作的計畫、存檔與 commit

規則原文是知識點 `agent:project-harness` 的五頁筆記（空框架裡附在 `skills/init-001/references/`）。這一節只寫知識庫怎麼套用。

**什麼時候開計畫**：一次對話做不完、或會中斷換人的工作，例如整理一整章原件、匯入或大改一個技能、改框架的腳本或 schema。改幾頁、補別名這類小事不必開。

```bash
python scripts/wiki.py new plan clt-handbook-ch4 --title "CLT 手冊第 4 章"   # 建立 docs/plans/<今天>-clt-handbook-ch4/
```

- 先寫 `plan.md` 的目標、範圍、輸入、待確認，和 `specs.md` 的驗收條件，再開始做。驗收條件寫成指令能判斷的，例如「`wiki.py lint` 0 錯誤」「`query point <知識點>` 列出每一項」。
- **存檔點**：每個階段結束、或中途要停時，在 `tasks.md` 的表更新一列：產出、commit 代號、lint 結果、狀態、下一步。頁都在 git 裡，所以識別碼記 commit，不必逐檔記雜湊值；原件記登記卡上的 sha256。
- **續作**：先讀 `docs/plans/` 裡還沒歸檔的計畫，從 `tasks.md` 第一個不是「已驗收」的階段接著做。表上的 commit 和 `git log` 對不上時，先記進 FEEDBACK 再繼續。
- **變更等級**：在規格內的修改直接改；要改 `specs.md` 時，先記下日期、原因和要重做的驗收。知識庫的檔案都在 git 裡，不另外備份。
- **驗收**：結果只用通過、失敗、未執行、不適用，每一條附指令和證據。頁的 `reviewed` 只有擁有者能設，所以 agent 的驗收最多到「已驗收」，頁維持 `draft`。
- **結案**：`plan.md` 的狀態改成「完成」或「取消」並寫結案，整個資料夾移到 `docs/plans/archive/`。lint 會提醒結束了還沒歸檔的計畫。
- **commit**：整個任務完成而且 lint 通過才 commit，只納入這次的變更，不自動 push。commit 不等於擁有者確認。

**框架的問題和版本**

- 框架本身（腳本、schema、規則、模板、技能層）的問題和調整，記在 [`docs/FEEDBACK.md`](docs/FEEDBACK.md)。知識內容的問題記在各主題的 `inbox.md`。
- 改了框架就在 [`CHANGELOG.md`](CHANGELOG.md) 加一筆，並更新 `schema.json` 的 `framework_version`。lint 會檢查兩者相同。
- `.claude/agents/page-reviewer.md` 是唯讀的確認助手，可以請它照 `query review` 的順序逐頁對照原件，結果由擁有者決定。

## 11. 不要做

- 不改原件，不改 `index/`（用腳本產生）。
- 不把 `status` 設成 `reviewed`，不改擁有者寫的觀點。
- 不重複使用或跳回去用別的主題已經用過的編號。
- 不把付費課程整段搬進來：只留筆記、短程式片段和少量截圖。
- 不把有授權限制的內容（專案圖說、付費課程）放到公開的地方。
- 不新增類型或欄位，除非先改 `schema.json` 並說明原因。
- 不在技能本體（SKILL.md、scripts/）寫專案的名稱、圖號、人名或本機路徑，放 profile。
- 不把 `share` 標得比推算結果寬。
- 不在驗證失敗或任務沒做完時 commit，不自動 push。
