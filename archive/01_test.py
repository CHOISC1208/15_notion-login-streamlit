import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.kintone_fetch import fetch_kintone_data
from src.utils.df_cleaner import clean_dataframe


cassette_info = {
    "name": "test",
    "domain": "qhlwv3k5c4j1",  # サブドメイン部分のみ
    "app_id": "14",
    "api_token": "CCte4r7VzGbpOqRPFSZzJBiEcj6yr4yphOiJVo4M",
    "query": ""
}

df = fetch_kintone_data(
    domain=cassette_info["domain"],
    api_token=cassette_info["api_token"],
    app_id=cassette_info["app_id"],
    query=cassette_info["query"]
)

# 型の自動検出
#suggested_types = auto_detect_types(df)
#print("推奨される型設定:", suggested_types)

# 型設定と順序を同時に指定
column_config = {
    '$id': 'float',
    '使用部署': 'str',
    '仕入れ先': 'str',
    '税込購入金額': 'float',
    '購入履歴': 'str',
    '受入日': 'date',
    '合計購入金額': 'float',
    '消費税': 'float',
    '作成日時': 'str',
    '更新日時': 'str',
    '更新者_name': 'str',
    '作成者_name': 'str'
}

# データフレームのクレンジング
result_df = clean_dataframe(df, column_config=column_config)