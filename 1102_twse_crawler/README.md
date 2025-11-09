# TWSE Crawler - 台灣證券交易所爬蟲工具

這是一個用於抓取台灣證券交易所（TWSE）機構投資人交易資料的 Python CLI 工具，可將資料自動存入 MongoDB 資料庫。

## 功能特色

- 抓取 **T86** 報表：三大法人買賣超日報（按個股統計）
- 抓取 **BFI82U** 報表：三大法人買賣金額統計表（匯總統計）
- 支援單日或日期區間批次抓取
- 自動建立唯一索引，防止重複資料
- 具備重試機制與錯誤處理
- 幕等性設計：重複執行不會產生重複資料

## 專案結構

```
twse_crawler/
├── .env                    # 環境變數設定檔（MongoDB 連線設定）
├── requirements.txt        # Python 套件依賴清單
├── venv/                   # Python 虛擬環境（已建立）
│
├── config.py              # 配置管理：讀取環境變數
├── db.py                  # 資料庫層：MongoDB 連線與資料操作
├── twse_api.py            # API 客戶端：抓取 TWSE 資料
├── __init__.py            # 套件初始化檔案
├── __main__.py            # CLI 入口點（作為模組執行）
├── crawler.py             # 獨立執行腳本（推薦使用）
│
├── test_connection.py     # MongoDB 連線測試工具
└── run.py                 # 替代執行腳本
```

## 檔案說明

### 核心檔案

#### `config.py`
- **用途**：管理環境變數配置
- **功能**：
  - 載入 `.env` 檔案
  - 提供 `get_mongo_uri()` - 取得 MongoDB 連線 URI
  - 提供 `get_db_name()` - 取得資料庫名稱

#### `db.py`
- **用途**：資料庫操作層
- **功能**：
  - `ensure_indexes()` - 建立唯一索引（防止重複資料）
    - `t86`: (date, stock_code) 複合唯一索引
    - `bfi82u`: (date) 唯一索引
  - `upsert_t86(docs)` - 批次插入/更新 T86 資料
  - `upsert_bfi82u(doc)` - 插入/更新 BFI82U 資料
  - 使用單例模式管理 MongoClient 連線

#### `twse_api.py`
- **用途**：TWSE API 客戶端
- **功能**：
  - `fetch_t86(date)` - 抓取 T86 報表
    - 回傳：每檔股票的三大法人買賣資料（list of dicts）
  - `fetch_bfi82u(date)` - 抓取 BFI82U 報表
    - 回傳：當日匯總統計資料（single dict）
  - 自動重試機制（預設 3 次，間隔 0.6 秒）
  - SSL 憑證驗證與備援處理
  - 模擬瀏覽器 User-Agent

#### `__main__.py`
- **用途**：CLI 程式入口點（作為模組執行時）
- **功能**：
  - 解析命令列參數（argparse）
  - 支援三種子命令：`t86`、`bfi82u`、`both`
  - 支援單日或日期區間
  - 自動建立索引並執行爬蟲
- **執行方式**：`python -m twse_crawler both --date 2024-11-01`

#### `crawler.py`（推薦使用）
- **用途**：獨立執行腳本
- **功能**：與 `__main__.py` 相同，但使用絕對導入
- **執行方式**：
  ```bash
  source venv/bin/activate
  python crawler.py both --date 2024-11-01
  ```
- **優點**：在虛擬環境中執行更簡單，不需要設定 PYTHONPATH

### 配置檔案

#### `.env`
```bash
# MongoDB 連線設定
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=twse
```
- **用途**：存放環境變數
- **可設定項目**：
  - `MONGODB_URI` - MongoDB 連線字串
  - `MONGODB_DB` - 資料庫名稱

支援的連線方式：
1. 本機連線（預設）：`mongodb://localhost:27017/`
2. MongoDB Atlas（雲端）：`mongodb+srv://username:password@cluster.mongodb.net/`
3. 有帳號密碼的連線：`mongodb://username:password@localhost:27017/`
4. 遠端連線：`mongodb://username:password@192.168.1.100:27017/`

#### `requirements.txt`
```
pymongo>=4.0.0          # MongoDB 驅動程式
python-dotenv>=0.19.0   # 環境變數管理
requests>=2.28.0        # HTTP 請求
certifi>=2022.0.0       # SSL 憑證
urllib3>=1.26.0         # HTTP 客戶端
```

### 輔助工具

#### `test_connection.py`
- **用途**：測試 MongoDB 連線是否正常
- **執行方式**：`python test_connection.py`

#### `run.py`
- **用途**：替代執行腳本（較少使用）
- **說明**：嘗試導入 `__main__.py` 並執行

