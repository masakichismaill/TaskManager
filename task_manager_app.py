import tkinter as tk
import json
import os
from datetime import datetime

from tkcalendar import DateEntry

# タスクを保存する箱。各タスクは{"title":...,"due":...,"memo":...,"done":...}という辞書で持つ
tasks = []
# 　カテゴリ候補
CATEGORIES = ["(未選択)", "仕事", "勉強", "生活", "その他"]
# フィルタ種別
FILTER_ALL = "all"  # すべて
FILTER_ACTIVE = "active"  # 未完了のみ
FILTER_DONE = "done"  # 完了のみ

# 現在のフィルタモード
current_filter = FILTER_ALL

# ソート種別
SORT_NONE = "none"
SORT_DUE_ASC = "due_asc"  # 期日が近い順

current_sort = SORT_NONE

# 「Listboxの何行目か」→「tasksの何番目か」を対応させるためのリスト
display_indices = []


def get_display_title(task: dict) -> str:
    """
    Listbox に表示する１行分の文字列を作る。
    例：
      [ ] [仕事] レポートを書く
      [✔] [勉強] Pythonの復習
    """
    done = task.get("done", False)
    mark = "[✔] " if done else "[ ] "

    category = task.get("category", CATEGORIES[0])  # なければ"(未選択)"

    # カテゴリが未選択ならタイトルだけ、選ばれていたら [カテゴリ] をつける
    if category == CATEGORIES[0]:
        return mark + task["title"]
    else:
        return f"{mark}[{category}] {task['title']}"


def get_due_datetime(task):
    """task['due'] を datetime に変換する。失敗したら最大値を返す。"""
    due_str = task.get("due", "").strip()
    if not due_str:
        return datetime.max  # 期日なし → 一番後ろに
    try:
        # 形式：YYYY-MM-DD を想定
        return datetime.strptime(due_str, "%Y-%m-%d")
    except ValueError:
        # 変な書式なら、とりあえず後ろに回す
        return datetime.max


def get_task_color(task):
    """
    このタスクを Listbox に表示するときの文字色を決める。
    戻り値は "red" などの色名（文字列）。
    """
    done = task.get("done", False)

    # 1. 完了タスクは一律グレー
    if done:
        return "gray"

    # 2. 未完了タスクの場合は、期日を見て判断
    due_dt = get_due_datetime(task)
    if due_dt == datetime.max:
        # 期日なし、または変な書式 → 通常の黒
        return "black"

    today = datetime.today().date()
    due_date = due_dt.date()

    # 3. 今日より前 → 期限切れ（赤）
    if due_date < today:
        return "dim gray"

    # 4. 今日ちょうど → 今日中の締切（オレンジ）
    if due_date == today:
        return "red"

    # 5. 未来の日付 → まだ余裕（青）
    return "blue"


def refresh_task_list():
    """current_filter と current_sort に応じて Listbox を描き直す"""
    global display_indices

    task_listbox.delete(0, tk.END)
    display_indices = []

    # まずフィルタに合うタスクの index リストを作る
    filtered_indices = []
    for i, task in enumerate(tasks):
        done = task.get("done", False)
        selected_cat = category_filter_var.get()
        task_cat = task.get("category", CATEGORIES[0])
        # フィルタ処理
        if current_filter == FILTER_ACTIVE and done:
            continue
        if current_filter == FILTER_DONE and not done:
            continue
        if selected_cat != "全てのカテゴリ" and task_cat != selected_cat:
            continue
        filtered_indices.append(i)

    # ソートモードに応じて並び替え（今は「期日が近い順」のみ）
    if current_sort == SORT_DUE_ASC:
        filtered_indices.sort(key=lambda idx: get_due_datetime(tasks[idx]))

    # 並び替え結果をもとに Listbox と display_indices を作る
    for row, idx in enumerate(filtered_indices):
        task = tasks[idx]
        display_text = get_display_title(task)
        task_listbox.insert(tk.END, display_text)

        # ここで色も決めて反映
        color = get_task_color(task)
        task_listbox.itemconfig(row, fg=color)

        display_indices.append(idx)


def set_filter(mode):
    """フィルタモードを変えて一覧を描き直す"""
    global current_filter
    current_filter = mode
    refresh_task_list()


def set_sort(mode):
    """ソートモードを変えて一覧を描き直す"""
    global current_sort
    current_sort = mode
    refresh_task_list()


