import tkinter as tk
import json
import os


# タスクを保存する箱。各タスクは{"title":...,"due":...,"memo":...}という辞書でもつ。
# 呼び出す時にtasks["title"]など意味のある名前で呼べる。
tasks = []

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
    }

    # 内部のリストに追加
    tasks.append(task)

    # Listbox にタイトルを表示.tk.ENDは今あるアイテムの最後に入れる。
    task_listbox.insert(tk.END, title)

    # 入力欄をクリア（好みで変えてOK）
    title_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    memo_text.delete("1.0", tk.END)
    save_tasks_to_file()


def on_select(event):
    """タスク一覧で選ばれたものを、右側の入力欄に表示する"""
    if not tasks:
        return
    # curselection:現在の選択。今選択されている行の番号たち
    selection = task_listbox.curselection()
    if not selection:
        return
    # Listboxで上から何番目を選んだか->同じ番号のtasks[index]を取り出す
    index = selection[0]  # 何番目か（0,1,2,...）
    task = tasks[index]  # 対応するタスク辞書を取り出す

    # いったん全部クリア
    title_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    memo_text.delete("1.0", tk.END)

    # 選択中タスクの内容をセット
    # task_listbox.insert(位置,追加するリスト)指定した位置に、新しい行を差し込む
    title_entry.insert(0, task["title"])
    due_entry.insert(0, task["due"])
    memo_text.insert("1.0", task["memo"])


# 保存関数
def save_tasks_to_file():
    with open("tasks.json", "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)


# 読み込み関数
def load_tasks_from_file():
    if not os.path.exists("tasks.json"):
        return
    global tasks
    with open("tasks.json", "r", encoding="utf-8") as f:
        tasks = json.load(f)

    # 画面(Listbox)にも反映
    task_listbox.delete(0, tk.END)
    for task in tasks:
        task_listbox.insert(tk.END, task["title"])


# 更新用関数
def update_task():
    """選択中のタスクを、右側の入力内容で上書きする"""
    selection = task_listbox.curselection()
    if not selection:
        print("更新するタスクを選んでください。")
        return

    index = selection[0]

    title = title_entry.get().strip()
    due = due_entry.get().strip()
    memo = memo_text.get("1.0", tk.END).strip()

    if not title:
        print("タイトルを入力してください。")
        return

    # 内部データを上書き
    tasks[index] = {
        "title": title,
        "due": due,
        "memo": memo,
    }

    # Listbox の表示も更新
    task_listbox.delete(index)
    task_listbox.insert(index, title)
    task_listbox.selection_set(index)  # 選択状態を保つ

    # ファイルに保存
    save_tasks_to_file()


def delete_task():
    """選択中のタスクを削除する"""
    selection = task_listbox.curselection()
    if not selection:
        print("削除するタスクを選んでください。")
        return

    index = selection[0]

    # Listbox から削除
    task_listbox.delete(index)

    # 内部データからも削除
    tasks.pop(index)

    # ファイルに保存
    save_tasks_to_file()

    # 右側の入力欄をクリア
    title_entry.delete(0, tk.END)
    due_entry.delete(0, tk.END)
    memo_text.delete("1.0", tk.END)


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

task_listbox = tk.Listbox(left_frame, width=30, height=20)
task_listbox.bind("<<ListboxSelect>>", on_select)
task_listbox.pack(side="left", fill="y")

scrollbar = tk.Scrollbar(left_frame, orient="vertical")
scrollbar.pack(side="right", fill="y")

# Listbox と スクロールバーを連動
task_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.config(command=task_listbox.yview)

# =========================
# 右側：タスク編集エリア
# =========================
right_frame = tk.Frame(root, padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True)

# タイトル
title_label = tk.Label(right_frame, text="タイトル", font=("メイリオ", 11, "bold"))
title_label.pack(anchor="w")

title_entry = tk.Entry(right_frame)
title_entry.pack(fill="x")

# 期日（締切）
due_label = tk.Label(right_frame, text="期日（任意）", font=("メイリオ", 10))
due_label.pack(anchor="w", pady=(10, 0))

due_entry = tk.Entry(right_frame)
due_entry.pack(fill="x")

# メモ
memo_label = tk.Label(right_frame, text="メモ", font=("メイリオ", 10))
memo_label.pack(anchor="w", pady=(10, 0))

memo_text = tk.Text(right_frame, wrap="word")
memo_text.pack(fill="both", expand=True)

# =========================
# ボタンエリア
# =========================
button_frame = tk.Frame(right_frame, pady=10)
button_frame.pack(fill="x")

add_button = tk.Button(button_frame, text="追加", width=10)
update_button = tk.Button(button_frame, text="更新", width=10)
delete_button = tk.Button(button_frame, text="削除", width=10)

add_button.pack(side="left", padx=5)
update_button.pack(side="left", padx=5)
delete_button.pack(side="left", padx=5)

add_button.config(command=add_task)
update_button.config(command=update_task)
delete_button.config(command=delete_task)

load_tasks_from_file()
# メインループ
root.mainloop()
