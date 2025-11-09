import requests
from datetime import datetime
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_institutional_investors_data(date_str):
    """
    抓取台灣證券交易所三大法人買賣超日報

    Args:
        date_str: 日期格式 YYYYMMDD (例如: 20251023)

    Returns:
        前10筆資料
    """
    # API端點
    url = "https://www.twse.com.tw/rwd/zh/fund/T86"

    # 請求參數
    params = {
        'date': date_str,
        'selectType': 'ALL',
        'response': 'json'
    }

    # 設定Headers模擬瀏覽器請求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 發送GET請求
        print(f"正在抓取 {date_str} 的三大法人買賣超資料...")
        response = requests.get(url, params=params, headers=headers, verify=False)
        response.raise_for_status()

        # 解析JSON資料
        data = response.json()

        # 檢查資料是否存在
        if 'data' not in data or not data['data']:
            print("查無資料或該日期無交易資料")
            return None

        # 顯示欄位名稱
        print("\n欄位說明:")
        if 'fields' in data:
            print(data['fields'])

        # 取得前10筆資料
        records = data['data'][:10]

        print(f"\n總共抓取到 {len(records)} 筆資料（前10筆）:")
        print("=" * 100)

        # 逐筆顯示資料
        for idx, record in enumerate(records, 1):
            print(f"\n第 {idx} 筆資料:")
            for i, value in enumerate(record):
                if 'fields' in data and i < len(data['fields']):
                    print(f"  {data['fields'][i]}: {value}")
                else:
                    print(f"  欄位{i}: {value}")
            print("-" * 100)

        return records

    except requests.exceptions.RequestException as e:
        print(f"網路請求錯誤: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"JSON解析錯誤: {e}")
        return None
    except Exception as e:
        print(f"發生錯誤: {e}")
        return None


if __name__ == "__main__":
    # 114年10月23日 = 2025年10月23日
    # 注意：目前日期是2025-10-26，但實際上今天是2025年1月（根據系統資訊），
    # 所以114年10月23日在未來。這裡使用正確的西元年份

    # 民國114年 = 西元2025年
    # 但根據系統時間，現在是2025年1月，10月23日還沒到
    # 讓我們先嘗試一個已經過去的日期作為示範

    # 使用民國114年（2025年）的日期格式
    date = "20251023"  # YYYYMMDD格式

    print("=" * 100)
    print("台灣證券交易所 - 三大法人買賣超日報爬蟲")
    print("=" * 100)

    result = fetch_institutional_investors_data(date)

    if result:
        print("\n✓ 資料抓取成功！")
    else:
        print("\n✗ 資料抓取失敗，請檢查日期或網路連線")
