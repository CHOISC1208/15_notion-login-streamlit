# Notion-Streamlit Data Viewer

## 概要

**Notion-Streamlit Data Viewer** は、Notion データベースと連携し、データ処理の過程を「カセット」として管理し、画面上で切り替えて表示できるデータ処理プラットフォームです。

このアプリは、**Streamlit** をフロントエンドに使用し、**Notion** をデータベースとして活用します。また、**Heroku** を利用して簡単にデプロイが可能です。

## 特徴

- **Notion 認証連携**: Notion のデータベースを認証情報として使用し、ユーザー管理を簡単に行えます。
- **カセット方式のデータ処理**: データ処理ロジックを「カセット」として管理し、簡単に切り替え可能。
- **インタラクティブなデータ表示**: AgGrid を使用したデータの動的な可視化。
- **Heroku に簡単デプロイ**: クラウド環境での運用がスムーズ。

---

## 初期設定

### 1. Notion でログイン用のデータベースを作成

[こちらのテンプレート](https://www.notion.so/03_login-1b0f4e3e47b180839a57cd35885b4e75?pvs=21) をコピーし、Notion にデータベースを作成してください。

### 2. `.env` に Notion の API 情報を設定

アプリディレクトリ内（`app.py` と同じディレクトリ）に `.env` ファイルを作成し、以下の情報を記述してください。

```ini
# Notion API トークンとデータベース ID
NOTION_API_TOKEN='honyaraara'  # ここにAPIトークンを入力
DATABASE_ID='hogehoge'  # ここにデータベースIDを入力
```

### 3. `data` ディレクトリにカセットを作成

データ処理のスクリプトは `src/data` ディレクトリに保存します。結果を `result_df` として出力すれば、画面に表示されます。

### 4. Heroku で接続設定

### 5. Heroku の環境変数を設定

Heroku の **Settings → Config Vars** に `.env` の内容を登録します。

| Key | Value |
|------|------|
| NOTION_API_TOKEN | `honyaraara` |
| DATABASE_ID | `hogehoge` |

### 6. Heroku にデプロイ

```sh
git add .
git commit -m "Deploy Notion-Streamlit Data Viewer"
git push heroku main
```

---

## 現在の構成

```plaintext
.
├── Procfile
├── README.md
├── app.py
├── requirements.txt
├── runtime.txt
├── setup.sh
└── src
    ├── data  # カセット管理
    │   ├── 01_白十字仕入れ記録.py
    └── utils  # 各種ユーティリティ
        ├── auth_manager.py  # ログイン処理
        ├── grid_config.py  # AgGrid 設定
        ├── kintone_fetch_v3.py  # Kintone データ取得
        └── notion_fetch.py  # Notion DB を認証情報として活用
```

---

## AgGrid の設定方法

データの可視化には **AgGrid** を使用しています。

### **`configure_grid` の設定**

```python
from st_aggrid import GridOptionsBuilder, JsCode

def configure_grid(df):
    """AgGrid の設定を構成する関数"""
    gb = GridOptionsBuilder.from_dataframe(df)
    
    # 1. 並び替え機能
    gb.configure_default_column(sortable=True)
    
    # 2. フィルタリング機能
    gb.configure_default_column(filterable=True)
    
    # 3. グループ化機能
    gb.configure_default_column(
        groupable=True,
        enableRowGroup=True,
        aggFunc='sum'
    )
    
    # 4. ピボットテーブル機能
    gb.configure_default_column(
        enablePivot=True,
        enableValue=True
    )
    
    # 5. エクスポート機能（CSVとExcel）
    gb.configure_grid_options(
        enableRangeSelection=True,
        domLayout='normal',
        suppressExcelExport=False,
        suppressCsvExport=True
    )
    
    # 6. カラムの表示/非表示切り替え
    gb.configure_side_bar(
        defaultToolPanel='columns',
        columns_panel=True
    )
    
    # 7. ページネーション設定
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=15)
    
    # 8. 選択機能
    gb.configure_selection('multiple', use_checkbox=False)
    
    return gb.build()
```

この設定により、データのフィルタリングやピボット分析、エクスポートが簡単に行えます。

