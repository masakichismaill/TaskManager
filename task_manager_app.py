import tkinter as tk


# メインウィンドウ
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
# ボタンエリア（まだ中身なし）
# =========================
button_frame = tk.Frame(right_frame, pady=10)
button_frame.pack(fill="x")

add_button = tk.Button(button_frame, text="追加", width=10)
update_button = tk.Button(button_frame, text="更新", width=10)
delete_button = tk.Button(button_frame, text="削除", width=10)

add_button.pack(side="left", padx=5)
update_button.pack(side="left", padx=5)
delete_button.pack(side="left", padx=5)

# メインループ
root.mainloop()
