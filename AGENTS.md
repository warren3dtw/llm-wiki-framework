# 給所有 agent 的入口

這個 repo 是一個個人知識庫。

- **原件**（raw）登記進來後，整理成四種**頁**（page）：**筆記**（note）、**資料**（data）、**圖**（figure）、**程式碼**（code）。筆記再用種類分成原理、做法、觀點。
- 四種頁底下都依**知識點**（point）分資料夾。檔名是「知識點-編號-描述」，**同編號就是同一項**（例如一個細部的圖和它的配置表），檔頭的 `pair` 互相列出。每個知識點的入口是 `note/<知識點>/NOTE.md`。
- 頁用多語的**原子**（atom，即詞條）串起來，再產生一份給 agent 先讀的**索引**。
- 五個動作：**ingest** 攝入、**query** 查詢、**fileback** 回存、**lint** 檢查、**export** 輸出。
- **技能**（skill）放在 `skills/<代號>/SKILL.md`：把頁打包成 agent 可以照著做的工作。專案的慣例放在技能的 `profiles/<專案主題>/`。

先判斷你這次是哪一種角色，一次工作只當一種。

| 你要做的事 | 角色 | 讀這個 |
|---|---|---|
| 查資料、回答問題、做計算、輸出圖集或手冊、把答案回存 | 使用 agent | [`USING.md`](USING.md) |
| 登記原件、從 PDF 或網頁新增頁、修改知識、整理收件匣、新增或改進技能 | 維護 agent | [`MAINTAINING.md`](MAINTAINING.md) |
| 只改腳本、說明文件、schema | 維護 agent | [`MAINTAINING.md`](MAINTAINING.md) 的「目錄」和「不要做」 |

## 所有角色都要遵守

- 寫給擁有者的文字用繁體中文。英文術語第一次出現時附中文，對照表在 [`GLOSSARY.md`](GLOSSARY.md)。
- `status` 不是 `reviewed` 的頁還沒有經過擁有者確認，引用時要說明。agent 不把狀態設成 `reviewed`。
- 不修改 `wikis/*/raw/` 裡的原件和擷取結果。同一個資料夾裡的登記卡（`raw/*.md`）可以更新閱讀進度和已知問題。
- 專案主題（`project-*`）的內容通常受委託方或原設計單位的著作權和保密限制，不能拿到這個 repo 以外的地方用。放了專案內容的 repo 必須維持私人。
- 要給別人的東西一律用 `export` 產生（公開版技能、空框架），不要手動複製檔案。`share` 是 `private` 的內容不能公開。
- 知識庫是學習筆記，不是設計依據。實際設計以現行規範原文和專業簽證為準。

## 指令

全部從 `scripts/wiki.py` 進入。Windows 上把 `python` 換成 `py`。只用 Python 標準庫；擷取另需 poppler 和 tesseract。

```bash
python scripts/wiki.py query overview                      # 有哪些主題
python scripts/wiki.py query search 搭接 --type figure      # 找頁（中、英、日文都可以）
python scripts/wiki.py query get <代號>                    # 讀一頁
python scripts/wiki.py query point bearing-connection     # 一個知識點的全部頁
python scripts/wiki.py fileback <主題> note <知識點> <描述> ...  # 把答案存回成一頁
python scripts/wiki.py lint                                # 檢查格式、連結、索引，驗證公式
python scripts/wiki.py index                               # 重建索引
python scripts/wiki.py export atlas --wiki project-demo  # 輸出細部圖集
python scripts/wiki.py query share                         # 哪些可以公開
python scripts/wiki.py export skill <代號> --public         # 輸出公開版技能（另有 --profile <專案主題>）
python scripts/wiki.py install skill <代號> <專案路徑> --profile <專案主題>   # 把技能裝進工作專案
python scripts/wiki.py export framework                    # 輸出空框架
```

整體設計（有哪些東西、怎麼關聯、資料怎麼流動）見 [`docs/FRAMEWORK.md`](docs/FRAMEWORK.md)。