## 安裝步驟

### 1. 建立虛擬環境（已完成）
```bash
python3 -m venv venv
```

### 2. 啟動虛擬環境
```bash
source venv/bin/activate
```

### 3. 安裝相依套件（已完成）
```bash
pip install -r requirements.txt
```

### 4. 設定 MongoDB 連線
編輯 `.env` 檔案：
```bash
MONGODB_URI=mongodb://localhost:27017/
MONGODB_DB=twse
```

確保 MongoDB 服務正在運行：
```bash
# macOS (使用 Homebrew)
brew services start mongodb-community

# 或手動啟動
mongod --config /opt/homebrew/etc/mongod.conf
```

## 使用方式

### 基本指令

```bash
# 1. 啟動虛擬環境
source venv/bin/activate

# 2. 抓取單日資料（兩種報表都抓）
python crawler.py both --date 2024-11-01

# 3. 抓取日期區間
python crawler.py both --start 2024-10-01 --end 2024-10-31 --sleep 1.0

# 4. 只抓 T86 報表
python crawler.py t86 --date 2024-11-01

# 5. 只抓 BFI82U 報表
python crawler.py bfi82u --date 2024-11-01
```

### 命令列參數說明

#### 子命令
- `t86` - 只抓取 T86 報表
- `bfi82u` - 只抓取 BFI82U 報表
- `both` - 同時抓取兩種報表（推薦）

#### 參數
- `--date YYYY-MM-DD` - 抓取單一日期
- `--start YYYY-MM-DD` - 區間起始日（需搭配 --end）
- `--end YYYY-MM-DD` - 區間結束日（需搭配 --start）
- `--sleep N` - 每次請求間隔秒數（預設 0.6，建議 0.6-1.0）

### 使用範例

```bash
# 範例 1：抓取最近一個交易日
python crawler.py both --date 2024-11-01

# 範例 2：抓取整個 10 月份（工作日約 20 天，需時約 20 秒）
python crawler.py both --start 2024-10-01 --end 2024-10-31 --sleep 1.0

# 範例 3：只抓 T86 並加快速度（小心被限流）
python crawler.py t86 --start 2024-11-01 --end 2024-11-05 --sleep 0.3
```

### 執行結果示例

```
[T86] 2024-11-01 upserted: 15016 rows
[BFI82U] 2024-11-01 upserted
```

- **T86**：每個交易日約有 1000-2000 檔股票（包含上市、上櫃、ETF）
- **BFI82U**：每個交易日一筆匯總資料

## 資料結構

### MongoDB Collections

#### `t86` Collection
```javascript
{
  "_id": ObjectId("..."),
  "date": "2024-11-01",              // ISO 日期格式
  "stock_code": "2330",              // 股票代碼
  "stock_name": "台積電",            // 股票名稱
  "證券代號": "2330",
  "證券名稱": "台積電",
  "外陸資買進股數(不含外資自營商)": "12,345,678",
  "外陸資賣出股數(不含外資自營商)": "10,234,567",
  "外陸資買賣超股數(不含外資自營商)": "2,111,111",
  // ... 其他欄位（保留 TWSE 原始中文欄位名稱）
}
```
- **唯一索引**：`(date, stock_code)`
- **每日筆數**：約 1000-2000 筆
- **數值格式**：千分位字串（如 "1,234,567"）

#### `bfi82u` Collection
```javascript
{
  "_id": ObjectId("..."),
  "date": "2024-11-01",
  "fields": [
    "單位名稱",
    "買進金額",
    "賣出金額",
    "買賣差額"
  ],
  "rows": [
    {
      "單位名稱": "自營商(自行買賣)",
      "買進金額": "12,345,678,901",
      "賣出金額": "11,234,567,890",
      "買賣差額": "1,111,111,011"
    },
    // ... 其他機構（外資、投信等）
  ]
}
```
- **唯一索引**：`(date)`
- **每日筆數**：1 筆（包含所有機構的匯總）

## 資料查詢範例

```javascript
// 使用 MongoDB Shell 或 Compass

// 1. 查詢台積電的三大法人買賣資料
db.t86.find({
  stock_code: "2330",
  date: { $gte: "2024-10-01", $lte: "2024-10-31" }
}).sort({ date: 1 })

// 2. 查詢某日外資買超前 10 名
db.t86.find({
  date: "2024-11-01"
}).sort({ "外陸資買賣超股數(不含外資自營商)": -1 }).limit(10)

// 3. 查詢某月份的匯總統計
db.bfi82u.find({
  date: { $gte: "2024-10-01", $lte: "2024-10-31" }
}).sort({ date: 1 })
```

