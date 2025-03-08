import requests
import pandas as pd

def fetch_kintone_data(domain, api_token, app_id, query=""):
    """kintoneからデータを取得してDataFrameに変換する関数"""
    # kintoneのURLを正しく構築
    base_url = f"https://{domain}.cybozu.com/k/v1/records.json"
    headers = {"X-Cybozu-API-Token": api_token}
        
    all_records = []
    offset = 0
    limit = 500
    total_records = 0
    
    print(f"レコード取得中... (limit={limit})")
    while True:
        params = {
            "app": app_id,
            "query": f"{query} limit {limit} offset {offset}"
        }
        
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # エラー時に例外を発生
        
        batch_records = response.json().get('records', [])
        if not batch_records:
            break
            
        all_records.extend(batch_records)
        total_records += len(batch_records)
        print(f"- {offset}～{offset + len(batch_records)}件目を取得 (現在合計: {total_records}件)")
        
        offset += limit
        if len(batch_records) < limit:
            break
    
    print(f"取得完了: 合計{total_records}件\n")
    
    # レコードをフラット化してDataFrameに変換
    main_data = []
    
    for record in all_records:
        # メインテーブルのデータ処理
        main_row = {}
        for key, value in record.items():
            if value['type'] in ['CREATOR', 'MODIFIER']:
                main_row[f'{key}_code'] = value['value']['code']
                main_row[f'{key}_name'] = value['value']['name']
            elif isinstance(value['value'], dict) and 'code' in value['value']:
                main_row[f'{key}_code'] = value['value']['code']
                main_row[f'{key}_name'] = value['value']['name']
            elif isinstance(value['value'], dict):
                for subkey, subvalue in value['value'].items():
                    main_row[f'{key}_{subkey}'] = subvalue
            else:
                main_row[key] = value['value']
        main_data.append(main_row)
    
    return pd.DataFrame(main_data)