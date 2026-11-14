# 維護 init-001

改編自 Rhino-init 的 init-maintainer 角色（原檔快照在 `wikis/agent/raw/rhino-init-2026-11-14/init-maintainer.md`）。目標不變：任何人只拿到 init-001，就能走完「環境建置 → 空結構 → 第一個任務 → 中斷續作」，不依賴原作者的電腦、案例或對話。

## 回饋從哪裡來

- 用 init-001 建立的工作專案：`docs/FEEDBACK.md`、`docs/INIT-REPORT.md` 的差異說明、專案自己改編過的規範。
- 這個資料夾的 `tests/examples/` 跑驗證或走讀時發現的缺口。

## 判斷哪些要併入

- 併入：換專案、換電腦或換人仍會發生的問題與改法。
- 不併入：個案的尺寸、字高、字型、檔名、模型雜湊與客戶資料；這些留在專案的 PROJECT 或計畫。
- 工具行為和版本有關時，寫成「案例」並附版本，不寫成全域預設。
- 原因還是推測、沒有證據的先不併入，在 PR 說明缺什麼。
- 要改變 作者已定的規則時（例如備份規則），列出差異等作者決定，不自行改。

## 修改順序

1. 列候選：專案名稱與 FEEDBACK ID、是否併入、理由、要改 SKILL.md 哪一節。
2. 改 `SKILL.md` 的內容契約。
3. 同步 `tests/examples/` 裡受影響的模式；general 不得出現繪圖或動畫內容。
4. 有實質改動就提升版本：`version`（例如 2.3.0 → 2.4.0）、SKILL.md 內文 INIT-REPORT 契約的「init 規格版本」、每個示例 `docs/INIT-REPORT.md` 的版本與「x.y 調整」小節；必要檔有增減時，同步 Phase 1 清單、`scripts/validate_init.py` 的清單與示例的生成清單。
5. 跑驗證（見下節），沒跑的寫「未執行」。
6. 在 `CHANGELOG.md` 寫一筆，註明回饋來源；回到原專案時，在對應 FEEDBACK 項目寫「已併入 init-001 x.y（章節）」或不併入的原因。

## 每次都要檢查

- 可攜性：生成內容不含絕對路徑、使用者名稱、Email、電腦名稱、客戶或案名、本機檔案，也不寫只在某個專案成立的敘述。
- 外部軟體：寫清楚如何確認已安裝、如何確認 AI 能操作、未連線時怎麼繼續。MCP 安裝步驟不寫進 init。查不到取得方式就寫「待確認」，不編造下載位置、版本或工具名稱。
- 階段存檔：流程中斷後，只憑 tasks 的階段表就能接續。
- 驗證：在 `skills/init-001/scripts/` 跑 `python -m unittest test_validate_init`，它會對三個示例跑 `validate_init.py`，也測試壞掉的結構會被抓到。之後 `wiki.py lint` 支援技能時會自動執行。內容契約、空白語意與走讀情境仍要逐檔讀過。

## 界線

- 不修改原工作專案的 sources、models、drawings、deliverables，也不操作 Rhino、CADCraft 或動畫引擎。
- 不放寬權限、不改全域設定。
- 不修改專案計畫的驗收結果，不把未實測的外部能力寫成已驗證。
