# 組裝、審核與交換資料

規則寫在這裡，實作放在 skill 或程式。排序與匯出的 skill：未登記；首次匯出前確認實作來源，未安裝的 skill 不列為可用。

## 單元與排序

- 圖層完整路徑提供分區、樓層、類別。先查實際路徑結構，確認優先級後才展開排序；使用者提供的順序優先。
- 普通 Rhino group 就是組裝單元，不要求命名；未分組物件各自為單元；巢狀 group 以最外層為單元。重疊 group、跨樓層／分區或部分成員在範圍外時先釐清，不自動聯集合併，也不漏掉組員。
- 每個單元一個唯一順序 `order`；組內標記（例如 012-01）只供識別。批次進場另用 `animationStep`，不得因此合併單元、GUID、group 或 GLB 節點。原始 GUID 保留；單元的穩定 ID 不用順序號或 group index 代替。
- 鋼木接點、臨時支撐與吊裝相依不能只憑幾何相交判定，只提出疑點與建議，使用者確認後才重排。

## 強制流程

盤點 → 草稿與編號 → Rhino 標註與對照表 → 使用者明確核准 → 核對 fingerprint → 匯出。核准的草稿、規則與回覆證據寫進本次 tasks。
GUID、幾何、group、圖層或規則改變要重審；只改背景或運鏡只重驗畫面。
標註放專用輔助圖層並排除輸出；未經要求不改 group 名稱或原物件名稱。

## 交換資料

- JSON 記 schema 版本、fingerprint、單元 ID／order／animationStep、成員 GUID／圖層與 bounds。GLB 保留單元父節點與物件子節點，extras 帶單元 ID、order、animationStep、Rhino GUID；不跨單元合併。
- 單位轉公尺，Rhino Z-up 轉 glTF Y-up，資料的單位與方向必須一致。
- 核准範圍內全部物件才是完整模型，列明排除圖層；不支援的物件類型停止並說明，不破壞性 explode 原文件。
- 審查用的低精度網格要標明「非正式交換資料」，仍須保留單元、GUID、座標與 animationStep。
- 新修訂輸出到 exports/ 的未用版本資料夾，JSON 與 GLB 同修訂；給動畫用時整組放 public/assembly/，記 SHA256 與來源。資產載入或 GUID 驗證失敗就停止。
