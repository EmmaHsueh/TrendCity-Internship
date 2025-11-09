import requests
from bs4 import BeautifulSoup
import json
import urllib3

# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def fetch_twse_html_data(date_str):
    """
    使用HTML標籤抓取台灣證券交易所三大法人買賣超日報

    Args:
        date_str: 日期格式 YYYYMMDD (例如: 20251023)

    Returns:
        包含表頭和資料的字典
    """
    # 使用相同的API端點，但這次我們解析返回的HTML
    url = "https://www.twse.com.tw/rwd/zh/fund/T86"

    # 請求參數
    params = {
        'date': date_str,
        'selectType': 'ALL',
        'response': 'html'  # 要求返回HTML格式
    }

    # 設定Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        print(f"正在抓取 {date_str} 的三大法人買賣超資料（HTML格式）...")
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
            "data": data_rows[:10] if len(data_rows) > 10 else data_rows  # 取前10筆
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
        print(f"資料內容（前10筆）:")
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
        output_file = f"twse_html_data_{date_str}.json"
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


if __name__ == "__main__":
    # 民國114年10月23日 = 2025年10月23日
    # 日期格式: YYYYMMDD
    date = "20251023"

    print("=" * 100)
    print("台灣證券交易所 - 三大法人買賣超日報爬蟲 (HTML解析版本)")
    print("=" * 100)

    result = fetch_twse_html_data(date)

    if result:
        print("\n✓ 資料抓取成功！")
        print(f"表頭列數: {len(result['params']['headers'])}")
        print(f"資料筆數: {len(result['data'])}")
    else:
        print("\n✗ 資料抓取失敗，請檢查日期或網路連線")
