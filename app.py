import streamlit as st
import sqlite3
from datetime import date

# --- データベースの準備 ---
conn = sqlite3.connect('todo.db', check_same_thread=False)
c = conn.cursor()

# テーブル作成（status: 0=未完了, 1=完了）
c.execute('''CREATE TABLE IF NOT EXISTS tasks 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, 
              content TEXT, 
              status INTEGER, 
              due_date TEXT,
              priority TEXT)''')
conn.commit()

# --- アプリの画面設定 ---
st.set_page_config(page_title="ToDo管理アプリ", page_icon="✅")
st.title("✅ 完了管理機能付きToDo")

# --- 1. タスク登録エリア ---
with st.expander("➕ 新しいタスクを追加", expanded=False):
    new_task = st.text_input("タスク名")
    col1, col2 = st.columns(2)
    with col1:
        selected_date = st.date_input("期限", date.today())
    with col2:
        priority = st.selectbox("優先度", ["高", "中", "低"], index=1)

    if st.button("登録する", use_container_width=True):
        if new_task:
            # 初期状態は status=0 (未完了) で保存
            c.execute('INSERT INTO tasks (content, status, due_date, priority) VALUES (?, ?, ?, ?)', 
                      (new_task, 0, str(selected_date), priority))
            conn.commit()
            st.rerun()

# --- 2. データの取得と分類 ---
# 優先度順に全件取得
c.execute("SELECT * FROM tasks ORDER BY CASE priority WHEN '高' THEN 1 WHEN '中' THEN 2 WHEN '低' THEN 3 END")
all_tasks = c.fetchall()

# 未完了と完了済みでリストを分ける（プログラム側で仕分け）
todo_tasks = [t for t in all_tasks if t[2] == 0]
done_tasks = [t for t in all_tasks if t[2] == 1]

# --- 3. メイン表示エリア ---
st.subheader("📝 実行中のタスク")
if not todo_tasks:
    st.info("現在、実行中のタスクはありません。")

for task in todo_tasks:
    with st.container(border=True):
        cols = st.columns([0.6, 0.2, 0.2])
        p_icon = "🔥" if task[4] == "高" else "📄"
        cols[0].markdown(f"{p_icon} **{task[1]}** (期限: {task[3]})")
        cols[1].caption(f"優先度: {task[4]}")
        
        # ★修正ポイント：DELETEではなくUPDATEでstatusを1にする
        if cols[2].button("完了 ✅", key=f"done_{task[0]}"):
            c.execute('UPDATE tasks SET status = 1 WHERE id = ?', (task[0],))
            conn.commit()
            st.rerun()

# --- 4. 完了済みエリア ---
st.divider()
with st.expander(f"📁 完了済みのタスク ({len(done_tasks)}件)"):
    for task in done_tasks:
        cols = st.columns([0.7, 0.3])
        # 打ち消し線を入れる演出
        cols[0].markdown(f"~~{task[1]}~~")
        
        # 完全に消したい時のための削除ボタン
        if cols[1].button("完全に削除 🗑️", key=f"del_{task[0]}"):
            c.execute('DELETE FROM tasks WHERE id = ?', (task[0],))
            conn.commit()
            st.rerun()

conn.close()