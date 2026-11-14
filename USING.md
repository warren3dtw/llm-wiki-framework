# 使用知識庫（query、fileback、export）

給要查資料、回答問題、做計算、輸出成品的 agent 和人。查詢時不修改既有的頁；發現錯誤寫進該主題的 `inbox.md`。

## 1. 先看索引，再開檔

| 順序 | 讀什麼 | 得到什麼 |
|---|---|---|
| 1 | [`index/OVERVIEW.md`](index/OVERVIEW.md) | 有哪些主題、知識點，各有多少頁 |
| 2 | 知識點的入口 `note/<知識點>/NOTE.md`，或 `python scripts/wiki.py query point <知識點>` | 這個知識點有哪些項目、閱讀順序 |
| 3 | `python scripts/wiki.py query search <關鍵字>`，或篩 `index/catalog.jsonl` | 跨知識點找頁 |
| 4 | `python scripts/wiki.py query get <代號>`，或打開索引裡的 `path` | 說明文字 |
| 5 | 頁的附帶檔（索引裡的 `file`）：資料的 `.csv`、圖的影像、程式檔 | 數據、圖、程式本身 |

不要一開始就掃過所有檔案。`index/points.json` 列出每個知識點的每一項在四種頁的代號。

## 2. 結構

```
wikis/<主題>/
  note/<知識點>/NOTE.md                       入口：知識點是什麼、各項目、閱讀順序
  note/<知識點>/<知識點>-001-<描述>.md          筆記
  data/<知識點>/<知識點>-001-<描述>.md + .csv   資料（同編號 = 同一項）
  figure/<知識點>/<知識點>-001-<描述>.md + .png 圖
  code/<知識點>/<知識點>-002-<描述>.md + .js    程式碼
  raw/                                        原件和登記卡
atoms/                                        原子（詞條），全部主題共用
skills/<代號>/SKILL.md                         技能：agent 可以照著做的能力包，全部主題共用
```

**技能**（skill）不是第五種頁，是把頁打包成一件工作的做法：何時用、規則、步驟、腳本、驗收題。要做一件有技能的工作時，先讀 SKILL.md 照著做；專案的慣例在技能的 `profiles/<專案主題>/`。`index/OVERVIEW.md` 的「技能」一節列出全部技能。整體設計見 [`docs/FRAMEWORK.md`](docs/FRAMEWORK.md)。

| 類型 | 存什麼 | 數據在哪 |
|---|---|---|
| 筆記 | 原理（概念 concept、規則 rule）、做法（步驟 procedure、算例 example）、觀點（主張 claim、審查 review） | 不放數據，連到資料頁 |
| 資料 | 所有數據：係數、配置表、參數、結果、對照表 | 同名 `.csv` |
| 圖 | 細部圖、圖面、示意圖、截圖。圖上原文、說明和圖放在一起 | 影像檔；圖上的數據在資料頁 |
| 程式碼 | 程式片段、設定檔、提示詞 | 同名程式檔 |

**頁和頁的關聯**，寫在檔頭：

| 欄位 | 意思 |
|---|---|
| `point` | 知識點，等於資料夾名稱 |
| `item` | 項目：知識點-編號。編號全部主題共用一套 |
| `pair` | 同編號的其他頁（例如細部圖 ↔ 它的配置表） |
| `data` | 用到哪些資料頁（可以跨知識點） |
| `from` | 依據哪些頁 |
| `against` | 反駁或審查哪些頁 |
| `atoms` | 講到哪些原子 |
| `raw` | 原件和位置 |

代號寫成 `<主題>:<類型>/<檔名>`，例如 `project-demo:figure/bearing-connection-001-demo-fj2-bearing-on-wall`。同一個主題裡可以省略主題。

## 3. 查詢（query）

```bash
python scripts/wiki.py query point bearing-connection              # 一個知識點：每一項在四種頁的位置
python scripts/wiki.py query search 搭接                            # 中文
python scripts/wiki.py query search "lap joint"                     # 英文，找到同一批
python scripts/wiki.py query search 相欠き --all                      # 日文，連專案一起查
python scripts/wiki.py query search 螺絲 --type data --kind schedule --all
python scripts/wiki.py query search 撓度 --group 觀點 --all           # 只找觀點（審查意見）
python scripts/wiki.py query atom 自攻木螺絲                          # 各語言名稱、下位原子、用到它的頁
python scripts/wiki.py query data panel-joint-001-demo-fj1-lap-joint t_mm=160   # 依欄位條件查
python scripts/wiki.py query trace clt-roof-panel-check-005-demo2-clt150-deflection-review
```

