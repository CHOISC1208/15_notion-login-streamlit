import requests
import pandas as pd

class KintoneDataManager:
    def __init__(self, api_settings):
        self.base_url = api_settings['base_url']
        self.configs = api_settings['configs']
        self.dataframes = None

    # 以下は元々のコードそのままでOK
    def fetch_data(self):
        """すべてのデータを取得して処理する"""
        print("\nkintone APIの制限事項:")
        print("=" * 40)
        print("- 1回のリクエストの最大取得件数: 500件")
        print("- offset上限値: 10,000件")
        print("- 検索結果上限: 100,000件")
        print("=" * 40)
        
        all_data = self._fetch_all_kintone_data()
        self.dataframes = self._merge_dataframes(all_data)
        
        print("\n取得したデータフレーム一覧:")
        print("=" * 40)
        for df_name, df in self.dataframes.items():
            record_count = len(df)
            status = "⚠️ 制限に近い" if record_count > 9000 else "✓"
            print(f"- {df_name:<30} ({record_count:>6,} 行) {status}")
        print("=" * 40 + "\n")
        
        return self
    
    def get_dataframe(self, name):
        """単一のデータフレームを取得"""
        if self.dataframes is None:
            raise ValueError("データフレームが初期化されていません。fetch_data()を先に実行してください。")
        return self.dataframes.get(name.strip())

    def get_multiple_dataframes(self, *names):
        """複数のデータフレームを一度に取得"""
        if self.dataframes is None:
            raise ValueError("データフレームが初期化されていません。fetch_data()を先に実行してください。")
        return [self.get_dataframe(name) for name in names]
    
    def get_available_dataframes(self):
        """利用可能なデータフレーム名の一覧を返す"""
        if self.dataframes is None:
            raise ValueError("データフレームが初期化されていません。fetch_data()を先に実行してください。")
        return list(self.dataframes.keys())

    def show_dataframe_info(self):
        """データフレームの詳細情報を表示"""
        print("\n利用可能なデータフレーム一覧:")
        print("=" * 40)
        for df_name, df in self.dataframes.items():
            print(f"- {df_name:<30} ({len(df):>6,} 行)")
        print("=" * 40 + "\n")

    # 以下、前回修正したサブテーブル処理関数
    def _process_main_field(self, main_row, key, value):
        if value['type'] in ['CREATOR', 'MODIFIER']:
            main_row[f'{key}_code'] = value['value']['code']
            main_row[f'{key}_name'] = value['value']['name']
        elif isinstance(value['value'], dict):
            for subkey, subvalue in value['value'].items():
                main_row[f'{key}_{subkey}'] = subvalue
        else:
            main_row[key] = value['value']

    def _process_subtable(self, record, key, value, sub_data_dict):
        subtable = value['value']
        if key not in sub_data_dict:
            sub_data_dict[key] = []
        
        for subrecord in subtable:
            sub_row = {}
            # サブテーブル内の各フィールドを展開
            for field_name, field_value in subrecord['value'].items():
                if isinstance(field_value, dict) and 'value' in field_value:
                    # フィールド名をそのままキーとして値を取得
                    sub_row[field_name] = field_value['value']
                else:
                    # 予期しない形式の場合、そのまま格納
                    sub_row[field_name] = field_value

            # メインレコードとの紐付け用にメインIDを追加
            sub_row['main_id'] = record['$id']['value']
            # サブテーブル内レコードIDも念のため追加
            sub_row['sub_id'] = subrecord['id']

            # 結果を追加
            sub_data_dict[key].append(sub_row)

    # 以下は変更不要（元々のコード）
    def _fetch_kintone_records(self, app_no, apitoken, query='', limit=500):
        headers = {"X-Cybozu-API-Token": apitoken}
        offset = 0
        records = []
        
        while True:
            params = {
                "app": app_no,
                "query": query + f" limit {limit} offset {offset}"
            }
            
            ret = requests.get(self.base_url, headers=headers, params=params)
            ret.raise_for_status()
            
            batch_records = ret.json().get('records', [])
            
            if not batch_records:
                break
                
            records.extend(batch_records)
            
            offset += limit
        
        return self._process_records(records)

    def _process_records(self, records):
        main_data = []
        sub_data_dict = {}
        
        for record in records:
            main_row = {}
            for key, value in record.items():
                if value['type'] == 'SUBTABLE':
                    self._process_subtable(record, key, value, sub_data_dict)
                else:
                    self._process_main_field(main_row, key, value)
            main_data.append(main_row)
        
        df_main = pd.DataFrame(main_data)
        
        df_sub_tables = {
            f'df_sub_{i+1}': pd.DataFrame(data) 
            for i, (key,data) in enumerate(sub_data_dict.items())
        }
        
        return df_main, df_sub_tables

    def _fetch_all_kintone_data(self):
      return {key: {'main': main_df, 'sub_tables': sub_dfs}
              for key, config in self.configs.items()
              for main_df, sub_dfs in [self._fetch_kintone_records(
                  config['app_no'], config['apitoken'], config['query'])]}
    
    def _merge_dataframes(self, all_data):
      merged_dataframes={}
      for config_name,data in all_data.items():
          merged_dataframes[f"{config_name}_main"]=data['main']
          for sub_name,sub_df in data['sub_tables'].items():
              merged_df_name=f"{config_name}_{sub_name}"
              merged_df=sub_df.merge(data['main'],how='left',left_on='main_id',right_on='$id')
              merged_dataframes[merged_df_name]=merged_df
      
      return merged_dataframes
