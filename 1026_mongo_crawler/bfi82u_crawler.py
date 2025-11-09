import requests
from datetime import datetime
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_institutional_trading_amount(date_str):
    """
    抓取台灣證券交易所三大法人買賣金額統計表（日報）

    Args:
        date_str: 日期格式 YYYYMMDD (例如: 20241223)

    Returns:
        包含三大法人買賣金額資料的字典
    """
    # API端點
    url = "https://www.twse.com.tw/rwd/zh/fund/BFI82U"

    # 請求參數
    params = {
        'dayDate': date_str,
        'type': 'day',
        'response': 'json'
    }

    # 設定Headers模擬瀏覽器請求
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        # 發送GET請求
        print(f"正在抓取 {date_str} 的三大法人買賣金額統計表...")
        response = requests.get(url, params=params, headers=headers, verify=False)
        response.raise_for_status()

        # 解析JSON資料
        data = response.json()

        # 檢查資料是否存在
        if data.get('stat') != 'OK':
            print(f"查無資料: {data.get('stat', '未知錯誤')}")
            return None

        # 顯示標題
        print("\n" + "=" * 100)
        print(f"標題: {data.get('title', 'N/A')}")
        print("=" * 100)

        # 顯示欄位名稱
        if 'fields' in data:
            print("\n欄位說明:")
            for i, field in enumerate(data['fields'], 1):
                print(f"  {i}. {field}")

        # 取得資料
        records = data.get('data', [])

        print(f"\n總共抓取到 {len(records)} 筆資料:")
        print("=" * 100)

        # 逐筆顯示資料
        for idx, record in enumerate(records, 1):
            print(f"\n第 {idx} 筆資料:")
            if 'fields' in data:
                for i, (field, value) in enumerate(zip(data['fields'], record)):
                    print(f"  {field}: {value}")
            else:
                for i, value in enumerate(record):
                    print(f"  欄位{i}: {value}")
            print("-" * 100)

        # 顯示註記
        if 'notes' in data and data['notes']:
            print("\n" + "=" * 100)
            print("註記:")
            print("=" * 100)
            for i, note in enumerate(data['notes'], 1):
                print(f"{i}. {note}")

        # 顯示單位提示
        if 'hints' in data:
            print(f"\n{data['hints']}")

        return data

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
    # 使用最近的交易日期作為範例
    # 民國113年12月23日 = 西元2024年12月23日
    # 日期格式: YYYYMMDD
    date = "20241223"

    print("=" * 100)
    print("台灣證券交易所 - 三大法人買賣金額統計表爬蟲（日報）")
    print("=" * 100)

    result = fetch_institutional_trading_amount(date)

    if result:
        print("\n✓ 資料抓取成功！")
    else:
        print("\n✗ 資料抓取失敗，請檢查日期或網路連線")