## 注意事項

### 1. 交易日判斷
- TWSE 只在**交易日**才有資料
- 週末、國定假日會回傳空資料（顯示 "no data or holiday"）
- 這是正常現象，不是錯誤

### 2. 請求頻率
- 建議 `--sleep` 設定在 **0.6-1.0 秒**
- 過快可能被 TWSE 伺服器限流（HTTP 429）
- 過慢會增加整體執行時間

### 3. SSL 憑證警告
```
⚠️ SSL 憑證驗證失敗，改用非驗證連線（verify=False）
```
- 這是因為 TWSE 伺服器的 SSL 憑證可能不被 certifi 信任
- 程式會自動退回使用 `verify=False`
- 不影響資料抓取，但連線安全性較低

### 4. 資料重複處理
- 程式使用 **upsert** 操作（有則更新，無則插入）
- 唯一索引確保同一天的同一檔股票只有一筆資料
- 可以安全地重複執行，不會產生重複資料

### 5. MongoDB 連線
- 確保 MongoDB 服務正在運行
- 預設連接 `localhost:27017`
- 如需修改，編輯 `.env` 檔案

## 錯誤排除

### 問題 1：無法連接 MongoDB
```
pymongo.errors.ServerSelectionTimeoutError
```
**解決方法**：
```bash
# 檢查 MongoDB 是否運行
brew services list | grep mongodb

# 啟動 MongoDB
brew services start mongodb-community
```

### 問題 2：找不到模組
```
ModuleNotFoundError: No module named 'pymongo'
```
**解決方法**：
```bash
# 確認已啟動虛擬環境
source venv/bin/activate

# 重新安裝套件
pip install -r requirements.txt
```

### 問題 3：日期格式錯誤
```
ValueError: time data '20241101' does not match format '%Y-%m-%d'
```
**解決方法**：
- 使用正確的日期格式：`YYYY-MM-DD`
- 範例：`--date 2024-11-01`（不是 `20241101`）

### 問題 4：TWSE 回傳空資料
```
[T86] 2024-11-02 no data or holiday
```
**說明**：
- 該日可能是週末或國定假日
- 或 TWSE 尚未公佈該日資料（通常 T+1 公佈）

## 開發資訊

### 技術棧
- **Python 3.13**
- **pymongo 4.15.3** - MongoDB 官方驅動
- **requests 2.32.5** - HTTP 請求
- **python-dotenv 1.2.1** - 環境變數管理

### TWSE API 端點
- **T86**：`https://www.twse.com.tw/rwd/zh/fund/T86`
- **BFI82U**：`https://www.twse.com.tw/rwd/zh/fund/BFI82U`

### 架構設計
```
CLI (crawler.py / __main__.py)
    ↓
API Client (twse_api.py) → 抓取 JSON from TWSE
    ↓
Database Layer (db.py) → Upsert to MongoDB
    ↑
Config (config.py) ← .env
```

## 版本歷史

### 2024-11-04
- 新增 `crawler.py` 獨立執行腳本
- 修改 `db.py` 支援絕對導入和相對導入
- 建立虛擬環境並安裝相依套件
- 成功抓取並存入 MongoDB（測試日期：2024-11-01）

## 更改/新增檔案總結

  1. 新增檔案（3 個）

  venv/ 目錄
  - Python 虛擬環境，包含所有相依套件
  - 讓專案依賴與系統環境隔離

  crawler.py（主要新增，推薦使用）
  - 獨立執行腳本，91 行程式碼
  - 完整複製 __main__.py 的功能
  - 改用絕對導入 (from db import ... 而非 from .db import ...)
  - 可直接執行：python crawler.py both --date 2024-11-01

  run_crawler.py（測試檔案，可刪除）
  - 最初嘗試的執行腳本，未成功
  - 建議刪除，不影響專案運作

  2. 修改檔案（1 個）

  db.py 的第 4-7 行   
  **原本**   
  from .config import get_mongo_uri, get_db_name

  **修改為**   
  try:
      from .config import get_mongo_uri, get_db_name
  except ImportError:
      from config import get_mongo_uri, get_db_name
  - 目的：同時支援相對導入和絕對導入
  - 讓程式更靈活，可作為模組或獨立腳本執行

  3. 原有檔案保持不變

  - __main__.py - CLI 入口點
  - __init__.py - 套件初始化
  - config.py - 配置管理
  - twse_api.py - API 客戶端
  - test_connection.py - 連線測試
  - run.py - 執行腳本
  - .env - 環境變數設定
  - requirements.txt - 套件依賴

  