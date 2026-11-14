# 用語對照

文件和頁裡常出現的英文。知識內容的術語在 `atoms/`，用 `python scripts/wiki.py query atom <名稱>` 查。

## 結構

| 英文 | 中文 | 在這裡的意思 |
|---|---|---|
| wiki | 主題 | `wikis/` 底下的一個資料夾，例如 timber、project-demo |
| raw | 原件 | 原始的 PDF、網頁快照，和它的登記卡 |
| atom | 原子 | 最小的概念，即詞條：有中英日名稱、上下位關係，全部主題共用 |
| page | 頁 | 筆記、資料、圖、程式碼四種的統稱 |
| note | 筆記 | 用文字講一件事：原理、做法或觀點 |
| data | 資料 | 一張表格：`.md` 說明加 `.csv` 數據 |
| figure | 圖 | 影像加上圖上原文和說明 |
| code | 程式碼 | 程式片段、設定檔、提示詞 |
| point | 知識點 | 依知識領域分的資料夾，四種頁共用同一個名稱 |
| item | 項目 | 知識點-編號，例如 bearing-connection-001。同編號就是同一項 |
| pair | 同編號 | 檔頭欄位，列出同一項的其他頁 |
| NOTE.md | 入口檔 | 每個知識點的入口，像 skill 的 SKILL.md |
| skill | 技能 | `skills/<代號>/`：agent 可以照著做的能力包，依據頁，全部主題共用 |
| SKILL.md | 技能本體 | 技能的說明：何時用、規則、步驟 |
| profile | 個人設定 | 技能的 `profiles/<專案主題>/`：某個專案的慣例、參數、案件經驗，私人 |
| profile.example | 示範設定 | 去識別化的 profile，公開輸出時取代 profiles |
| share | 可見度 | public 可以公開、attribution 要標出處、private 不能公開。原件登記，其他推算 |
| denylist | 禁用字清單 | 不能出現在公開輸出裡的字。根目錄一份管全部，技能的 profile 裡各一份只管那個技能 |
| incoming | 待併入的改動 | 技能的 `incoming/`：從工作專案帶回來、還沒併入的差異 |
| framework | 空框架 | 只有程式、規則、模板的版本，可以給別人 |
| plan / specs / tasks | 計畫 / 規格 / 任務 | `docs/plans/<日期-名稱>/` 的三份檔案，給一次做不完的工作用 |
| checkpoint | 存檔點 | tasks 的「階段與存檔點」表的一列：產出、commit、lint 結果、狀態、下一步 |
| FEEDBACK | 問題與調整紀錄 | `docs/FEEDBACK.md`，只記框架本身的問題 |
| CHANGELOG | 版本紀錄 | 框架的版本，號碼在 `schema.json` 的 `framework_version` |
| index | 索引 | `index/` 裡給 agent 先讀的目錄 |

## 動作

| 英文 | 中文 | 在這裡的意思 |
|---|---|---|
| ingest | 攝入 | 登記原件、擷取文字和圖 |
| query | 查詢 | 找頁、查表、追依據 |
| fileback | 回存 | 把查詢得到的答案存回成新的一頁 |
| lint | 檢查 | 檢查格式、連結、編號、索引，驗證公式 |
| export | 輸出 | 產生細部圖集、數據手冊、私人版或公開版的技能、空框架 |
| install | 安裝 | 把技能裝進工作專案，並記下版本 |
| new | 新建 | 建立新的主題或技能 |
| review | 確認 | 擁有者核對後把狀態改成 reviewed |

## 其他

| 英文 | 中文 | 在這裡的意思 |
|---|---|---|
| agent | 代理程式 | 會自己讀檔、跑指令的 AI 工具，例如 Claude Code |
| frontmatter / YAML | 檔頭 | 檔案開頭兩條 `---` 之間的欄位 |
| schema | 結構定義 | `schema.json`，規定有哪些類型和欄位 |
| draft / reviewed / retired | 草稿 / 已確認 / 停用 | 頁的狀態；只有擁有者能設 reviewed |
| OCR | 文字辨識 | 從圖片辨識文字，結果要校對 |
| crop | 裁切 | 從 PDF 頁面切出一塊區域存成圖 |
| region box | 裁切範圍 | 裁切的頁碼和座標，可以重新裁出同一塊 |
| atlas | 圖集 | 把圖和配置表依知識點排成一份文件 |
| datasheet | 數據手冊 | 把資料頁依主題和種類排成一份文件 |
| CSV | 逗號分隔值 | 表格的純文字格式，Excel 可以直接開 |
| commit / push | 提交 / 推送 | git 的存檔和上傳 |
