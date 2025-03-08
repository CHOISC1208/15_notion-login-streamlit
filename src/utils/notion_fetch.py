import os
from dotenv import load_dotenv
import requests

# .envファイルを読み込む
load_dotenv()

# 環境変数を取得
NOTION_API_TOKEN = os.getenv('NOTION_API_TOKEN')
DATABASE_ID = os.getenv('DATABASE_ID')

# APIリクエストのヘッダーを設定
headers = {
    'Authorization': f'Bearer {NOTION_API_TOKEN}',
    'Content-Type': 'application/json',
    'Notion-Version': '2022-06-28'
}

# データベースクエリのURLを設定
url = f'https://api.notion.com/v1/databases/{DATABASE_ID}/query'

# Notionからデータを取得する関数
def fetch_notion_data():
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        credentials = {}
        for page in data['results']:
            # 各プロパティを取得
            try:
                name = page['properties']['Name']['title'][0]['plain_text']
                email = page['properties']['email']['email']
                username = page['properties']['username']['rich_text'][0]['plain_text']
                password = page['properties']['password']['rich_text'][0]['plain_text']
                
                # Streamlit Authenticator用の形式で保存
                credentials[username] = {
                    'name': name,
                    'email': email,
                    'password': password
                }
            except (KeyError, IndexError) as e:
                print(f"Error extracting data for a page: {e}")
        return credentials
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# メイン処理
if __name__ == "__main__":
    credentials = fetch_notion_data()
    if credentials:
        print("Fetched Credentials:")
        print(credentials)
    else:
        print("Failed to fetch data from Notion.")