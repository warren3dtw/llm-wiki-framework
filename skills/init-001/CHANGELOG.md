# 版本紀錄

只往上追加。每筆寫版本、日期、改了什麼、回饋從哪裡來。

## 2.3.2（2026-11-14）

- 跨專案通用的五條工作規則（存檔點、變更等級、未知不是預設、驗收證據、commit 時機）寫成 `agent` 主題的 `project-harness` 知識點，本技能改成依據它們（`from`、`points`），本文加「依據的規則」一節。內容契約沒有改。

## 2.3.1（2026-11-14）

- SKILL.md 從 745 行拆成本體加三份內容契約（`references/contracts-common.md`、`mode-rhino-cadcraft.md`、`mode-rhino-animation.md`），符合 Agent Skills 建議的 500 行以內；各模式只讀自己需要的契約。內容契約本身沒有改，init 規格版本仍是 2.3。
- 檔頭改成知識庫的技能格式；`references/maintaining.md` 不再提到擁有者的名字。

## 2.3.0（2026-11-14）

- 搬進 New-LLM-Wiki 的 `skills/`。主版本從此在這裡；工作專案裡的 init.md 是它的輸出。
- 新增 rhino-animation 模式：Phase 1 必要清單、Phase 2 的動畫規格與資料流、Phase 4B 的 MODELING／ASSEMBLY／ANIMATION／DELIVERY 契約、Phase 5 的 .gitignore、空權限基底、animation-workflow 規則、animation-reviewer 與角色索引、Phase 6 的走讀。來源：rhino-remotion-skill 專案的改編紀錄（原件登記卡 `wikis/agent/raw/rhino-remotion-skill-2026-11-14.md`）。
- 使用 Codex 時所有模式另加 AGENTS.md。來源同上。
- 新增 `scripts/validate_init.py`（改寫自該專案的 validate-init.mjs，支援三種模式）與 `tests/examples/rhino-animation/`。
- general、rhino-cadcraft 的示例只更新 INIT-REPORT 的版本與 2.3 調整說明。

## 2.2（2026-11-05 前後，Rhino-init）

- 原始版本，見 `wikis/agent/raw/rhino-init-2026-11-14/init.md`。2.1、2.2 的調整摘要在示例的 INIT-REPORT。
