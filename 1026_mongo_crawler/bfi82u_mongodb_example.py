"""
BFI82U MongoDB整合範例

這個腳本展示如何使用 bfi82u_html_crawler.py 的MongoDB功能
"""

from pymongo import MongoClient
import time
from bfi82u_html_crawler import fetch_bfi82u_html_data, save_to_mongo


def example_single_date():
    """範例一：抓取單一日期並儲存到MongoDB"""
    print("=" * 80)
    print("範例一：抓取單一日期並儲存到MongoDB")
    print("=" * 80)

    date = "20241223"
    result = fetch_bfi82u_html_data(date)

    if result:
        save_to_mongo(result)
        print(f"✓ {date} 資料已成功儲存到MongoDB")


def example_batch_dates():
    """範例二：批次抓取多個日期"""
    print("\n" + "=" * 80)
    print("範例二：批次抓取多個日期")
    print("=" * 80)

    dates = ['20241220', '20241223', '20241224']

    for date in dates:
        print(f"\n處理日期: {date}")
        result = fetch_bfi82u_html_data(date)

        if result:
            save_to_mongo(result)
            print(f"✓ {date} 資料已儲存")
        else:
            print(f"✗ {date} 資料抓取失敗")

        time.sleep(3)  # 避免請求過於頻繁

    print("\n批次處理完成！")


def example_query_mongo():
    """範例三：查詢MongoDB中的資料"""
    print("\n" + "=" * 80)
    print("範例三：查詢MongoDB中的資料")
    print("=" * 80)

    client = MongoClient('mongodb://localhost:27017/')
    db = client['twse_db']
    collection = db['bfi82u_records']

    # 查詢特定日期的所有資料
    date = '20241223'
    print(f"\n查詢 {date} 的資料：")
    records = collection.find({'query_date': date})

    for record in records:
        print(f"  {record['單位名稱']}: 買賣差額 = {record['買賣差額']}")

    # 查詢外資買賣差額
    print(f"\n查詢外資買賣差額：")
    foreign_record = collection.find_one({
        'query_date': date,
        '單位名稱': '外資及陸資(不含外資自營商)'
    })

    if foreign_record:
        print(f"  日期: {foreign_record['query_date']}")
        print(f"  買進金額: {foreign_record['買進金額']}")
        print(f"  賣出金額: {foreign_record['賣出金額']}")
        print(f"  買賣差額: {foreign_record['買賣差額']}")

    client.close()


def example_aggregate_analysis():
    """範例四：使用MongoDB聚合分析"""
    print("\n" + "=" * 80)
    print("範例四：MongoDB聚合分析 - 查看資料庫統計")
    print("=" * 80)

    client = MongoClient('mongodb://localhost:27017/')
    db = client['twse_db']
    collection = db['bfi82u_records']

    # 統計總資料筆數
    total_count = collection.count_documents({})
    print(f"\n總資料筆數: {total_count}")

    # 統計有多少個不同的查詢日期
    distinct_dates = collection.distinct('query_date')
    print(f"不同查詢日期數: {len(distinct_dates)}")
    print(f"日期列表: {sorted(distinct_dates)}")

    # 查詢最新的資料
    latest_record = collection.find_one(
        sort=[('query_date', -1), ('inserted_at', -1)]
    )

    if latest_record:
        print(f"\n最新資料日期: {latest_record['query_date']}")
        print(f"插入時間: {latest_record['inserted_at']}")

    client.close()


def example_custom_mongo_config():
    """範例五：使用自訂MongoDB配置"""
    print("\n" + "=" * 80)
    print("範例五：使用自訂MongoDB配置")
    print("=" * 80)

    date = "20241223"
    result = fetch_bfi82u_html_data(date)

    if result:
        # 使用自訂的資料庫和集合名稱
        save_to_mongo(
            result,
            mongo_uri="mongodb://localhost:27017/",
            db_name="custom_db",
            collection_name="custom_collection"
        )
        print(f"✓ 資料已儲存到自訂資料庫")


if __name__ == "__main__":
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "BFI82U MongoDB整合範例" + " " * 35 + "║")
    print("╚" + "=" * 78 + "╝")
    print()

    # 執行範例（取消註解以執行）

    # 範例一：單一日期
    # example_single_date()

    # 範例二：批次處理
    # example_batch_dates()

    # 範例三：查詢資料
    example_query_mongo()

    # 範例四：聚合分析
    example_aggregate_analysis()

    # 範例五：自訂配置
    # example_custom_mongo_config()

    print("\n✓ 範例執行完成！")
    print("\n提示：修改 __main__ 區塊中的註解來執行不同的範例")
