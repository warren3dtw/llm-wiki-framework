# 架構與資料流

| 路徑 | 用途 |
|---|---|
| README.md | 人與 AI 的起點 |
| CLAUDE.md | Claude 工作入口 |
| docs/ | 專案事實、規範、成果與初始化報告 |
| docs/templates/ | 計畫原始模板 |
| docs/plans/ | 任務及驗收證據 |
| docs/plans/archive/ | 完成或取消的完整計畫 |
| .claude/ | 工具設定、規則、角色及 hooks 說明 |

來源供追溯，工作檔供編輯，交付檔保存已產出版本；三者不能混用。

資料流：需求 → plan／specs／tasks → Rhino GUID 與圖層盤點 → group 組裝單元 → Rhino 編號 → 使用者核准 → 同修訂 JSON＋GLB → 場景 → 逐格渲染 → 影片與配套驗收。
上游 group、GUID、幾何、圖層或排序規則變更，排序審核與下游驗收失效；只改運鏡或背景不必重編號，但要重驗畫面與影片。

| 路徑 | 用途 |
|---|---|
| sources/ | 唯讀來源：原始 .3dm、參考圖、HDRI／貼圖與授權資訊 |
| models/ | 正常保存的 Rhino 工作模型 |
| exports/ | 經核准的 JSON／GLB 同修訂配套 |
| public/assembly/ | 當次場景使用的完整配套，不混修訂 |
| out/ | 暫存測試影片，不進 git |
| deliverables/ | 正式影片與配套交付，不覆寫已發布版本 |

動畫引擎與場景程式尚未選定；建立後登記在 PROJECT，並在本表加上場景程式的位置。
