# 台灣證券交易所三大法人買賣金額統計表爬蟲 - 方法比較說明

本專案提供兩種不同的方法來抓取台灣證券交易所的三大法人買賣金額統計表（日報），每種方法各有其特點與適用場景。

## 目錄

- [方法概覽](#方法概覽)
- [方法一：API JSON格式抓取（推薦）](#方法一api-json格式抓取推薦)
- [方法二：HTML解析抓取](#方法二html解析抓取)
- [方法比較表](#方法比較表)
- [安裝說明](#安裝說明)
- [使用建議](#使用建議)

---

## 方法概覽

| 方法 | 檔案名稱 | 技術 | 狀態 | 推薦度 |
|------|---------|------|------|--------|
| 方法一 | `bfi82u_crawler.py` | requests + JSON API | ✅ 可用 | ⭐⭐⭐⭐⭐ |
| 方法二 | `bfi82u_html_crawler.py` | requests + BeautifulSoup | ✅ 可用 | ⭐⭐⭐⭐ |

---

## 方法一：API JSON格式抓取（推薦）

### 檔案：`bfi82u_crawler.py`

### 技術原理

直接呼叫台灣證券交易所的官方JSON API，無需解析HTML結構，獲取結構化的JSON資料。

### 優點

- ✅ **速度最快**：直接獲取JSON資料，無需HTML解析
- ✅ **資料結構清晰**：API返回標準化的JSON格式
- ✅ **依賴最少**：僅需要 `requests` 和 `urllib3` 套件
- ✅ **最穩定**：官方API通常較穩定，不易因網頁改版而失效
- ✅ **網路流量小**：僅傳輸必要的資料
- ✅ **包含註記資訊**：提供完整的註記說明

### 缺點

- ❌ **依賴API**：若API端點變更或關閉，程式將無法運作
- ❌ **靈活性較低**：僅能獲取API提供的資料格式

### 使用方式

```bash
# 啟動虛擬環境
source venv/bin/activate

# 執行程式
python bfi82u_crawler.py
```

### 程式碼範例

```python
import requests

url = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"
params = {
    'dayDate': '20241223',
    'type': 'day',
    'response': 'json'  # 要求JSON格式
}
response = requests.get(url, params=params, verify=False)
data = response.json()
```

### 輸出格式

- 終端輸出：格式化顯示全部6筆資料（三大法人各類別）
- 不自動儲存檔案（可自行修改程式新增儲存功能）

### 資料內容

JSON API返回的資料包含：

```json
{
  "stat": "OK",
  "date": "20241223",
  "title": "113年12月23日 三大法人買賣金額統計表",
  "fields": ["單位名稱", "買進金額", "賣出金額", "買賣差額"],
  "data": [
    ["自營商(自行買賣)", "5,243,028,941", "2,975,504,988", "2,267,523,953"],
    ["自營商(避險)", "12,488,930,361", "9,035,713,466", "3,453,216,895"],
    ["投信", "28,651,644,695", "28,516,508,697", "135,135,998"],
    ["外資及陸資(不含外資自營商)", "139,498,877,563", "100,071,058,060", "39,427,819,503"],
    ["外資自營商", "0", "0", "0"],
    ["合計", "185,882,481,560", "140,598,785,211", "45,283,696,349"]
  ],
  "notes": [...],  // 詳細註記說明
  "hints": "單位：元"
}
```

---

## 方法二：HTML解析抓取

### 檔案：`bfi82u_html_crawler.py`

### 技術原理

使用requests請求API的HTML格式回應，再使用BeautifulSoup解析HTML中的`<table>`標籤，提取`<thead>`和`<tbody>`中的資料。

### 優點

- ✅ **完整的HTML結構**：可獲取完整的表格結構
- ✅ **表頭資訊完整**：自動抓取`<thead>`中所有`<tr>`作為params
- ✅ **易於理解**：程式邏輯清晰，適合學習HTML解析
- ✅ **自動存儲JSON**：結果自動儲存為JSON檔案
- ✅ **MongoDB整合**：內建MongoDB儲存功能，自動儲存結構化資料
- ✅ **資料結構化**：將表頭和資料分離，便於後續處理
- ✅ **不需瀏覽器**：無需安裝Chrome或ChromeDriver

### 缺點

- ❌ **速度略慢**：需要額外的HTML解析步驟
- ❌ **依賴較多**：需要 `requests`, `beautifulsoup4`, `lxml` 套件
- ❌ **缺少註記**：HTML回應不包含註記資訊

### 使用方式

```bash
# 啟動虛擬環境
source venv/bin/activate

# 執行程式
python bfi82u_html_crawler.py
```

### 程式碼範例

```python
from bs4 import BeautifulSoup
import requests

# 請求HTML格式
params = {
    'dayDate': '20241223',
    'type': 'day',
    'response': 'html'  # 要求HTML格式
}
response = requests.get(url, params=params, verify=False)

# 解析HTML
soup = BeautifulSoup(response.text, 'html.parser')
table = soup.find('table')

# 抓取表頭
thead = table.find('thead')
thead_rows = thead.find_all('tr')

# 抓取資料
tbody = table.find('tbody')
tbody_rows = tbody.find_all('tr')
```

### 輸出格式

**JSON檔案結構**（`bfi82u_html_data_YYYYMMDD.json`）：

```json
{
  "params": {
    "query_date": "20241223",
    "headers": [
      ["113年12月23日 三大法人買賣金額統計表"],
      ["單位名稱", "買進金額", "賣出金額", "買賣差額"]
    ]
  },
  "data": [
    ["自營商(自行買賣)", "5,243,028,941", "2,975,504,988", "2,267,523,953"],
    ["自營商(避險)", "12,488,930,361", "9,035,713,466", "3,453,216,895"],
    ["投信", "28,651,644,695", "28,516,508,697", "135,135,998"],
    ["外資及陸資(不含外資自營商)", "139,498,877,563", "100,071,058,060", "39,427,819,503"],
    ["外資自營商", "0", "0", "0"],
    ["合計", "185,882,481,560", "140,598,785,211", "45,283,696,349"]
  ]
}
```

### 資料說明

- **params.query_date**：查詢日期
- **params.headers**：陣列，包含表頭的所有列
  - 第1列：標題（如 "113年12月23日 三大法人買賣金額統計表"）
  - 第2列：欄位名稱（4個欄位）
- **data**：資料陣列，共6筆資料（三大法人各類別及合計）

### 抓取內容

**HTML結構**：
```html
<table>
  <thead>
    <tr>
      <th colspan='4'>113年12月23日 三大法人買賣金額統計表</th>
    </tr>
    <tr>
      <th>單位名稱</th>
      <th>買進金額</th>
      <th>賣出金額</th>
      <th>買賣差額</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>自營商(自行買賣)</td>
      <td>5,243,028,941</td>
      <td>2,975,504,988</td>
      <td>2,267,523,953</td>
    </tr>
    ...
  </tbody>
</table>
```

---

## 方法比較表

### 效能比較

| 項目 | 方法一 (JSON API) | 方法二 (HTML解析) |
|------|------------------|------------------|
| **執行速度** | ⚡⚡⚡ 最快 (~1秒) | ⚡⚡ 快 (~2秒) |
| **網路流量** | 📦 最小 | 📦📦 中等 |
| **記憶體使用** | 💾 ~20MB | 💾💾 ~50MB |
| **CPU使用** | 🔋 低 | 🔋🔋 中 |

### 功能比較

| 功能 | 方法一 | 方法二 |
|------|--------|--------|
| **獲取資料** | ✅ | ✅ |
| **表頭結構** | ✅ | ✅ (完整) |
| **註記說明** | ✅ | ❌ |
| **自動存檔** | ❌ | ✅ JSON |
| **MongoDB儲存** | ❌ | ✅ 內建 |
| **穩定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **易維護** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |

### 依賴套件比較

| 套件 | 方法一 | 方法二 |
|------|--------|--------|
| requests | ✅ | ✅ |
| urllib3 | ✅ | ✅ |
| beautifulsoup4 | ❌ | ✅ |
| lxml | ❌ | ✅ |
| pymongo | ❌ | ✅ (選用) |

---

## 安裝說明

### 環境準備

```bash
# 創建虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows
```

### 方法一所需套件

```bash
pip install requests urllib3
```

### 方法二所需套件

```bash
pip install requests urllib3 beautifulsoup4 lxml pymongo
```

### MongoDB安裝（選用）

如果需要使用MongoDB儲存功能：

```bash
# macOS
brew tap mongodb/brew
brew install mongodb-community

# 啟動MongoDB服務
brew services start mongodb-community

# Ubuntu/Debian
sudo apt-get install mongodb

# 確認MongoDB運行狀態
pgrep -l mongod
```

---

## 使用建議

### 🏆 最佳選擇：方法一（API JSON格式）

**適用場景**：
- 日常資料抓取
- 自動化排程任務
- 需要高效能的場景
- 需要註記說明資訊
- 資源受限的環境

**範例**：
```bash
source venv/bin/activate
python bfi82u_crawler.py
```

### 🥈 次選：方法二（HTML解析）

**適用場景**：
- 學習HTML解析技術
- 需要完整表頭結構
- 需要自動存檔為JSON
- API格式不滿足需求時

**範例**：
```bash
source venv/bin/activate
python bfi82u_html_crawler.py
```

**輸出檔案**：`bfi82u_html_data_20241223.json`

---

## 程式修改指南

### 修改查詢日期

```python
# 修改主程式中的日期變數
date = "20241223"  # 格式：YYYYMMDD
```

### 新增CSV匯出功能

```python
import csv

# 在主程式結尾新增
with open('output.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)

    # 寫入表頭
    if headers_data:
        writer.writerows(headers_data)

    # 寫入資料
    writer.writerows(data_rows)
```

---

## 常見問題

### Q1: 為什麼有兩種方法？

**A:** 不同的場景有不同的需求：
- **方法一**最快速穩定，適合日常使用，並提供完整的註記資訊
- **方法二**提供完整的HTML結構，適合學習和需要表頭資訊的場景

### Q2: 哪種方法最適合我？

**A:**
- 如果只是要抓取資料 → 使用**方法一**
- 如果需要學習HTML解析 → 使用**方法二**
- 如果需要註記說明 → 使用**方法一**

### Q3: 如何選擇JSON或HTML格式？

**A:**
- **JSON格式**（方法一）：資料結構化，處理方便，速度快，包含註記
- **HTML格式**（方法二）：保留完整表格結構，可獲取更多HTML元素資訊

### Q4: SSL證書錯誤如何處理？

**A:** 程式已內建 `verify=False` 和 `urllib3.disable_warnings()`，一般不會遇到問題。

### Q5: 資料從什麼時候開始提供？

**A:** 根據證交所資訊，此資料自民國93年4月7日（西元2004年4月7日）起提供。

### Q6: 如何定期自動執行？

**A:** 使用cron（Linux/macOS）或Task Scheduler（Windows）：

```bash
# crontab範例：每天早上9點執行
0 9 * * * cd /path/to/project && source venv/bin/activate && python bfi82u_crawler.py
```

---

## 進階應用

### 整合MongoDB儲存

**方法二（bfi82u_html_crawler.py）已內建MongoDB儲存功能**，執行程式時會自動儲存資料到MongoDB。

#### 自動儲存（預設行為）

```bash
# 執行程式會自動儲存到MongoDB
source venv/bin/activate
python bfi82u_html_crawler.py
```

#### 自訂MongoDB連線參數

如果需要使用自訂的MongoDB連線參數，可以修改程式：

```python
# 在 bfi82u_html_crawler.py 的 main 區塊中修改
save_to_mongo(
    result,
    mongo_uri="mongodb://username:password@host:port/",
    db_name="custom_db",
    collection_name="custom_collection"
)
```

#### MongoDB儲存的資料結構

```python
{
  "_id": ObjectId("..."),
  "query_date": "20241223",
  "inserted_at": ISODate("2025-10-26T21:42:26.643Z"),
  "單位名稱": "自營商(自行買賣)",
  "買進金額": "5,243,028,941",
  "賣出金額": "2,975,504,988",
  "買賣差額": "2,267,523,953"
}
```

#### 查詢MongoDB資料

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['twse_db']
collection = db['bfi82u_records']

# 查詢特定日期的資料
records = collection.find({'query_date': '20241223'})
for record in records:
    print(f"{record['單位名稱']}: {record['買賣差額']}")

# 查詢外資買賣差額
foreign_record = collection.find_one({
    'query_date': '20241223',
    '單位名稱': '外資及陸資(不含外資自營商)'
})
print(f"外資買賣差額: {foreign_record['買賣差額']}")

# 查詢最近7天的資料
import datetime
week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).strftime('%Y%m%d')
recent_records = collection.find({
    'query_date': {'$gte': week_ago}
}).sort('query_date', -1)
```

#### 僅儲存JSON不儲存MongoDB

如果不想使用MongoDB儲存功能，只需註解掉主程式中的MongoDB儲存程式碼：

```python
if result:
    print("\n✓ 資料抓取成功！")
    # 註解掉以下MongoDB儲存部分
    # save_to_mongo(result)
```

### 批次查詢多個日期

#### 批次抓取並儲存到MongoDB

```python
import time
from bfi82u_html_crawler import fetch_bfi82u_html_data, save_to_mongo

dates = ['20241220', '20241223', '20241224']

for date in dates:
    print(f"\n處理日期: {date}")
    result = fetch_bfi82u_html_data(date)

    if result:
        # 儲存到MongoDB
        save_to_mongo(result)
        print(f"✓ {date} 資料已儲存")
    else:
        print(f"✗ {date} 資料抓取失敗")

    time.sleep(3)  # 避免請求過於頻繁

print("\n批次處理完成！")
```

#### 查詢多日資料趨勢

```python
from pymongo import MongoClient
import pandas as pd

client = MongoClient('mongodb://localhost:27017/')
db = client['twse_db']
collection = db['bfi82u_records']

# 查詢多個日期的外資買賣差額
dates = ['20241220', '20241223', '20241224']
trend_data = []

for date in dates:
    record = collection.find_one({
        'query_date': date,
        '單位名稱': '外資及陸資(不含外資自營商)'
    })

    if record:
        trend_data.append({
            'date': date,
            'amount': record['買賣差額']
        })

# 使用pandas分析趨勢
df = pd.DataFrame(trend_data)
print(df)
```

### 資料分析

```python
import pandas as pd

# 方法一：從API返回的data直接建立DataFrame
df = pd.DataFrame(data['data'], columns=data['fields'])

# 方法二：從JSON檔案載入
with open('bfi82u_html_data_20241223.json', 'r', encoding='utf-8') as f:
    json_data = json.load(f)

df = pd.DataFrame(json_data['data'], columns=json_data['params']['headers'][-1])

# 顯示外資買賣差額
foreign = df[df['單位名稱'] == '外資及陸資(不含外資自營商)']
print(foreign[['單位名稱', '買賣差額']])
```

---

## API詳細說明

### 端點資訊

**API URL**：`https://www.twse.com.tw/rwd/zh/fund/BFI82U`

### 請求參數

| 參數名稱 | 必填 | 說明 | 範例值 |
|---------|------|------|--------|
| dayDate | 是 | 查詢日期 | 20241223 |
| type | 是 | 報表類型 | day (日報), week (週報), month (月報) |
| response | 是 | 回應格式 | json, html |

### 回應格式（JSON）

```json
{
  "stat": "OK",                    // 狀態：OK 或錯誤訊息
  "date": "20241223",              // 查詢日期
  "title": "...",                  // 標題
  "fields": [...],                 // 欄位名稱陣列
  "data": [...],                   // 資料陣列
  "notes": [...],                  // 註記說明陣列
  "hints": "單位：元",             // 提示資訊
  "params": {...}                  // 請求參數
}
```

### 資料欄位說明

1. **單位名稱**：法人類別
   - 自營商(自行買賣)
   - 自營商(避險)
   - 投信
   - 外資及陸資(不含外資自營商)
   - 外資自營商
   - 合計

2. **買進金額**：該法人類別當日買進股票的總金額（單位：元）
3. **賣出金額**：該法人類別當日賣出股票的總金額（單位：元）
4. **買賣差額**：買進金額 - 賣出金額（正值表示淨買進，負值表示淨賣出）

---

## 專案檔案結構

```
mongo_crawler/
├── venv/                          # 虛擬環境
├── bfi82u_crawler.py              # 方法一：JSON API（推薦）
├── bfi82u_html_crawler.py         # 方法二：HTML解析
├── bfi82u_html_data_20241223.json # 方法二輸出範例
└── bfi82u_README.md               # 本文件
```

---

## 授權與免責聲明

本專案僅供學習與研究使用，資料版權屬於台灣證券交易所所有。使用時請遵守證交所的使用規範，不得用於商業用途或過度頻繁請求。

---

## 參考資源

- [台灣證券交易所官網](https://www.twse.com.tw/)
- [三大法人買賣金額統計表](https://www.twse.com.tw/zh/trading/foreign/bfi82u.html)
- [BeautifulSoup文件](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Requests文件](https://requests.readthedocs.io/)

---

**最後更新**：2025年1月26日
**版本**：1.0.0
