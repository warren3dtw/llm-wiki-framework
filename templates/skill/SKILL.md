---
name: 前綴-001            # 等於資料夾名稱：前綴加三位數，例如 rhino-002。同一前綴從 001 起算不重複
title: 標題               # 一句話說這個技能做什麼
summary: 一句話，80 字以內
description: 前綴-001：做什麼、什麼時候用。agent 靠這一行判斷要不要載入，寫成一行，1024 字以內
type: skill
kind: workflow            # workflow 工作流程 / tool 工具操作 / check 檢查與審查 / setup 建置
version: 0.1.0            # 主版本.次版本.修正。改規則升次版本，修錯字升修正，改輸入輸出格式升主版本
share: private            # private / attribution / public。只能比依據推算的結果更嚴格；沒把握就填 private
atoms: []                 # 講到哪些原子
points: []                # 用到哪些知識點，寫成 主題:知識點，例如 timber:assembly-sequence。不能是專案主題
from: []                  # 依據哪些頁，寫完整代號，例如 timber:note/assembly-sequence-001-opening-order。不能是專案主題
uses: []                  # 要先用哪些技能，例如 skill:rhino-001
raw: ""                   # 從工作專案匯入時填「主題:raw/原件代號, 位置」；自己寫的留空
status: draft
updated: YYYY-MM-DD
checked:                  # 依據改過、重看後不必改時填這個日期
---

一句話說明用完會得到什麼。

## 何時使用

- 什麼情況要用。
- 什麼情況不要用，改用哪個技能。

## 開始前需要

- 輸入資料、軟體和版本、要先用的技能。
- 專案的慣例和參數在 `profiles/<專案主題>/`。沒有這個專案的 profile 時，照 `profile.example/` 建一份，不要猜。

## 規則

每條規則後面註明依據的頁。沒有依據的標〔經驗〕或〔待查證〕。

1. 規則。（依據：timber:note/知識點-001-描述）

## 步驟

1. 動作。要跑的腳本寫成 `scripts/xxx.py`，參數讀 profile 的 `config.json`。
2. 動作。

## 怎麼確認做對了

做完後檢查什麼。驗收題在 `tests.md`。

## 限制

已知做不到、或要人工判斷的情況。
