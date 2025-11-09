import requests
from bs4 import BeautifulSoup
import json
import urllib3
from pymongo import MongoClient
from datetime import datetime

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_bfi82u_html_data(date_str):
    """
    使用HTML標籤抓取台灣證券交易所三大法人買賣金額統計表（日報）

    Args:
        date_str: 日期格式 YYYYMMDD (例如: 20241223)

    Returns:
        包含表頭和資料的字典
    """
    # 使用相同的API端點，但這次我們解析返回的HTML
    url = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"

    # 請求參數
    params = {
        'dayDate': date_str,
        'type': 'day',
        'response': 'html'  # 要求返回HTML格式
    }

    # 設定Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"正在抓取 {date_str} 的三大法人買賣金額統計表（HTML格式）...")
        response = requests.get(url, params=params, headers=headers, verify=False)
        response.raise_for_status()

        # 使用BeautifulSoup解析HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # 尋找表格
        table = soup.find('table')

        if not table:
            print("未找到表格數據")
            return None

        # 抓取<thead>中的所有<tr>
        print("正在抓取表頭...")
        thead = table.find('thead')
        headers_data = []

        if thead:
            thead_rows = thead.find_all('tr')
            for row in thead_rows:
                row_data = []
                # 找所有th標籤
                ths = row.find_all(['th', 'td'])
                for th in ths:
                    row_data.append(th.get_text(strip=True))
                if row_data:
                    headers_data.append(row_data)

            print(f"找到 {len(headers_data)} 列表頭")

        # 抓取<tbody>中的所有<tr>內所有<td>的資料
        print("正在抓取表格資料...")
        tbody = table.find('tbody')
        data_rows = []

        if tbody:
            tbody_rows = tbody.find_all('tr')
            for row in tbody_rows:
                row_data = []
                tds = row.find_all('td')
                for td in tds:
                    row_data.append(td.get_text(strip=True))
                if row_data:
                    data_rows.append(row_data)

        print(f"總共抓取到 {len(data_rows)} 筆資料")

        if not data_rows:
            print("查無資料或該日期無交易資料")
            return None

        # 組織成JSON格式
        result = {
            "params": {
                "query_date": date_str,
                "headers": headers_data
            },
            "data": data_rows  
        }

        # 顯示結果
        print("\n" + "=" * 100)
        print("表頭資訊:")
        print("=" * 100)
        for idx, header_row in enumerate(headers_data):
            print(f"表頭第{idx + 1}列:")
            for i, header in enumerate(header_row):
                print(f"  欄位{i}: {header}")

        print("\n" + "=" * 100)
        print(f"資料內容（共 {len(data_rows)} 筆）:")
        print("=" * 100)

        # 使用最後一列表頭作為欄位名稱
        column_names = headers_data[-1] if headers_data else []

        for idx, row in enumerate(result["data"], 1):
            print(f"\n第 {idx} 筆資料:")
            for i, value in enumerate(row):
                if column_names and i < len(column_names):
                    print(f"  {column_names[i]}: {value}")
                else:
                    print(f"  欄位{i}: {value}")
            print("-" * 100)

        # 儲存為JSON檔案
        output_file = f"bfi82u_html_data_{date_str}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 資料已儲存至: {output_file}")

        return result

    except requests.exceptions.RequestException as e:
        print(f"網路請求錯誤: {e}")
        return None
    except Exception as e:
        print(f"發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None


def save_to_mongo(result, mongo_uri="mongodb://localhost:27017/", db_name="twse_db", collection_name="bfi82u_records"):
    """
    將資料儲存到MongoDB

    Args:
        result: fetch_bfi82u_html_data 函數返回的結果字典
        mongo_uri: MongoDB連線URI
        db_name: 資料庫名稱
        collection_name: 集合名稱

    Returns:
        儲存成功返回True，失敗返回False
    """
    if not result:
        print("無資料可儲存到MongoDB")
        return False

    try:
        # 連接MongoDB
        client = MongoClient(mongo_uri)
        db = client[db_name]
        collection = db[collection_name]

        # 準備儲存的文件
        # 從 headers 獲取欄位名稱
        column_names = result['params']['headers'][-1] if result['params']['headers'] else []

        # 將每筆資料轉換為字典格式
        records = []
        for row in result['data']:
            record = {
                "query_date": result['params']['query_date'],
                "inserted_at": datetime.now(),  # 記錄插入時間
            }

            # 將陣列資料轉換為有欄位名稱的字典
            for i, value in enumerate(row):
                if i < len(column_names):
                    field_name = column_names[i]
                    record[field_name] = value
                else:
                    record[f"field_{i}"] = value

            records.append(record)

        # 插入資料
        if records:
            result_insert = collection.insert_many(records)
            print(f"\n✓ 成功儲存 {len(result_insert.inserted_ids)} 筆資料到MongoDB")
            print(f"  資料庫: {db_name}")
            print(f"  集合: {collection_name}")
            return True
        else:
            print("無資料可儲存")
            return False

    except Exception as e:
        print(f"\n✗ MongoDB儲存失敗: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'client' in locals():
            client.close()


if __name__ == "__main__":
    # 使用最近的交易日期作為範例
    # 民國113年12月23日 = 西元2024年12月23日
    # 日期格式: YYYYMMDD
    date = "20241223"

    print("=" * 100)
    print("台灣證券交易所 - 三大法人買賣金額統計表爬蟲（日報）(HTML解析版本)")
    print("=" * 100)

    result = fetch_bfi82u_html_data(date)

    if result:
        print("\n✓ 資料抓取成功！")
        print(f"表頭列數: {len(result['params']['headers'])}")
        print(f"資料筆數: {len(result['data'])}")

        # 儲存到MongoDB
        print("\n" + "=" * 100)
        print("開始儲存資料到MongoDB...")
        print("=" * 100)
        save_to_mongo(result)

    else:
        print("\n✗ 資料抓取失敗，請檢查日期或網路連線")
