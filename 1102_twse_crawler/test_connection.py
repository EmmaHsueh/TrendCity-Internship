#!/usr/bin/env python3
"""
測試 MongoDB 連線的腳本
"""
from pymongo import MongoClient
from config import get_mongo_uri, get_db_name

def test_connection():
    """測試 MongoDB 連線"""
    print("=" * 50)
    print("MongoDB 連線測試")
    print("=" * 50)

    try:
        # 讀取設定
        uri = get_mongo_uri()
        db_name = get_db_name()

        print(f"\n[設定資訊]")
        print(f"MongoDB URI: {uri}")
        print(f"資料庫名稱: {db_name}")

        # 建立連線
        print(f"\n[連線測試]")
        print("正在連線到 MongoDB...")
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # 測試連線
        client.admin.command('ping')
        print("✓ 連線成功！")

        # 顯示伺服器資訊
        server_info = client.server_info()
        print(f"\n[伺服器資訊]")
        print(f"MongoDB 版本: {server_info['version']}")

        # 列出現有的資料庫
        print(f"\n[現有資料庫]")
        databases = client.list_database_names()
        for db in databases:
            print(f"  - {db}")

        # 檢查目標資料庫
        print(f"\n[目標資料庫: {db_name}]")
        db = client[db_name]
        collections = db.list_collection_names()

        if collections:
            print(f"現有 collections:")
            for coll in collections:
                count = db[coll].count_documents({})
                print(f"  - {coll}: {count} 筆資料")
        else:
            print("尚無 collections（第一次執行爬蟲時會自動建立）")

        print("\n" + "=" * 50)
        print("測試完成！MongoDB 已準備就緒")
        print("=" * 50)

        return True

    except Exception as e:
        print(f"\n✗ 連線失敗: {e}")
        print("\n[可能的解決方式]")
        print("1. 確認 MongoDB 服務是否正在運行:")
        print("   brew services list | grep mongodb")
        print("2. 如果未運行，啟動服務:")
        print("   brew services start mongodb-community")
        print("3. 檢查 .env 檔案中的 MONGODB_URI 設定是否正確")
        return False

if __name__ == "__main__":
    test_connection()
