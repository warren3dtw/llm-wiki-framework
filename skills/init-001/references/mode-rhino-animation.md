# init-001 內容契約：rhino-animation

由 [SKILL.md](../SKILL.md) 指過來。只有 rhino-animation 模式要讀。共用的契約在 [contracts-common.md](contracts-common.md)；MODELING 的「建模方法」「MCP 操作」「建模檢查」寫在 [mode-rhino-cadcraft.md](mode-rhino-cadcraft.md)，動畫模式只取用到的部分。

## Phase 4B：rhino-animation 文件擴充

本節的引擎例子是 React Three Fiber＋Remotion。使用其他動畫工具時，保留階段、絕對時序、GUID 對應與驗收規則，引擎專用的指令與設定改記 PROJECT。

### docs/MODELING.md（動畫）

寫明主要使用既有建築模型，不為動畫重建；任務要新建幾何時預設點→線→面→體，規則同 Phase 4 的「建模方法」，用途只需線或面時可停止。尺寸、單位、公差與版本讀 PROJECT。

操作流程：

1. 以不啟動實例的唯讀工具定位實例與文件；沒有實例不為初始化啟動 Rhino。
2. 查來源、文件單位、規格與本次輸出範圍；含隱藏、鎖定、重複及輔助物件，不能只看選取或畫面。
3. 依 DEVELOPMENT 判 task／spec 備份；來源唯讀，工作檔正常存 models/。
4. 修改前取 context；腳本用 MCP 實作提供的文件參照（原介面為 __rhino_doc__），不猜作用中文件。
5. 修改後檢查幾何、數量、GUID、圖層、group 與視圖；階段存檔要有實檔、SHA256、工具與來源版本及下一步。
6. 編號與匯出讀 ASSEMBLY；影片觀感不能代替幾何檢查。

另寫入 Phase 4 的「MCP 操作」注意事項與「建模檢查」中和動畫有關的部分；版本案例只記版本，不作全域預設。不引入 DRAWING 的出圖流程。

### docs/ASSEMBLY.md

寫入組裝單元、排序審核與交換資料的規則；實作放在 skill 或程式，docs 只記介面與限制。已安裝排序或匯出 skill 時連到它的 SKILL 與資料契約；沒有時寫「未登記；首次匯出前確認實作來源」，不把未安裝的 skill 列為可用。

單元與排序：

- 圖層完整路徑提供分區、樓層、類別。先查實際路徑結構，確認優先級後才展開排序；使用者提供的順序優先。
- 普通 Rhino group 就是組裝單元，不要求命名；未分組物件各自為單元；巢狀 group 以最外層為單元。重疊 group、跨樓層／分區或部分成員在範圍外時先釐清，不自動聯集合併，也不漏掉組員。
- 每個單元一個唯一順序 `order`；組內標記（例如 012-01）只供識別。需要批次進場時另用 `animationStep`，不得因此合併單元、GUID、group 或 GLB 節點。原始 GUID 保留；單元的穩定 ID 不用順序號或 group index 代替。
- 鋼木接點、臨時支撐與吊裝相依不能只憑幾何相交判定，只提出疑點與建議，使用者確認後才重排。

強制流程：盤點 → 草稿與編號 → Rhino 標註與對照表 → 使用者明確核准 → 核對 fingerprint → 匯出。核准的草稿、規則與回覆證據寫進本次 tasks。GUID、幾何、group、圖層或規則改變要重審；只改背景或運鏡只重驗畫面。標註放專用輔助圖層並排除輸出；未經要求不改 group 名稱或原物件名稱。

交換資料：

