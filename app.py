import streamlit as st
import sqlite3
from datetime import date, datetime

# ============================================================
# 1. ページ設定（一番最初に呼ぶ）
# ============================================================
st.set_page_config(page_title="Task Master Pro", page_icon="🎯", layout="wide")

# ============================================================
# 2. パスワード認証（Secretsを使用）
# ============================================================
def check_password():
    """パスワードが正しいかチェック。コード内に直接パスワードは書かない"""
    def password_entered():
        # Streamlit Cloudの「Secrets」設定、またはローカルの secrets.toml から取得
        correct_password = st.secrets.get("password")
        
        if not correct_password:
            st.error("設定エラー: Secretsに 'password' が設定されていません。")
            return

        if st.session_state["password"] == correct_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("🔒 パスワードを入力してください", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("🔒 パスワードを入力してください", type="password", on_change=password_entered, key="password")
        st.error("😕 パスワードが違います")
        return False
    return True

if not check_password():
    st.stop()

# ============================================================
# 3. カスタム CSS（デザイン）
# ============================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #0e0f14; color: #e8e6e0; }
[data-testid="stSidebar"] { background: #16171f !important; border-right: 1px solid #2a2b35; }

h1 {
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important;
    letter-spacing: -1px !important;
    background: linear-gradient(135deg, #f0c274 0%, #e8875a 50%, #d15f8a 100%);
    -webkit-background-clip: text !important;
    -webkit-text-fill-color: transparent !important;
}

.task-card {
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 12px;
    border: 1px solid rgba(255,255,255,0.08);
    backdrop-filter: blur(8px);
    transition: transform 0.15s ease;
    position: relative;
    overflow: hidden;
}
.task-card:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.4); }

.card-work { background: rgba(209, 95, 138, 0.10); }
.card-work::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #d15f8a; }
.card-study { background: rgba(82, 196, 168, 0.10); }
.card-study::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #52c4a8; }
.card-private { background: rgba(100, 149, 237, 0.10); }
.card-private::before { content: ''; position: absolute; left: 0; top: 0; bottom: 0; width: 4px; background: #6495ed; }

.task-title { font-family: 'Syne', sans-serif; font-weight: 600; font-size: 1.05rem; margin-bottom: 6px; }
.task-title.overdue { color: #ff7b7b; }
.task-title.done-text { text-decoration: line-through; color: #666; }

.badge { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 0.72rem; font-weight: 500; }
.badge-high { background: rgba(255,80,80,0.18); color: #ff8080; }
.badge-mid { background: rgba(255,180,50,0.18); color: #ffc850; }
.badge-low { background: rgba(100,200,150,0.18); color: #64c896; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# 4. データベース
# ============================================================
@st.cache_resource
def get_connection():
    conn = sqlite3.connect('todo.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS tasks
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  content TEXT,
                  status INTEGER DEFAULT 0,
                  due_date TEXT,
                  priority TEXT,
                  created_at TEXT,
                  category TEXT,
                  completed_at TEXT)''')
    conn.commit()
    return conn

conn = get_connection()
c = conn.cursor()

# ============================================================
# 5. ヘルパー関数・定数
# ============================================================
PRIORITY_ORDER = {"高": 0, "中": 1, "低": 2}
CAT_CLASS = {"仕事": "card-work", "学習関連": "card-study", "プライベート": "card-private"}
CAT_BADGE = {"仕事": "badge-work", "学習関連": "badge-study", "プライベート": "badge-private"}
CAT_ICON  = {"仕事": "💼", "学習関連": "📚", "プライベート": "🏠"}
PRI_BADGE = {"高": "badge-high", "中": "badge-mid", "低": "badge-low"}

def render_task_card(task, done=False):
    tid, content, status, due_date, priority, created_at, category, completed_at = task
    card_class = "card-done" if done else CAT_CLASS.get(category, "")
    title_class = "done-text" if done else ""

    try:
        due_dt = datetime.strptime(due_date, '%Y-%m-%d').date()
        is_overdue = (not done) and (due_dt < date.today())
        if is_overdue: title_class += " overdue"
    except:
        is_overdue = False

    st.markdown(f"""
    <div class="task-card {card_class}">
        <div class="task-title {title_class}">{'✅ ' if done else ''}{content}{' ⚠️ 期限切れ' if is_overdue else ''}</div>
        <div class="task-meta" style="font-size: 0.78rem; color: #888; display: flex; gap: 12px;">
            <span class="badge {CAT_BADGE.get(category)}">{CAT_ICON.get(category)} {category}</span>
            <span class="badge {PRI_BADGE.get(priority)}">{priority}</span>
            <span>📅 {due_date}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    return tid

# ============================================================
# 6. サイドバー
# ============================================================
st.sidebar.markdown("## 🛠️ 操作パネル")
with st.sidebar.expander("➕ 新規タスク登録", expanded=True):
    new_task = st.text_input("タスク名")
    selected_date = st.date_input("期限", date.today())
    category = st.selectbox("カテゴリー", ["仕事", "学習関連", "プライベート"])
    priority = st.selectbox("優先度", ["高", "中", "低"], index=1)
    if st.sidebar.button("💾 保存", use_container_width=True):
        if new_task.strip():
            c.execute("INSERT INTO tasks (content, status, due_date, priority, created_at, category) VALUES (?, 0, ?, ?, ?, ?)",
                      (new_task, str(selected_date), priority, str(date.today()), category))
            conn.commit()
            st.rerun()

st.sidebar.divider()
search_query = st.sidebar.text_input("🔎 検索")
filter_cat = st.sidebar.multiselect("カテゴリー", ["仕事", "学習関連", "プライベート"], default=["仕事", "学習関連", "プライベート"])
sort_by = st.sidebar.selectbox("並び替え", ["期限順", "優先度順"])

# ============================================================
# 7. メイン表示
# ============================================================
st.title("🎯 Task Master Pro")

c.execute("SELECT * FROM tasks")
all_tasks = c.fetchall()
todo_tasks = [t for t in all_tasks if t[2] == 0 and t[6] in filter_cat]
done_tasks = [t for t in all_tasks if t[2] == 1 and t[6] in filter_cat]

# ソート
if sort_by == "期限順": todo_tasks.sort(key=lambda t: t[3])
else: todo_tasks.sort(key=lambda t: PRIORITY_ORDER.get(t[4], 1))

# 進捗表示
if all_tasks:
    prog = len(done_tasks) / len(all_tasks)
    st.progress(prog)
    st.write(f"進捗: {int(prog*100)}%")

col_left, col_right = st.columns([3, 2])

with col_left:
    st.subheader("📝 実行中")
    for task in todo_tasks:
        tid = render_task_card(task)
        bc1, bc2 = st.columns(2)
        if bc1.button("✅ 完了", key=f"d_{tid}"):
            c.execute("UPDATE tasks SET status=1, completed_at=? WHERE id=?", (str(date.today()), tid))
            conn.commit()
            st.rerun()
        if bc2.button("🗑️ 削除", key=f"del_{tid}"):
            c.execute("DELETE FROM tasks WHERE id=?", (tid,))
            conn.commit()
            st.rerun()

with col_right:
    st.subheader("📁 完了済み")
    for task in done_tasks:
        render_task_card(task, done=True)