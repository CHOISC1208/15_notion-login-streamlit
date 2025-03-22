import streamlit as st
from src.utils.auth_manager import AuthManager
from src.utils.notion_fetch import fetch_notion_data
import importlib.util
from pathlib import Path
from st_aggrid import AgGrid

from src.utils.grid_config import configure_grid
from src.utils.auth_manager import AuthManager


# ページ設定
st.set_page_config(
    page_title="白十字様Datastation",
    layout="wide"
)

# Notionからユーザーデータを取得
users_data = fetch_notion_data()

# 認証マネージャーの初期化
auth_manager = AuthManager(users_data)
auth_manager.initialize_session_state()

# カスタムCSS
st.markdown("""
    <style>
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin: 0 auto;
        max-width: 400px;
        padding-top: 50px;
    }
    div[data-testid="stForm"] {
        width: 100%;
        max-width: 350px;
        margin: 0 auto;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    div.stButton > button {
        background-color: #FFA500; /* オレンジ色 */
        color: black; /* 黒文字 */
        font-weight: bold; /* 太字 */
        width: 100%; /* 横幅いっぱいに広げる */
    }
    div.stTextInput > div > div > input {
        padding: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# ログイン状態の確認
if not auth_manager.is_logged_in:
    # ログイン画面のコンテナを作成
    login_container = st.container()
    
    with login_container:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        
        # ログインフォーム作成
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True)
            
            if submitted:
                if auth_manager.login(username, password):
                    st.success("ログインに成功しました")
                    st.rerun() 
                else:
                    st.error("ユーザー名またはパスワードが間違っています")
        
        st.markdown('</div>', unsafe_allow_html=True)
else:
    # ログイン成功時の処理（メイン画面）
    with st.sidebar:
        st.write(f"ログインユーザー: {auth_manager.current_user}")
        
        if st.button("ログアウト", use_container_width=True):
            auth_manager.logout()
            st.rerun() 

    # タイトル
    st.title("kintoneデータ活用プラットフォーム")

    # カセットファイルのパス
    cassette_dir = Path("src/data")
    cassette_files = list(cassette_dir.glob("*.py"))
    cassette_names = [f.stem for f in cassette_files]

    if not cassette_names:
        st.error("カセットが見つかりません")
        st.stop()

    # カセット選択と実行ボタンを横に並べる
    st.markdown('<div class="cassette-selection-area">', unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # カセット選択
        selected_cassette = st.selectbox("カセットを選択", cassette_names)
    
    with col2:
        # 実行ボタン（上部に余白を追加して垂直方向に揃える）
        st.markdown("<div style='padding-top: 32px;'></div>", unsafe_allow_html=True)
        execute_button = st.button("データ取得・処理実行", key="execute_button", help="選択したカセットを実行します")
    
    st.markdown('</div>', unsafe_allow_html=True)

    # 実行ボタンが押された場合の処理
    if execute_button:
        with st.spinner("データを取得・処理中..."):
            try:
                # 選択されたカセットファイルのパス
                cassette_path = cassette_dir / f"{selected_cassette}.py"
                
                # カセットファイルをモジュールとして動的にインポート
                spec = importlib.util.spec_from_file_location(selected_cassette, cassette_path)
                cassette_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(cassette_module)
                
                # カセットモジュールからデータフレームを取得
                if hasattr(cassette_module, 'result_df'):
                    df = cassette_module.result_df
                    st.success(f"{len(df)}件のデータを取得しました")
                    
                    # データフレームをセッションに保存
                    st.session_state["result_df"] = df
                    #st.session_state["cassette_info"] = cassette_module.cassette_info
                else:
                    st.error("カセットからデータフレームを取得できませんでした")
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.exception(e)

    # 処理結果の表示
    if "result_df" in st.session_state:
        df = st.session_state["result_df"]
        #cassette_info = st.session_state["cassette_info"]
        
        # カセット情報の表示
        #st.subheader(f"カセット: {cassette_info['name']}")
        #with st.expander("カセット詳細"):
        #    st.write(f"kintoneドメイン: {cassette_info['domain']}")
        #    st.write(f"アプリID: {cassette_info['app_id']}")
        #    if cassette_info.get("query"):
        #        st.write(f"クエリ: {cassette_info['query']}")
        
        # 設定モジュールからグリッドオプションを取得
        grid_options = configure_grid(df)
        
        # AgGridを使用してデータテーブル表示
        AgGrid(
            df,
            gridOptions=grid_options,
            theme='streamlit',
            height=600, 
            width='100%',
            enable_enterprise_modules=True,
            allow_unsafe_jscode=True
        )

