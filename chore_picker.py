import json
import random
import tkinter as tk
from tkinter import ttk, messagebox

# Load chores from JSON file
def load_chores(filename):
    with open(filename, 'r') as f:
        data = json.load(f)
    return data['household_chores']

def pick_random_chore(chores, category):
    if category == "all":
        all_chores = []
        for cat in chores.values():
            all_chores.extend(cat)
        if not all_chores:
            return None
        return random.choice(all_chores)
    if category not in chores:
        return None
    return random.choice(chores[category])

def show_chore():
    category = category_var.get()
    chore = pick_random_chore(chores, category)
    if chore:
        result = f"Chore: {chore['chore']}\nScore: {chore['score']}\nTime Estimate: {chore['time_estimate']} min"
        result_label.config(text=result)
    else:
        result_label.config(text="No chores found for this category.")

# Main program
chores = load_chores('chore_data.json')

root = tk.Tk()
root.title("Chore Picker")

mainframe = ttk.Frame(root, padding="20 20 20 20")
mainframe.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

category_options = ["all"] + list(chores.keys())
category_var = tk.StringVar(value=category_options[0])
category_label = ttk.Label(mainframe, text="Choose a category:")
category_label.grid(row=0, column=0, sticky=tk.W)

category_menu = ttk.Combobox(mainframe, textvariable=category_var, values=category_options, state="readonly")
category_menu.grid(row=0, column=1, sticky=(tk.W, tk.E))

pick_button = ttk.Button(mainframe, text="Pick Random Chore", command=show_chore)
pick_button.grid(row=1, column=0, columnspan=2, pady=10)

result_label = ttk.Label(mainframe, text="", font=("Arial", 12), justify=tk.LEFT)
result_label.grid(row=2, column=0, columnspan=2, sticky=tk.W)

root.mainloop()
