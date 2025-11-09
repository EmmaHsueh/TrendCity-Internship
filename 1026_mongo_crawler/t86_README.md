# 台灣證券交易所三大法人買賣超爬蟲 - 方法比較說明

本專案提供三種不同的方法來抓取台灣證券交易所的三大法人買賣超日報資料，每種方法各有其特點與適用場景。

## 目錄

- [方法概覽](#方法概覽)
- [方法一：API JSON格式抓取](#方法一api-json格式抓取)
- [方法二：HTML解析抓取（推薦）](#方法二html解析抓取推薦)
- [方法三：Selenium動態抓取](#方法三selenium動態抓取)
- [方法比較表](#方法比較表)
- [安裝說明](#安裝說明)
- [使用建議](#使用建議)

---

## 方法概覽

| 方法 | 檔案名稱 | 技術 | 狀態 | 推薦度 |
|------|---------|------|------|--------|
| 方法一 | `twse_crawler.py` | requests + JSON API | ✅ 可用 | ⭐⭐⭐⭐⭐ |
| 方法二 | `twse_html_simple_crawler.py` | requests + BeautifulSoup | ✅ 可用 | ⭐⭐⭐⭐ |
| 方法三 | `twse_html_crawler.py` | Selenium + WebDriver | ⚠️ 有問題 | ⭐⭐ |

---

## 方法一：API JSON格式抓取

### 檔案：`twse_crawler.py`

### 技術原理

直接呼叫台灣證券交易所的官方JSON API，無需解析HTML結構，獲取結構化的JSON資料。

### 優點

- ✅ **速度最快**：直接獲取JSON資料，無需HTML解析
- ✅ **資料結構清晰**：API返回標準化的JSON格式
- ✅ **依賴最少**：僅需要 `requests` 和 `urllib3` 套件
- ✅ **最穩定**：官方API通常較穩定，不易因網頁改版而失效
- ✅ **網路流量小**：僅傳輸必要的資料

### 缺點

- ❌ **依賴API**：若API端點變更或關閉，程式將無法運作
- ❌ **靈活性較低**：僅能獲取API提供的資料格式

### 使用方式

```bash
# 啟動虛擬環境
source venv/bin/activate

# 執行程式
python twse_crawler.py
```

### 程式碼範例

```python
import requests

url = "https://www.twse.com.tw/rwd/zh/fund/T86"
params = {
    'date': '20251023',
    'selectType': 'ALL',
    'response': 'json'  # 要求JSON格式
}
response = requests.get(url, params=params, verify=False)
data = response.json()
```

### 輸出格式

- 終端輸出：格式化顯示前10筆資料
- 不自動儲存檔案（可自行修改程式新增儲存功能）

---

## 方法二：HTML解析抓取（推薦）

### 檔案：`twse_html_simple_crawler.py`

### 技術原理

使用requests請求API的HTML格式回應，再使用BeautifulSoup解析HTML中的`<table>`標籤，提取`<thead>`和`<tbody>`中的資料。

### 優點

- ✅ **完整的HTML結構**：可獲取完整的表格結構
- ✅ **表頭資訊完整**：自動抓取`<thead>`中所有`<tr>`作為params
- ✅ **易於理解**：程式邏輯清晰，適合學習HTML解析
- ✅ **自動存儲JSON**：結果自動儲存為JSON檔案
- ✅ **資料結構化**：將表頭和資料分離，便於後續處理
- ✅ **不需瀏覽器**：無需安裝Chrome或ChromeDriver

### 缺點

- ❌ **速度略慢**：需要額外的HTML解析步驟
- ❌ **依賴較多**：需要 `requests`, `beautifulsoup4`, `lxml` 套件

### 使用方式

```bash
# 啟動虛擬環境
source venv/bin/activate

# 執行程式
python twse_html_simple_crawler.py
```

### 程式碼範例

```python
from bs4 import BeautifulSoup
import requests

# 請求HTML格式
params = {
    'date': '20251023',
    'selectType': 'ALL',
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

**JSON檔案結構**（`twse_html_data_YYYYMMDD.json`）：

```json
{
  "params": {
    "query_date": "20251023",
    "headers": [
      ["114年10月23日 三大法人買賣超日報"],
      ["證券代號", "證券名稱", "外陸資買進股數(不含外資自營商)", ...]
    ]
  },
  "data": [
    ["00715L", "期街口布蘭特正2", "62,195,000", "926,000", ...],
    ["2337", "旺宏", "56,115,550", "22,708,390", ...],
    ...
  ]
}
```

### 資料說明

- **params.query_date**：查詢日期
- **params.headers**：陣列，包含表頭的所有列
  - 第1列：標題（如 "114年10月23日 三大法人買賣超日報"）
  - 第2列：欄位名稱（19個欄位）
- **data**：資料陣列，每筆資料為一個陣列（前10筆）

### 抓取內容

**HTML結構**：
```html
<main>
  <table>
    <thead>
      <tr><!-- 標題列 --></tr>
      <tr><!-- 欄位名稱列 --></tr>
    </thead>
    <tbody>
      <tr>
        <td>00715L</td>
        <td>期街口布蘭特正2</td>
        <td>62,195,000</td>
        ...
      </tr>
      ...
    </tbody>
  </table>
</main>
```

---

## 方法三：Selenium動態抓取

### 檔案：`twse_html_crawler.py`

### 技術原理

使用Selenium自動化瀏覽器，模擬使用者操作：開啟網頁 → 輸入日期 → 點擊查詢 → 等待表格載入 → 抓取HTML。

### 優點

- ✅ **最接近真實瀏覽**：模擬真實使用者行為
- ✅ **處理動態內容**：可處理需要JavaScript渲染的網頁
- ✅ **彈性最高**：可處理複雜的互動流程

### 缺點

- ❌ **目前有技術問題**：無法正確定位網頁元素
- ❌ **速度最慢**：需要啟動完整瀏覽器
- ❌ **依賴最多**：需要安裝Chrome、ChromeDriver、Selenium
- ❌ **資源消耗大**：記憶體和CPU使用率高
- ❌ **維護成本高**：網頁改版時需要更新選擇器

### 已知問題

```
TimeoutException: Message:
無法找到元素 (By.ID, "input_date")
```

**原因**：網頁可能使用了不同的元素ID或動態生成的ID，需要進一步調整選擇器。

### 使用方式（目前不建議）

```bash
# 安裝依賴
source venv/bin/activate
pip install selenium

# 確保已安裝Chrome瀏覽器和ChromeDriver

# 執行程式
python twse_html_crawler.py
```

### 適用場景

此方法適合以下情況：
- 網站完全依賴JavaScript渲染，無API可用
- 需要處理複雜的使用者互動（如登入、多步驟查詢）
- 需要截圖或錄製操作過程

**本專案不推薦使用此方法**，因為台灣證券交易所提供了更簡單的API和HTML格式。

---

## 方法比較表

### 效能比較

| 項目 | 方法一 (JSON API) | 方法二 (HTML解析) | 方法三 (Selenium) |
|------|------------------|------------------|------------------|
| **執行速度** | ⚡⚡⚡ 最快 (~1秒) | ⚡⚡ 快 (~2秒) | ⚡ 慢 (~10秒) |
| **網路流量** | 📦 最小 | 📦📦 中等 | 📦📦📦 最大 |
| **記憶體使用** | 💾 ~20MB | 💾💾 ~50MB | 💾💾💾 ~200MB |
| **CPU使用** | 🔋 低 | 🔋🔋 中 | 🔋🔋🔋 高 |

### 功能比較

| 功能 | 方法一 | 方法二 | 方法三 |
|------|--------|--------|--------|
| **獲取資料** | ✅ | ✅ | ⚠️ |
| **表頭結構** | ✅ | ✅ (完整) | ⚠️ |
| **自動存檔** | ❌ | ✅ JSON | ❌ |
| **穩定性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |
| **易維護** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐ |

### 依賴套件比較

| 套件 | 方法一 | 方法二 | 方法三 |
|------|--------|--------|--------|
| requests | ✅ | ✅ | ❌ |
| urllib3 | ✅ | ✅ | ✅ |
| beautifulsoup4 | ❌ | ✅ | ❌ |
| lxml | ❌ | ✅ | ❌ |
| selenium | ❌ | ❌ | ✅ |
| Chrome瀏覽器 | ❌ | ❌ | ✅ |
| ChromeDriver | ❌ | ❌ | ✅ |

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
pip install requests urllib3 beautifulsoup4 lxml
```

### 方法三所需套件

```bash
pip install requests urllib3 selenium

# 額外需要：
# 1. 安裝Chrome瀏覽器
# 2. 下載對應版本的ChromeDriver
# 3. 將ChromeDriver放入系統PATH
```

---

## 使用建議

### 🏆 最佳選擇：方法一（API JSON格式）

**適用場景**：
- 日常資料抓取
- 自動化排程任務
- 需要高效能的場景
- 資源受限的環境

**範例**：
```bash
source venv/bin/activate
python twse_crawler.py
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
python twse_html_simple_crawler.py
```

**輸出檔案**：`twse_html_data_20251023.json`

### ⚠️ 不推薦：方法三（Selenium）

**適用場景**：
- 僅在前兩種方法都無法使用時考慮
- 需要處理複雜的JavaScript互動
- 需要截圖或錄製操作

**目前狀態**：有技術問題，需要進一步調試

---

## 程式修改指南

### 修改查詢日期

**方法一和方法二**：
```python
# 修改主程式中的日期變數
date = "20251023"  # 格式：YYYYMMDD
```

**方法三**：
```python
# 修改主程式中的日期變數
date = "2025/10/23"  # 格式：YYYY/MM/DD
```

### 修改抓取筆數

所有方法都在程式中有以下程式碼：
```python
# 取前10筆
records = data['data'][:10]

# 修改為前20筆
records = data['data'][:20]

# 取得全部資料
records = data['data'][:]
```

### 修改查詢類型

```python
params = {
    'date': date_str,
    'selectType': 'ALL',  # 修改此處
    'response': 'json'  # 或 'html'
}

# selectType 選項：
# 'ALL' - 全部
# 'ALLBUT0999' - 全部(不含權證、牛熊證、可展延牛熊證)
# 'STOCK' - 股票
# 'ETF' - ETF
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

### Q1: 為什麼有三種方法？

**A:** 不同的場景有不同的需求：
- **方法一**最快速穩定，適合日常使用
- **方法二**提供完整的HTML結構，適合學習和需要表頭資訊的場景
- **方法三**保留作為參考，適合處理複雜互動的網站

### Q2: 哪種方法最適合我？

**A:**
- 如果只是要抓取資料 → 使用**方法一**
- 如果需要學習HTML解析 → 使用**方法二**
- 如果需要處理需要登入或複雜互動的網站 → 考慮**方法三**（但本專案不需要）

### Q3: 如何選擇JSON或HTML格式？

**A:**
- **JSON格式**（方法一）：資料結構化，處理方便，速度快
- **HTML格式**（方法二）：保留完整表格結構，可獲取更多HTML元素資訊

### Q4: SSL證書錯誤如何處理？

**A:** 程式已內建 `verify=False` 和 `urllib3.disable_warnings()`，一般不會遇到問題。

### Q5: 方法三為什麼無法運作？

**A:** 可能原因：
1. 網頁元素ID改變
2. 需要更長的等待時間
3. ChromeDriver版本不匹配

由於方法一和方法二已足夠使用，建議優先使用前兩種方法。

### Q6: 如何定期自動執行？

**A:** 使用cron（Linux/macOS）或Task Scheduler（Windows）：

```bash
# crontab範例：每天早上9點執行
0 9 * * * cd /path/to/project && source venv/bin/activate && python twse_crawler.py
```

---

## 進階應用

### 整合MongoDB儲存

```python
from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['twse_database']
collection = db['institutional_investors']

# 插入資料
collection.insert_one(result)
```

### 批次查詢多個日期

```python
dates = ['20251023', '20251024', '20251027']

for date in dates:
    result = fetch_twse_html_data(date)
    # 處理結果...
    time.sleep(3)  # 避免請求過於頻繁
```

### 資料分析

```python
import pandas as pd

# 載入JSON資料
with open('twse_html_data_20251023.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 轉換為DataFrame
df = pd.DataFrame(data['data'], columns=data['params']['headers'][-1])

# 分析三大法人買賣超前10名
top10 = df.nlargest(10, '三大法人買賣超股數')
print(top10[['證券代號', '證券名稱', '三大法人買賣超股數']])
```

---

## 專案檔案結構

```
mongo_crawler/
├── venv/                          # 虛擬環境
├── twse_crawler.py                # 方法一：JSON API
├── twse_html_simple_crawler.py    # 方法二：HTML解析（推薦）
├── twse_html_crawler.py           # 方法三：Selenium
├── twse_html_data_20251023.json   # 方法二輸出範例
├── README.md                      # 方法一的說明文件
└── html_README.md                 # 本文件（三種方法比較）
```

---

## 授權與免責聲明

本專案僅供學習與研究使用，資料版權屬於台灣證券交易所所有。使用時請遵守證交所的使用規範，不得用於商業用途或過度頻繁請求。

---

## 參考資源

- [台灣證券交易所官網](https://www.twse.com.tw/)
- [三大法人買賣超日報](https://www.twse.com.tw/zh/trading/foreign/t86.html)
- [BeautifulSoup文件](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [Selenium文件](https://www.selenium.dev/documentation/)
- [Requests文件](https://requests.readthedocs.io/)

---

**最後更新**：2025年10月26日
**版本**：1.0.0