- JSON 記 schema 版本、fingerprint、單元 ID／order／animationStep、成員 GUID／圖層與 bounds。GLB 保留單元父節點與物件子節點，extras 帶單元 ID、order、animationStep、Rhino GUID；不跨單元合併。
- 單位轉公尺，Rhino Z-up 轉 glTF Y-up，資料的單位與方向必須一致。
- 核准範圍內全部物件才是完整模型，列明排除圖層；不支援的物件類型停止並說明，不破壞性 explode 原文件。
- 審查用的低精度網格要標明「非正式交換資料」，仍須保留單元、GUID、座標與 animationStep。
- 新修訂輸出到 exports/ 的未用版本資料夾，JSON 與 GLB 同修訂；給動畫用時整組放 public/assembly/，記 SHA256 與來源。資產載入或 GUID 驗證失敗就停止。

### docs/ANIMATION.md

製片值讀 PROJECT 與本次 specs；既有空場景或 skill 的建議值不是已核准規格。

寫入下列階段，每階段依 DEVELOPMENT 存檔；不把未存的 GUI 狀態當存檔點。

| 階段 | 工作／輸出 | 完成條件 |
|---|---|---|
| A1 模型盤點 | 來源、圖層規則與單位記 specs；工作檔存 models/ | 範圍、group 衝突與必要資訊已確認 |
| A2 編號審核 | Rhino 標註、草稿與核准證據 | 使用者明確確認當版順序 |
| A3 交換資料 | exports/ 同修訂 JSON／GLB | fingerprint、GUID、bounds、組內姿態通過 |
| A4 場景與運鏡 | 場景程式與本地素材 | 單元剛性、風格、取景與載入通過 |
| A5 渲染驗收 | out/ 測試片與新版本正式影片 | 資料檢查、代表幀、短片與影片規格通過 |
| A6 使用者交付 | deliverables/ 及 DELIVERY | 使用者接受；此前維持待審查 |

場景與時間：

- 動畫一律以絕對幀數計算（Remotion 為 useCurrentFrame）；禁止累積 delta、未固定的亂數與即時物理。任意跳格或倒播要得到相同姿態。
- 時長依最大 animationStep（舊資料回退 order）與每步幀數計算，保留尾段觀賞時間；同一步的單元同時進場，仍保有獨立節點與 GUID。
- 同單元成員共用父節點移動；最終落位等於原模型。入場方向與路徑是視覺表達，不宣稱吊裝模擬或結構安全。
- JSON、GLB、HDRI、貼圖都要納入載入等待；失敗就取消渲染並回報，不輸出缺件或空白片。

畫面：運鏡依完整 bounds、長寬比與入場範圍設定目標、距離與 near／far，檢查遮擋與裁切。防 z-fighting 不移動物件：near／far 依 bounds 收緊，共面構件以材料類別的 polygonOffset 決定優先，且不與 logarithmicDepthBuffer 並用（Three.js 場景適用）。背景由使用者決定；HDRI 記來源與授權並存在本地，不在渲染時下載。未完成材質前不宣稱寫實。

渲染：順序審查以預覽工具（Remotion 為 Studio）為準，使用者未要求前不輸出影片，自檢只渲染單幀到暫存區。build 只產生 bundle。正式渲染前核對本機 CLI 說明與 Composition ID，先做代表幀與短片；記 CLI、瀏覽器或 GPU 入口、codec、像素、fps、幀數、時長與 SHA256。失敗先定位載入、記憶體、WebGL 或資料問題，不以降低規格冒充通過。

### docs/DELIVERY.md（動畫）

初始交付清單為空。表欄位：成果 ID、計畫／來源模型版本、JSON／GLB 版本、影片／設定版本、日期、驗收證據、驗收人／角色、狀態／限制。

規則：來源唯讀；工作檔與交付分離；新交付用未使用的版本，不覆寫已發布成果；最高版本不等於核准版。JSON、GLB、場景設定與影片同修訂，記 SHA256。不把原模型或素材的重新散布權視為自動取得。

影片驗收至少含可開啟、codec、尺寸、fps、時長／幀數、無黑幀、漏件、裁切與載入失敗；順序核准證據存在；GUID 雙向對應與最終姿態符合核准模型；記場景、運鏡、背景、燈光、材質的來源與授權；有聲音時驗音軌，無聲標不適用。自動與人工檢查分列；使用者未接受前維持待審查。
