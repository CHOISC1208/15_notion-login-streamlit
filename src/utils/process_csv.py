import pandas as pd
import re

def process_csv(raw_df, file_name):
    # ファイル名から日付を抽出
    date_match = re.search(r'\d{4}-\d{2}-\d{2}', file_name)

    if date_match:
        date_str = date_match.group()
        date_value = pd.to_datetime(date_str)
    else:
        date_value = pd.to_datetime("2023-01-01")  # デフォルト日付を設定

    # 1行目と2行目を抽出
    header_row_1 = raw_df.iloc[0]
    header_row_2 = raw_df.iloc[1]

    # 新しいカラム名を作成
    new_columns = []
    prev_col1 = None
    for col1, col2 in zip(header_row_1, header_row_2):
        if pd.isna(col1):
            col1 = prev_col1
        else:
            prev_col1 = col1
        if col2:
            new_columns.append(f"{col1}%{col2}")
        else:
            new_columns.append(col1)

    # 5列目まではそのまま使用
    new_columns[:5] = ['部門番号', '部門名', '商品番号', '商品名', '基本価格']

    # DataFrameのカラム名を更新
    raw_df.columns = new_columns

    # 1行目と2行目を削除
    raw_df = raw_df.iloc[2:].reset_index(drop=True)

    # ピボットするための準備
    pivoted_df = raw_df.melt(id_vars=['部門番号', '部門名', '商品番号', '商品名', '基本価格'],
                            var_name='区分',
                            value_name='値')

    # '値'が '-' の行を削除
    filtered_df = pivoted_df[pivoted_df['値'] != '-']

    # '値'を数値型に変換（必要に応じて）
    filtered_df['値'] = pd.to_numeric(filtered_df['値'], errors='coerce')

    # '区分' カラムを '%' で分割
    split_columns = filtered_df['区分'].str.split('%', expand=True)
    split_columns.columns = ['店舗', '区分']

    # 新しいカラムを元のDataFrameに追加
    filtered_df = pd.concat([filtered_df.drop(columns=['区分']), split_columns], axis=1)

    # カラムの順番を変更
    filtered_df = filtered_df[['部門番号', '部門名', '商品番号', '商品名', '基本価格', '店舗', '区分', '値']]

    # 日付カラムを追加
    filtered_df['date'] = date_value

    # 店舗が「合計」以外の行をフィルタリング
    filtered_df = filtered_df[filtered_df['店舗'] != '合計']

    # ピボット処理
    pivoted_df = filtered_df.pivot_table(index=['date', '部門番号', '部門名', '商品番号', '商品名', '基本価格', '店舗'],
                                        columns='区分',
                                        values='値',
                                        aggfunc='sum')

    # カラムの順番を整理
    pivoted_df = pivoted_df[['販売', '出荷', 'ロス', 'セ/崩/解', '在庫']]

    # DataFrameをリセット
    pivoted_df = pivoted_df.reset_index()

    return pivoted_df




# CSVファイルのパスを指定
#file_path = r'/Users/choisc/Library/Mobile Documents/com~apple~CloudDocs/github/15_notion-login-streamlit/archive/全店舗確認_2025-03-28-2.csv'

# CSVファイルを読み込み
#try:
#    raw_df = pd.read_csv(file_path, encoding='shift-jis', header=None)
#except FileNotFoundError:
#    print("ファイルが見つかりませんでした。")
#    exit()

# 処理関数を実行
#processed_df = process_csv(raw_df, file_path)

# 結果を新しいCSVファイルに保存
#processed_df.to_csv('/Users/choisc/Library/Mobile Documents/com~apple~CloudDocs/github/15_notion-login-streamlit/archive/20250328.csv', index=False)
