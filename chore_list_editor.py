import json
import tkinter as tk
from tkinter import ttk, messagebox

JSON_FILE = 'chore_data.json'

# Load chores from JSON file
def load_chores(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data

def save_chores(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def refresh_list():
    category = category_var.get()
    chores_listbox.delete(0, tk.END)
    for idx, chore in enumerate(data['household_chores'][category]):
        chores_listbox.insert(tk.END, f"{idx+1}. {chore['chore']} (Score: {chore['score']}, Time: {chore['time_estimate']} min)")

def add_chore():
    category = category_var.get()
    edit_chore_dialog(None, category)

def delete_chore():
    category = category_var.get()
    selection = chores_listbox.curselection()
    if not selection:
        return
    idx = selection[0]
    del data['household_chores'][category][idx]
    save_chores(JSON_FILE, data)
    refresh_list()

def edit_chore():
    category = category_var.get()
    selection = chores_listbox.curselection()
    if not selection:
        return
    idx = selection[0]
    edit_chore_dialog(idx, category)

def edit_chore_dialog(idx, category):
    if idx is not None:
        chore = data['household_chores'][category][idx]
        name_val = chore['chore']
        score_val = str(chore['score'])
        time_val = str(chore['time_estimate'])
    else:
        name_val = ''
        score_val = ''
        time_val = ''
    dialog = tk.Toplevel(root)
    dialog.title("Edit Chore" if idx is not None else "Add Chore")
    tk.Label(dialog, text="Chore name:").grid(row=0, column=0, sticky=tk.W)
    name_entry = tk.Entry(dialog)
    name_entry.insert(0, name_val)
    name_entry.grid(row=0, column=1)
    tk.Label(dialog, text="Score:").grid(row=1, column=0, sticky=tk.W)
    score_entry = tk.Entry(dialog)
    score_entry.insert(0, score_val)
    score_entry.grid(row=1, column=1)
    tk.Label(dialog, text="Time estimate (min):").grid(row=2, column=0, sticky=tk.W)
    time_entry = tk.Entry(dialog)
    time_entry.insert(0, time_val)
    time_entry.grid(row=2, column=1)
    def save():
        name = name_entry.get().strip()
        try:
            score = int(score_entry.get())
            time_estimate = int(time_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Score and time must be numbers.")
            return
        if not name:
            messagebox.showerror("Error", "Chore name required.")
            return
        if idx is not None:
            data['household_chores'][category][idx] = {
                'chore': name,
                'score': score,
                'time_estimate': time_estimate
            }
        else:
            data['household_chores'][category].append({
                'chore': name,
                'score': score,
                'time_estimate': time_estimate
            })
        save_chores(JSON_FILE, data)
        refresh_list()
        dialog.destroy()
    save_btn = tk.Button(dialog, text="Save", command=save)
    save_btn.grid(row=3, column=0, columnspan=2, pady=5)
    dialog.grab_set()

def on_category_change(event=None):
    refresh_list()

data = load_chores(JSON_FILE)

root = tk.Tk()
root.title("Chore List Editor")

mainframe = ttk.Frame(root, padding="20 20 20 20")
mainframe.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

category_var = tk.StringVar(value=list(data['household_chores'].keys())[0])
category_label = ttk.Label(mainframe, text="Category:")
category_label.grid(row=0, column=0, sticky=tk.W)

category_menu = ttk.Combobox(mainframe, textvariable=category_var, values=list(data['household_chores'].keys()), state="readonly")
category_menu.grid(row=0, column=1, sticky=(tk.W, tk.E))
category_menu.bind('<<ComboboxSelected>>', on_category_change)

chores_listbox = tk.Listbox(mainframe, width=50, height=12)
chores_listbox.grid(row=1, column=0, columnspan=2, pady=10)

add_button = ttk.Button(mainframe, text="Add Chore", command=add_chore)
add_button.grid(row=2, column=0, sticky=tk.W)

delete_button = ttk.Button(mainframe, text="Delete Chore", command=delete_chore)
delete_button.grid(row=2, column=1, sticky=tk.E)

edit_button = ttk.Button(mainframe, text="Edit Chore", command=edit_chore)
edit_button.grid(row=3, column=0, columnspan=2, pady=5)

refresh_list()

root.mainloop()