# =========================
# 関数エリア
# =========================
def add_task():
    """右側の入力内容からタスクを追加し、一覧に表示する"""
    title = title_entry.get().strip()
    due = due_entry.get().strip()
    memo = memo_text.get("1.0", tk.END).strip()

    if not title:
        print("タイトルを入力してください。")
        return

    # 1つのタスクを辞書で表現
    task = {
        "title": title,
        "due": due,
        "memo": memo,
        "done": False,  # 新規は未完了
        "category": category_var.get(),
    }

    tasks.append(task)

    # 入力欄をクリア
    title_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    memo_text.delete("1.0", tk.END)

    save_tasks_to_file()
    update_status_label()
    refresh_task_list()


def on_select(event):
    """タスク一覧で選ばれたものを、右側の入力欄に表示する"""
    if not tasks:
        return

    selection = task_listbox.curselection()
    if not selection:
        return

    list_index = selection[0]  # Listbox 上での何行目か
    if list_index >= len(display_indices):
        return

    real_index = display_indices[list_index]  # 実際の tasks 内の位置
    task = tasks[real_index]

    # いったん全部クリア
    title_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    memo_text.delete("1.0", tk.END)

    # 選択中タスクの内容をセット
    title_entry.insert(0, task["title"])
    due_entry.insert(0, task["due"])
    memo_text.insert("1.0", task["memo"])
    category_var.set(task.get("category", CATEGORIES[0]))


def save_tasks_to_file():
    """tasks 全体を JSON に保存"""
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


def update_status_label():
    """タスク件数と完了数をラベルに表示する"""
    total = len(tasks)
    done_count = sum(1 for t in tasks if t.get("done", False))
    status_label.config(text=f"タスク：{total}件（完了 {done_count}件）")


