# twse_t86_json_crawler.py
"""
from pymongo import MongoClient
import requests
import datetime

def fetch_t86_json(date="20251023"):
    url = f"https://www.twse.com.tw/exchangeReport/MI_MARGN?response=json&date={date}&selectType=ALLBUT0999"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }
    resp = requests.get(url, headers=headers, verify=False)  # ⚠️ verify=False 跳過 SSL
    resp.raise_for_status()
    data = resp.json()
    return data

def parse_json(data):
    data_list = []
    # JSON 中的 key "data" 包含每一檔股票的買賣超資料
    for row in data.get("data", []):
        record = {
            "date": data.get("date"),  # 網站資料日期
            "stock_id": row[0].strip(),
            "stock_name": row[1].strip(),
            "foreign_net_buy_sell": row[2].replace(",", ""),
            "investment_trust_net_buy_sell": row[3].replace(",", ""),
            "dealer_net_buy_sell": row[4].replace(",", ""),
            "total_net_buy_sell": row[5].replace(",", "")
        }
        data_list.append(record)
    return data_list

def save_to_mongo(records):
    client = MongoClient("mongodb://localhost:27017/")
    db = client["twse_db"]
    coll = db["t86_records"]
    if records:
        coll.insert_many(records)
        print(f"✅ 已儲存 {len(records)} 筆資料")
    else:
        print("❌ 沒有資料可以儲存")

def main():
    data_json = fetch_t86_json("20251023")
    records = parse_json(data_json)
    print(f"抓取到 {len(records)} 筆資料")
    save_to_mongo(records)

if __name__ == "__main__":
    main()
"""

# twse_t86_1023.py
import requests

def fetch_t86(date):
    url = f"https://www.twse.com.tw/exchangeReport/MI_MARGN?response=json&date={date}&selectType=ALLBUT0999"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    try:
        resp = requests.get(url, headers=headers, verify=False)  # ⚠️ verify=False 跳過 SSL 驗證
        data = resp.json()
        if data.get("stat") != "OK":
            print("❌ 無法抓取資料")
            print(data)
            return []

        # data["data"] 就是 T86 資料
        return data["data"]

    except Exception as e:
        print("❌ 發生錯誤:", e)
        return []

def main():
    date = "20251023"  # 目標日期
    records = fetch_t86(date)
    print(f"抓取到 {len(records)} 筆資料")
    for r in records:
        print(r)

if __name__ == "__main__":
    main()

"""
# twse_t86_1023_html.py
import requests
from bs4 import BeautifulSoup

def fetch_t86_html():
    url = "https://www.twse.com.tw/zh/trading/foreign/t86.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"
    }

    resp = requests.get(url, headers=headers, verify=False)  # ⚠️跳過 SSL 驗證
    resp.encoding = "utf-8"
    return resp.text

def parse_html(html):
    from datetime import date
    soup = BeautifulSoup(html, "html.parser")
    data_list = []

    # 找表格
    table = soup.find("table")
    if not table:
        print("找不到資料表格")
        return data_list

    rows = table.find_all("tr")
    for tr in rows[1:]:  # 跳過標題列
        cols = tr.find_all("td")
        if len(cols) < 5:
            continue
        record = {
            "date": date.today().isoformat(),
            "category": cols[0].get_text(strip=True),
            "foreign_net_buy_sell": cols[1].get_text(strip=True),
            "investment_trust_net_buy_sell": cols[2].get_text(strip=True),
            "dealer_net_buy_sell": cols[3].get_text(strip=True),
            "total_net_buy_sell": cols[4].get_text(strip=True)
        }
        data_list.append(record)

    return data_list

def main():
    html = fetch_t86_html()
    records = parse_html(html)
    print(f"抓取到 {len(records)} 筆資料")
    for r in records:
        print(r)

if __name__ == "__main__":
    main()
"""