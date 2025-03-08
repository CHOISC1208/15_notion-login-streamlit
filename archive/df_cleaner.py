import pandas as pd
import numpy as np
from datetime import datetime
import re

def clean_dataframe(df, column_config=None, column_order=None, date_format="%Y-%m-%d", use_config_as_order=True):
    """
    データフレームをクレンジングするための関数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        クレンジング対象のデータフレーム
    column_config : dict, optional
        カラムの型変換設定。例: {'カラム名': 'int', 'カラム名2': 'float'}
    column_order : list, optional
        カラムの表示順序。指定されたカラムが先頭に来る
    date_format : str, optional
        日付型変換時のフォーマット。デフォルトは'%Y-%m-%d'
    use_config_as_order : bool, optional
        column_configのキーの順番をカラム順序として使用するかどうか
        
    Returns:
    --------
    pandas.DataFrame
        クレンジング後のデータフレーム
    """
    # 元のデータフレームをコピー
    cleaned_df = df.copy()
    
    # カラム名の正規化（全角スペースを半角に、前後の空白を削除）
    cleaned_df.columns = [str(col).strip().replace('　', ' ') for col in cleaned_df.columns]
    
    # 型変換の処理
    if column_config:
        for column, dtype in column_config.items():
            if column in cleaned_df.columns:
                try:
                    if dtype == 'int':
                        # 数値に変換できない値をNaNに変換してから整数型に
                        cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors='coerce').fillna(0).astype(int)
                    elif dtype == 'float':
                        # 数値文字列（カンマ付き等）を浮動小数点に
                        if cleaned_df[column].dtype == 'object':
                            cleaned_df[column] = cleaned_df[column].replace('[\¥,$,円,comma]', '', regex=True)
                        cleaned_df[column] = pd.to_numeric(cleaned_df[column], errors='coerce')
                    elif dtype == 'date':
                        # 日付型への変換
                        cleaned_df[column] = pd.to_datetime(cleaned_df[column], errors='coerce', format=date_format)
                    elif dtype == 'str':
                        # 文字列型への変換（NaNはそのまま）
                        cleaned_df[column] = cleaned_df[column].astype(str).replace('nan', np.nan)
                    elif dtype == 'bool':
                        # ブール型への変換
                        cleaned_df[column] = cleaned_df[column].map({'true': True, 'True': True, '1': True, 
                                                                     'false': False, 'False': False, '0': False})
                    else:
                        # その他の型指定
                        cleaned_df[column] = cleaned_df[column].astype(dtype)
                except Exception as e:
                    print(f"カラム '{column}' の型変換中にエラーが発生しました: {e}")
    
    # カラムの順序変更
    if column_order:
        # 指定されたカラムが存在するか確認
        existing_columns = [col for col in column_order if col in cleaned_df.columns]
        # 指定されていないカラムを取得
        remaining_columns = [col for col in cleaned_df.columns if col not in existing_columns]
        # カラムを並べ替え
        cleaned_df = cleaned_df[existing_columns + remaining_columns]
    # column_configのキーの順番をカラム順序として使用
    elif column_config and use_config_as_order:
        # 設定に存在するカラムのみを抽出
        config_columns = [col for col in column_config.keys() if col in cleaned_df.columns]
        # 設定に存在しないカラムを取得
        remaining_columns = [col for col in cleaned_df.columns if col not in config_columns]
        # カラムを並べ替え
        cleaned_df = cleaned_df[config_columns + remaining_columns]
    
    return cleaned_df


def extract_money_value(df, column):
    """
    金額カラムから数値のみを抽出する関数
    
    Parameters:
    -----------
    df : pandas.DataFrame
        対象のデータフレーム
    column : str
        金額が格納されているカラム名
        
    Returns:
    --------
    pandas.Series
        数値のみが抽出された金額シリーズ
    """
    if column not in df.columns:
        raise ValueError(f"カラム '{column}' がデータフレームに存在しません")
    
    # 金額表記から数値のみを抽出
    extracted = df[column].astype(str).str.replace(r'[^\d.-]', '', regex=True)
    return pd.to_numeric(extracted, errors='coerce')
