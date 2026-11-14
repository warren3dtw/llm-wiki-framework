# 場景、時序與渲染

製片值讀 [PROJECT](PROJECT.md) 與本次 specs。動畫引擎尚未選定；以下以 React Three Fiber＋Remotion 為例，使用其他工具時保留階段、絕對時序、GUID 對應與驗收規則，專用指令記 PROJECT。

## 製作階段

| 階段 | 工作／輸出 | 完成條件 |
|---|---|---|
| A1 模型盤點 | 來源、圖層規則與單位記 specs；工作檔存 models/ | 範圍、group 衝突與必要資訊已確認 |
| A2 編號審核 | Rhino 標註、草稿與核准證據 | 使用者明確確認當版順序 |
| A3 交換資料 | exports/ 同修訂 JSON／GLB | fingerprint、GUID、bounds、組內姿態通過 |
| A4 場景與運鏡 | 場景程式與本地素材 | 單元剛性、風格、取景與載入通過 |
| A5 渲染驗收 | out/ 測試片與新版本正式影片 | 資料檢查、代表幀、短片與影片規格通過 |
| A6 使用者交付 | deliverables/ 及 [DELIVERY](DELIVERY.md) | 使用者接受；此前維持待審查 |

每階段依 [DEVELOPMENT](DEVELOPMENT.md) 存檔；未存的 GUI 狀態不算存檔點。

## 場景與時間

- 動畫一律以絕對幀數計算（Remotion 為 useCurrentFrame）；禁止累積 delta、未固定的亂數與即時物理。任意跳格或倒播要得到相同姿態。
- 時長依最大 animationStep（舊資料回退 order）與每步幀數計算，保留尾段觀賞時間；同一步的單元同時進場，仍保有獨立節點與 GUID。
- 同單元成員共用父節點移動；最終落位等於原模型。入場方向與路徑是視覺表達，不宣稱吊裝模擬或結構安全。
- JSON、GLB、HDRI、貼圖都要納入載入等待；失敗就取消渲染並回報，不輸出缺件或空白片。

## 畫面

運鏡依完整 bounds、長寬比與入場範圍設定目標、距離與 near／far，檢查遮擋與裁切。防 z-fighting 不移動物件：near／far 依 bounds 收緊，共面構件以材料類別的 polygonOffset 決定優先，且不與 logarithmicDepthBuffer 並用（Three.js 場景適用）。
背景由使用者決定；HDRI 記來源與授權並存在本地，不在渲染時下載。未完成材質前不宣稱寫實。

## 渲染

順序審查以預覽工具（Remotion 為 Studio）為準，使用者未要求前不輸出影片，自檢只渲染單幀到暫存區。build 只產生 bundle。
正式渲染前核對本機 CLI 說明與 Composition ID，先做代表幀與短片；記 CLI、瀏覽器或 GPU 入口、codec、像素、fps、幀數、時長與 SHA256。失敗先定位載入、記憶體、WebGL 或資料問題，不以降低規格冒充通過。
