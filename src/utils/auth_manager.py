import streamlit as st

class AuthManager:
    def __init__(self, users):
        self.users = users

    def validate_login(self, username: str, password: str) -> bool:
        """ログイン認証"""
        # self.usersは辞書形式なので、キー（username）で検索
        if username in self.users:
            user = self.users[username]
            if user["password"] == password:
                return True
        return False

    def initialize_session_state(self):
        """セッション状態を初期化"""
        if "loggedin" not in st.session_state:
            st.session_state.loggedin = False
            st.session_state.username = None

    def login(self, username: str, password: str) -> bool:
        """ログイン処理"""
        if self.validate_login(username, password):
            st.session_state.loggedin = True
            st.session_state.username = username
            return True
        return False

    def logout(self):
        """ログアウト処理"""
        st.session_state.loggedin = False
        st.session_state.username = None

    @property
    def is_logged_in(self) -> bool:
        """ログイン状態確認"""
        return st.session_state.get('loggedin', False)

    @property
    def current_user(self):
        """現在のユーザー名取得"""
        return st.session_state.get('username', None)