- 關鍵字會透過原子展開：查「螺絲」會連「全牙螺絲」「半牙螺絲」一起找到。多個關鍵字是「而且」。
- **專案主題預設不查**。問題提到專案，或要找實際案例時，加 `--all` 或 `--wiki project-demo`。
- 同一個知識點可以同時出現在通用和專案主題（例如 `clt-stiffness-deflection` 在 timber 和 project-demo2），編號接續。
- 只寫檔名時，同編號的筆記和程式碼檔名相同，要寫出類型，例如 `note/closure-001-closure`。

## 4. 引用

- 每頁都追得到原件的位置：`query trace <代號>`。
- 回答時附上頁的代號和原件位置。
- `status: draft` 的頁要說「尚未經擁有者確認」。圖上原文是原件的文字，說明是整理者寫的，兩者不要混著引用。
- `origin: fileback` 的頁是先前查詢後回存的答案；引用時一併說明，並看它的 `from`。
- 專案的數值只適用那個專案。通用問題不要拿專案值當答案；可以當作例子，並說明是哪個專案。
- 引用原理或做法的結論前，用 `query impact <代號>` 看有沒有觀點反駁它。

## 5. 計算

公式寫在 `calc/` 的 Python 函式，說明寫著依據哪一頁。參數一律用關鍵字傳，單位寫在參數名稱裡；係數從資料頁查。

```python
from calc.timber.clt import design_strength
design_strength(f_k_mpa=28.2, k_mod=0.8, gamma_m=1.25)
```

## 6. 回存（fileback）

查詢得到值得留下的答案（比較、歸納、審查意見）時，存回成一頁：

```bash
python scripts/wiki.py fileback project-demo note panel-joint fj1-vs-fj8 \
  --title "FJ1 和 FJ8 的半搭接差在哪" --summary "…" \
  --from figure/panel-joint-001-demo-fj1-lap-joint,figure/panel-joint-004-demo-fj8-joint-over-beam < 答案.md
```

- 編號自動取下一個。要補在既有項目上（例如替細部圖補一頁筆記），加 `--item panel-joint-001`，兩邊的 `pair` 會自動加上。
- `--from` 必填，答案裡的數值要在那些頁裡找得到。
- 新頁是 draft，會登記到 NOTE.md 的「回存」小節，自動重建索引並檢查。
- 只回存擁有者要的或明顯會再用到的答案。

## 7. 輸出（export）

```bash
python scripts/wiki.py export atlas --wiki project-demo --kind detail   # 細部圖集，依知識點分章
python scripts/wiki.py export datasheet --wiki timber                     # 數據手冊
```

輸出到 `build/`，是單一 HTML 檔（圖片內嵌），可以直接開或用瀏覽器存成 PDF。`build/` 不進 git。

## 8. 技能（skill）

```bash
python scripts/wiki.py query search 順序 --type skill               # 找技能
python scripts/wiki.py query get skill:rhino-002                    # 讀技能本文
python scripts/wiki.py query point assembly-sequence                # 知識點的頁，以及用到它的技能
python scripts/wiki.py query impact timber:note/assembly-sequence-001-opening-order   # 這頁改了會影響哪些技能
```

- 在知識庫裡直接用：讀 `skills/<代號>/SKILL.md`。本文寫的 `profile/` 是指 `profiles/<專案主題>/` 裡對應這次專案的那一份。
- 規則後面的「依據」是頁的代號，用 `query get` 讀；`status` 不是 `reviewed` 的技能和頁都還沒經過擁有者確認。
- 要在工作專案裡用，先裝進去：

```bash
python scripts/wiki.py install skill rhino-002 <工作專案路徑> --profile project-demo           # Claude Code
python scripts/wiki.py install skill timber-001 <工作專案路徑> --bare --target codex             # Codex，沒有 profile
```

- 在工作專案裡改了技能，用 `python scripts/wiki.py ingest skill <專案裡的技能資料夾>` 帶回來，差異會放在 `skills/<代號>/incoming/`，由維護 agent 併入。

## 9. 能不能公開（share）

```bash
python scripts/wiki.py query share              # 統計，以及還沒標 share 的原件
python scripts/wiki.py query share public       # 可以公開的頁和技能
```

- `private` 的內容不能拿出這個 repo，包括貼到公開的地方、放進公開版的技能。`attribution` 的要標出處並遵守授權條件。
- 要給別人的東西一律用 `export` 產生，不要手動複製檔案：

```bash
python scripts/wiki.py export skill rhino-001 --public --draft     # 公開版技能（草稿要加 --draft）
python scripts/wiki.py export framework                            # 空框架
```

輸出前會掃描禁用字、本機路徑、Email 和照抄的原件文字，有命中就不輸出。每次輸出旁邊有一份報告，給別人之前先看。
