from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import json
import time

def fetch_twse_html_data(date_str):
    """
    使用HTML標籤抓取台灣證券交易所三大法人買賣超日報

    Args:
        date_str: 日期格式 YYYY/MM/DD (例如: 2025/10/23)

    Returns:
        包含表頭和資料的字典
    """
    # 設定Chrome選項
    chrome_options = Options()
    chrome_options.add_argument('--headless')  # 無頭模式
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

    driver = None

    try:
        print(f"正在啟動瀏覽器...")
        driver = webdriver.Chrome(options=chrome_options)

        # 訪問網頁
        url = "https://www.twse.com.tw/zh/trading/foreign/t86.html"
        print(f"正在訪問網頁: {url}")
        driver.get(url)

        # 等待頁面載入
        time.sleep(3)

        # 輸入查詢日期
        print(f"設定查詢日期: {date_str}")
        date_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "input_date"))
        )

        # 清空並輸入日期
        date_input.clear()
        driver.execute_script(f"arguments[0].value = '{date_str}';", date_input)

        # 點擊查詢按鈕
        print("點擊查詢按鈕...")
        search_button = driver.find_element(By.CSS_SELECTOR, "button.btn-primary[type='button']")
        driver.execute_script("arguments[0].click();", search_button)

        # 等待表格載入
        print("等待數據載入...")
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "main table tbody tr"))
        )

        time.sleep(2)  # 額外等待確保數據完全載入

        # 抓取<thead>中的表頭資料
        print("正在抓取表頭資料...")
        thead_rows = driver.find_elements(By.CSS_SELECTOR, "main table thead tr")
        headers = []

        for row in thead_rows:
            row_data = []
            ths = row.find_elements(By.TAG_NAME, "th")
            for th in ths:
                row_data.append(th.text.strip())
            if row_data:  # 只加入非空的行
                headers.append(row_data)

        print(f"找到 {len(headers)} 列表頭")

        # 抓取<tbody>中的所有<tr>內所有<td>的資料
        print("正在抓取表格資料...")
        tbody_rows = driver.find_elements(By.CSS_SELECTOR, "main table tbody tr")

        data_rows = []
        for row in tbody_rows:
            row_data = []
            tds = row.find_elements(By.TAG_NAME, "td")
            for td in tds:
                row_data.append(td.text.strip())
            if row_data:  # 只加入非空的行
                data_rows.append(row_data)

        print(f"總共抓取到 {len(data_rows)} 筆資料")

        # 組織成JSON格式
        result = {
            "params": {
                "query_date": date_str,
                "headers": headers
            },
            "data": data_rows[:10] if len(data_rows) > 10 else data_rows  # 取前10筆
        }

        # 顯示結果
        print("\n" + "=" * 100)
        print("表頭資訊:")
        print("=" * 100)
        for idx, header_row in enumerate(headers):
            print(f"表頭第{idx + 1}列: {header_row}")

        print("\n" + "=" * 100)
        print(f"資料內容（前10筆）:")
        print("=" * 100)

        for idx, row in enumerate(result["data"], 1):
            print(f"\n第 {idx} 筆資料:")
            for i, value in enumerate(row):
                # 如果有表頭，使用表頭名稱
                if headers and len(headers[-1]) > i:  # 使用最後一列表頭
                    print(f"  {headers[-1][i]}: {value}")
                else:
                    print(f"  欄位{i}: {value}")
            print("-" * 100)

        # 儲存為JSON檔案
        output_file = f"twse_data_{date_str.replace('/', '')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n✓ 資料已儲存至: {output_file}")

        return result

    except Exception as e:
        print(f"發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        return None

    finally:
        if driver:
            print("\n關閉瀏覽器...")
            driver.quit()


if __name__ == "__main__":
    # 民國114年10月23日 = 2025年10月23日
    # 日期格式: YYYY/MM/DD
    date = "2025/10/23"

    print("=" * 100)
    print("台灣證券交易所 - 三大法人買賣超日報爬蟲 (HTML版本)")
    print("=" * 100)

    result = fetch_twse_html_data(date)

    if result:
        print("\n✓ 資料抓取成功！")
        print(f"總共抓取到 {len(result['data'])} 筆資料")
    else:
        print("\n✗ 資料抓取失敗，請檢查日期或網路連線")
