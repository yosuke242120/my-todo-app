import streamlit as st
import sqlite3
from datetime import date

# --- 1. パスワード認証機能 ---
def check_password():
    """パスワードが正しいかチェックし、結果を返す"""
    def password_entered():
        # Streamlit Cloudの「Secrets」設定、またはローカルのパスワードと比較
        # ※後ほど設定する「yousuke123」というパスワードを想定
        if st.session_state["password"] == st.secrets.get("password", "yousuke123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セキュリティのため入力値を消す
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初回表示：パスワード入力フォーム
        st.text_input("鍵がかかっています。パスワードを入力してください", 
                      type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # 間違った場合
        st.text_input("鍵がかかっています。パスワードを入力してください", 
                      type="password", on_change=password_entered, key="password")
        st.error("😕 パスワードが違います")
        return False
    else:
        # 正解！
        return True

# 認証が通らない場合は、ここでプログラムを止める
if not check_password():
    st.stop()

# --- 2. ここからToDoアプリ本体（認証成功時のみ実行される） ---

# --- データベースの準備 ---
conn = sqlite3.connect('todo.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              content TEXT, 
              status INTEGER, 
              due_date TEXT,
              priority TEXT,
              created_at TEXT)''')
conn.commit()

# --- ページ設定 ---
st.set_page_config(page_title="My Private Task Master", page_icon="🔐", layout="wide")

# --- サイドバー：タスク登録 ---
st.sidebar.title("🛠️ 操作パネル")
with st.sidebar.expander("➕ 新規タスク登録", expanded=True):
    new_task = st.sidebar.text_input("タスク名")
    selected_date = st.sidebar.date_input("期限", date.today())
    priority = st.sidebar.selectbox("優先度", ["高", "中", "低"], index=1)
    
    if st.sidebar.button("タスクを保存", use_container_width=True):
        if new_task:
            c.execute('''INSERT INTO tasks (content, status, due_date, priority, created_at) 
                         VALUES (?, ?, ?, ?, ?)''', 
                      (new_task, 0, str(selected_date), priority, str(date.today())))
            conn.commit()
            st.rerun()

# --- メイン画面 ---
st.title("🔐 My Private Task Master")

# データの取得
c.execute("SELECT * FROM tasks ORDER BY CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 WHEN '低' THEN 3 END")
all_tasks = c.fetchall()
todo_tasks = [t for t in all_tasks if t[2] == 0]
done_tasks = [t for t in all_tasks if t[2] == 1]

# 進捗管理
if all_tasks:
    progress = len(done_tasks) / len(all_tasks)
    st.write(f"### 📊 現在の達成率: {int(progress * 100)}%")
    st.progress(progress)
    st.divider()

# --- タスク表示 ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 実行中")
    for task in todo_tasks:
        with st.container(border=True):
            color = "red" if task[4] == "高" else "orange" if task[4] == "中" else "blue"
            st.markdown(f"### {task[1]}")
            st.caption(f"📅 期限: {task[3]} / 🆕 登録日: {task[5]}")
            st.markdown(f"**優先度:** :{color}[{task[4]}]")
            
            if st.button("完了 ✅", key=f"done_{task[0]}", use_container_width=True):
                c.execute('UPDATE tasks SET status = 1 WHERE id = ?', (task[0],))
                conn.commit()
                st.rerun()

with col_right:
    st.subheader("📁 完了済み")
    for task in done_tasks:
        with st.container(border=True):
            st.markdown(f"~~{task[1]}~~")
            st.caption(f"📅 完了済み (登録日: {task[5]})")
            if st.button("削除 🗑️", key=f"del_{task[0]}"):
                c.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
                conn.commit()
                st.rerun()

conn.close()