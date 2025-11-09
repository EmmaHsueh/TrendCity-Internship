import json

# 讀取原始文件
with open('bfi82u_html_data_20241223.json', 'r', encoding='utf-8') as f:
    original_data = json.load(f)

# 獲取表頭（第二行才是實際的列名）
headers = original_data['params']['headers'][1]

# 轉換數據：將每行數組轉換成對象
converted_data = []
for row in original_data['data']:
    # 創建一個字典，將表頭和數據對應起來
    obj = {}
    for i, header in enumerate(headers):
        obj[header] = row[i]
    converted_data.append(obj)

# 保存轉換後的數據
output = {
    "query_date": original_data['params']['query_date'],
    "title": original_data['params']['headers'][0][0],
    "data": converted_data
}

# 輸出到新文件
output_filename = 'bfi82u_html_data_20241223_converted.json'
with open(output_filename, 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"✓ 轉換完成！")
print(f"✓ 輸出文件：{output_filename}")
print(f"\n轉換後數據預覽：")
print(json.dumps(output, ensure_ascii=False, indent=2))
