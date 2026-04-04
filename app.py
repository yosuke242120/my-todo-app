import streamlit as st
import sqlite3
from datetime import date

# --- データベースの準備 ---
conn = sqlite3.connect('todo.db', check_same_thread=False)
c = conn.cursor()

# ★修正ポイント1：created_at（作成日）の列を追加
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              content TEXT, 
              status INTEGER, 
              due_date TEXT,
              priority TEXT,
              created_at TEXT)''') # 作成日を追加！
conn.commit()

# --- ページ設定 ---
st.set_page_config(page_title="Task Master Pro", page_icon="⚡", layout="wide")

# --- サイドバー：タスク登録 ---
st.sidebar.title("🛠️ 操作パネル")
with st.sidebar.expander("➕ 新規タスク登録", expanded=True):
    new_task = st.sidebar.text_input("タスク名")
    selected_date = st.sidebar.date_input("期限", date.today())
    priority = st.sidebar.selectbox("優先度", ["高", "中", "低"], index=1)
    
    if st.sidebar.button("タスクを保存", use_container_width=True):
        if new_task:
            # ★修正ポイント2：登録した瞬間の日付（date.today()）を一緒に保存
            c.execute('''INSERT INTO tasks (content, status, due_date, priority, created_at) 
                         VALUES (?, ?, ?, ?, ?)''', 
                      (new_task, 0, str(selected_date), priority, str(date.today())))
            conn.commit()
            st.rerun()

# --- メイン画面 ---
st.title("⚡ Task Master Pro")

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
            
            # ★修正ポイント3：作成日を表示に追加（task[5]が作成日）
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
            st.caption(f"📅 完了済み (登録日: {task[5]})") # ここにも登録日
            if st.button("削除 🗑️", key=f"del_{task[0]}"):
                c.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
                conn.commit()
                st.rerun()

conn.close()