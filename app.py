import streamlit as st
import sqlite3

# --- データベースの準備（SQLite） ---
# ここで「todo.db」というファイルを自動で作って、データを保存する設定をしてるよ
conn = sqlite3.connect('todo.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, content TEXT, status INTEGER)')
conn.commit()

# --- アプリの画面（UI） ---
st.title("📝 簡易ToDo管理アプリ")
st.caption("ITエージェントのための「Webアプリ解像度向上」プロジェクト")

# タスク入力エリア
new_task = st.text_input("新しいタスクを入力してね", placeholder="例：エンジニアと面談")
if st.button("追加"):
    if new_task:
        # データベースに書き込む処理（Create）
        c.execute('INSERT INTO tasks (content, status) VALUES (?, ?)', (new_task, 0))
        conn.commit()
        st.rerun()

# --- タスク一覧の表示 ---
st.write("### 現在のタスク一覧")
# データベースから読み取る処理（Read）
c.execute('SELECT * FROM tasks')
tasks = c.fetchall()

for task in tasks:
    cols = st.columns([0.1, 0.7, 0.2])
    # 削除ボタン
    if cols[2].button("完了/削除", key=task[0]):
        # データベースから消す処理（Delete）
        c.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
        conn.commit()
        st.rerun()
    cols[1].text(task[1])

conn.close()