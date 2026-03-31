import streamlit as st
import sqlite3
from datetime import date

# --- データベースの準備 ---
conn = sqlite3.connect('todo.db', check_same_thread=False)
c = conn.cursor()

# ★修正ポイント1：テーブルに「due_date（期限）」の列を追加するように変更
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              content TEXT, 
              status INTEGER, 
              due_date TEXT)''') # due_dateを追加！
conn.commit()

# --- アプリの画面 ---
st.title("📅 期限付きToDoアプリ")

# 入力エリア
new_task = st.text_input("タスク名を入力", placeholder="例：契約書の送付")

# ★修正ポイント2：日付を選択するカレンダーを追加
selected_date = st.date_input("期限を選んでね", date.today())

if st.button("追加"):
    if new_task:
        # ★修正ポイント3：SQL命令に「due_date」を追加（INSERT）
        c.execute('INSERT INTO tasks (content, status, due_date) VALUES (?, ?, ?)', 
                  (new_task, 0, str(selected_date)))
        conn.commit()
        st.rerun()

# --- 一覧表示 ---
st.write("### タスク一覧")
c.execute('SELECT * FROM tasks')
tasks = c.fetchall()

for task in tasks:
    cols = st.columns([0.1, 0.5, 0.2, 0.2])
    # task[1]が内容、task[3]が期限だよ
    cols[1].text(task[1])
    cols[2].caption(f"期限: {task[3]}") # 期限を表示
    
    if cols[3].button("完了", key=task[0]):
        c.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
        conn.commit()
        st.rerun()

conn.close()