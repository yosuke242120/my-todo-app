import streamlit as st
import sqlite3
from datetime import date, datetime

# --- 1. パスワード認証機能 ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("password", "yousuke123"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("鍵がかかっています。パスワードを入力してください", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("鍵がかかっています。パスワードを入力してください", type="password", on_change=password_entered, key="password")
        st.error("😕 パスワードが違います")
        return False
    else:
        return True

if not check_password():
    st.stop()

# --- 2. データベース準備（カテゴリー列を追加） ---
conn = sqlite3.connect('todo.db', check_same_thread=False)
c = conn.cursor()
# 今回、category列を新しく追加した設計図にするよ
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              content TEXT, 
              status INTEGER, 
              due_date TEXT,
              priority TEXT,
              created_at TEXT,
              category TEXT)''')
conn.commit()

# --- 3. 画面レイアウト ---
st.set_page_config(page_title="My Task Master Pro", page_icon="🎯", layout="wide")

# サイドバー：入力
st.sidebar.title("🛠️ 操作パネル")
with st.sidebar.expander("➕ 新規タスク登録", expanded=True):
    new_task = st.sidebar.text_input("タスク名")
    selected_date = st.sidebar.date_input("期限", date.today())
    category = st.sidebar.selectbox("カテゴリー", ["仕事", "学習関連", "プライベート"])
    priority = st.sidebar.selectbox("優先度", ["高", "中", "低"], index=1)
    
    if st.sidebar.button("タスクを保存", use_container_width=True):
        if new_task:
            c.execute('''INSERT INTO tasks (content, status, due_date, priority, created_at, category) 
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                      (new_task, 0, str(selected_date), priority, str(date.today()), category))
            conn.commit()
            st.rerun()

# --- 4. メイン画面 ---
st.title("🎯 My Private Task Master")

# データ取得
c.execute("SELECT * FROM tasks ORDER BY due_date ASC")
all_tasks = c.fetchall()
todo_tasks = [t for t in all_tasks if t[2] == 0]
done_tasks = [t for t in all_tasks if t[2] == 1]

# 進捗
if all_tasks:
    progress = len(done_tasks) / len(all_tasks)
    st.write(f"### 📊 進捗率: {int(progress * 100)}%")
    st.progress(progress)
    st.divider()

# --- 5. タスク表示 ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📝 実行中")
    # カテゴリー別にフィルタリングして表示する機能
    filter_cat = st.multiselect("カテゴリーで絞り込み", ["仕事", "学習関連", "プライベート"], default=["仕事", "学習関連", "プライベート"])
    
    for task in todo_tasks:
        if task[6] in filter_cat:
            # 期限切れチェック
            is_overdue = datetime.strptime(task[3], '%Y-%m-%d').date() < date.today()
            border_color = "red" if is_overdue else "gray"
            
            # 枠付きコンテナで表示
            with st.container(border=True):
                # 期限切れなら警告アイコンを出す
                title_prefix = "⚠️ [期限切れ] " if is_overdue else ""
                st.markdown(f"### {title_prefix}{task[1]}")
                
                # ラベルと日付の表示
                st.caption(f"📂 {task[6]} | 📅 期限: {task[3]} | 🆕 登録: {task[5]}")
                
                # 優先度の色付け
                p_color = "red" if task[4] == "高" else "orange" if task[4] == "中" else "blue"
                st.markdown(f"優先度: :{p_color}[{task[4]}]")
                
                if st.button("完了 ✅", key=f"done_{task[0]}", use_container_width=True):
                    c.execute('UPDATE tasks SET status = 1 WHERE id = ?', (task[0],))
                    conn.commit()
                    st.rerun()

with col_right:
    st.subheader("📁 完了済み")
    for task in done_tasks:
        with st.container(border=True):
            st.markdown(f"~~{task[1]}~~")
            st.caption(f"📂 {task[6]} | 📅 完了済み")
            if st.button("削除 🗑️", key=f"del_{task[0]}"):
                c.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
                conn.commit()
                st.rerun()

conn.close()