def load_tasks_from_file():
    """起動時に JSON からタスク一覧を読み込む"""
    if not os.path.exists("tasks.json"):
        return

    global tasks
    with open("tasks.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)

    # 古いデータに done が無い場合は False で補う
    for task in tasks:
        if "done" not in task:
            task["done"] = False
        if "category" not in task:
            task["category"] = CATEGORIES[0]
    update_status_label()
    refresh_task_list()


def update_task():
    """選択中のタスクを、右側の入力内容で上書きする"""
    selection = task_listbox.curselection()
    if not selection:
        print("更新するタスクを選んでください。")
        return

    list_index = selection[0]
    if list_index >= len(display_indices):
        return
    real_index = display_indices[list_index]

    title = title_entry.get().strip()
    due = due_entry.get().strip()
    memo = memo_text.get("1.0", tk.END).strip()

    if not title:
        print("タイトルを入力してください。")
        return

    # もともとの done を保持したまま、他の項目だけ更新
    old_done = tasks[real_index].get("done", False)
    tasks[real_index] = {
        "title": title,
        "due": due,
        "memo": memo,
        "done": old_done,
        "category": category_var.get(),
    }

    save_tasks_to_file()
    refresh_task_list()


def delete_task():
    """選択中のタスクを削除する"""
    selection = task_listbox.curselection()
    if not selection:
        print("削除するタスクを選んでください。")
        return

    list_index = selection[0]
    if list_index >= len(display_indices):
        return
    real_index = display_indices[list_index]

    tasks.pop(real_index)

    save_tasks_to_file()
    update_status_label()
    refresh_task_list()

    title_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    memo_text.delete("1.0", tk.END)


def toggle_done():
    """選択中タスクの完了/未完了を切り替える"""
    selection = task_listbox.curselection()
    if not selection:
        print("完了状態を切り替えるタスクを選んでください。")
        return

    list_index = selection[0]
    if list_index >= len(display_indices):
        return
    real_index = display_indices[list_index]

    task = tasks[real_index]
    task["done"] = not task.get("done", False)

    save_tasks_to_file()
    update_status_label()
    refresh_task_list()


def search_tasks():
    query = search_entry.get().strip()
    if not query:  # 空なら全件表示
        refresh_task_list()
        return
    task_listbox.delete(0, tk.END)
    display_indices.clear()

    for i, task in enumerate(tasks):
        title = task["title"]
        memo = task["memo"]
        # ---検索条件---
        if (query in title) or (query in memo):
            list_index = task_listbox.size()
            task_listbox.insert(tk.END, get_display_title(task))
            task_listbox.itemconfig(list_index, fg=get_task_color(task))
            display_indices.append(i)


def clear_search():
    search_entry.delete(0, tk.END)
    refresh_task_list()


# =========================
# メインウィンドウ
# =========================

root = tk.Tk()
root.title("タスク管理アプリ")
root.geometry("900x600")  # 幅 x 高さ

# =========================
# 左側：タスク一覧エリア
# =========================
left_frame = tk.Frame(root, padx=10, pady=10)
left_frame.pack(side="left", fill="y")

list_label = tk.Label(left_frame, text="タスク一覧", font=("メイリオ", 11, "bold"))
list_label.pack(anchor="w")

# フィルタボタンのエリア
filter_frame = tk.Frame(left_frame)
filter_frame.pack(fill="x", pady=(0, 5))

all_button = tk.Button(
    filter_frame, text="すべて", width=6, command=lambda: set_filter(FILTER_ALL)
)
active_button = tk.Button(
    filter_frame, text="未完了", width=6, command=lambda: set_filter(FILTER_ACTIVE)
)
done_button = tk.Button(
    filter_frame, text="完了", width=6, command=lambda: set_filter(FILTER_DONE)
)

all_button.pack(side="left", padx=2)
active_button.pack(side="left", padx=2)
done_button.pack(side="left", padx=2)

category_filter_var = tk.StringVar()
category_filter_var.set("全てのカテゴリ")

category_filter_menu = tk.OptionMenu(
    left_frame,
    category_filter_var,
    "全てのカテゴリ",
    *CATEGORIES[1:],
    command=lambda _: refresh_task_list(),
)
category_filter_menu.pack(anchor="w", pady=(5, 8))
# =========================
# 　検索エリア
# =========================
search_frame = tk.Frame(left_frame)
search_frame.pack(fill="x", pady=(0, 5))

search_entry = tk.Entry(search_frame, width=18)
search_entry.pack(side="left", padx=(0, 5))

search_button = tk.Button(search_frame, text="検索", width=6)
search_button.pack(side="left", padx=(0, 2))

clear_button = tk.Button(search_frame, text="クリア", width=6)
clear_button.pack(side="left")

# ソートボタン
sort_button = tk.Button(
    left_frame,
    text="期日が近い順",
    width=18,
    command=lambda: set_sort(SORT_DUE_ASC),
)
sort_clear_button = tk.Button(
    left_frame,
    text="並び替え解除",
    width=18,
    command=lambda: set_sort(SORT_NONE),
)
sort_button.pack(anchor="w", pady=(0, 2))
sort_clear_button.pack(anchor="w", pady=(0, 8))

task_listbox = tk.Listbox(left_frame, width=30, height=20)
task_listbox.bind("<<ListboxSelect>>", on_select)
task_listbox.pack(side="left", fill="y")

scrollbar = tk.Scrollbar(left_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

task_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=task_listbox.yview)


# =========================
# 右側：タスク編集エリア
# =========================
right_frame = tk.Frame(root, padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)
# カテゴリ選択のための変数
category_var = tk.StringVar()
category_var.set(CATEGORIES[0])
title_label = tk.Label(right_frame, text="タイトル", font=("メイリオ", 11, "bold"))
title_label.pack(anchor="w")

title_entry = tk.Entry(right_frame)
title_entry.pack(fill="x")

category_label = tk.Label(right_frame, text="カテゴリー", font=("メイリオ", 10))
category_label.pack(anchor="w", pady=(10, 0))

category_menu = tk.OptionMenu(right_frame, category_var, *CATEGORIES)
category_menu.pack(anchor="w")

due_label = tk.Label(right_frame, text="期日（任意）", font=("メイリオ", 10))
due_label.pack(anchor="w", pady=(10, 0))

due_entry = DateEntry(
    right_frame,
    width=20,
    date_pattern="yyyy-mm-dd",  # 例: 2025-11-21 という形式で返してくれる
    firstweekday="sunday",  # （お好みで）週の始まり
    showweeknumbers=False,  # （お好みで）週番号を非表示
)
due_entry.pack(fill="x")
today_str = datetime.today().strftime("%Y-%m-%d")
due_entry.insert(0, today_str)
memo_label = tk.Label(right_frame, text="メモ", font=("メイリオ", 10))
memo_label.pack(anchor="w", pady=(10, 0))

memo_text = tk.Text(right_frame, wrap="word")
memo_text.pack(fill="both", expand=True)

button_frame = tk.Frame(right_frame, pady=10)
button_frame.pack(fill="x")

status_label = tk.Label(right_frame, text="タスク：0件（完了 0件）")
status_label.pack(anchor="w", pady=(0, 5))

add_button = tk.Button(button_frame, text="追加", width=10)
update_button = tk.Button(button_frame, text="更新", width=10)
delete_button = tk.Button(button_frame, text="削除", width=10)
toggle_button = tk.Button(button_frame, text="完了切替", width=10)

add_button.pack(side="left", padx=5)
update_button.pack(side="left", padx=5)
delete_button.pack(side="left", padx=5)
toggle_button.pack(side="left", padx=5)

add_button.config(command=add_task)
update_button.config(command=update_task)
delete_button.config(command=delete_task)
toggle_button.config(command=toggle_done)
search_button.config(command=search_tasks)
search_entry.bind("<Return>", lambda event: search_tasks())
clear_button.config(command=clear_search)

# 起動時にロード
load_tasks_from_file()

root.mainloop()
