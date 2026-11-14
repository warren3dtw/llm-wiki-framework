# commit 時機：整個任務完成而且驗證通過才 commit，不自動 push

- 代號：agent:note/project-harness-005-commit-timing
- 類型：筆記・規則
- 摘要：只納入這次任務的變更；驗證失敗不 commit；commit 不等於驗收
- 出處：Rhino-init 工作專案快照（2026-11-14），init.md 規格 2.2 「docs/DEVELOPMENT.md」
- 狀態：草稿，還沒有經過作者確認

commit 太早，會把做到一半、沒驗證的狀態留在紀錄裡；太晚，中斷時又沒有可以回去的點。

## 規則

- 整個對話任務完成而且驗證通過後才 commit，不自動 push。
- 只納入這次任務的變更，不夾帶無關、來源不明的變更或敏感資料。沒有變更就不 commit。
- 驗證失敗或任務沒完成時不 commit，先回報。commit 的指令要以驗證結果為條件，不先提交再補救。
- commit 不等於驗收：待審查的項目在 commit 之後仍然是待審查。
- 案件資料要不要進 git，第一次加入之前先問使用者；沒答覆前不 commit 那些檔案，也不先寫進 .gitignore。

## 成立條件

用 git 管理、由 agent 修改檔案的專案。

## 不適用的情況

使用者另外指定了 commit 或 push 的方式時，照使用者的。
