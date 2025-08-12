import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os

class ChoreScheduleGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Chore Schedule Generator")
        self.geometry("400x700")  # Increased height from 440 to 700
        self.resizable(False, False)

        # Load people from people.json if available
        import json
        try:
            with open("people.json", "r") as pf:
                self.default_names = json.load(pf)
        except Exception:
            self.default_names = ['Archimedes', 'Ricardo', 'Curia', 'Joanne', 'Hypatia']

        # People checkboxes
        tk.Label(self, text="Include these people:").pack(pady=(20, 5))
        self.people_vars = []
        for name in self.default_names:
            var = tk.BooleanVar(value=True)
            cb = tk.Checkbutton(self, text=name, variable=var)
            cb.pack(anchor='w', padx=40)
            self.people_vars.append((name, var))

        # Fairness threshold controls
        fair_frame = tk.Frame(self)
        fair_frame.pack(pady=(10, 0))
        tk.Label(fair_frame, text="Max score diff:").grid(row=0, column=0, sticky='e')
        self.fair_score_var = tk.IntVar(value=12)
        tk.Spinbox(fair_frame, from_=0, to=100, width=5, textvariable=self.fair_score_var).grid(row=0, column=1, padx=5)
        tk.Label(fair_frame, text="Max time diff (min):").grid(row=0, column=2, sticky='e')
        self.fair_time_var = tk.IntVar(value=60)
        tk.Spinbox(fair_frame, from_=0, to=1000, width=5, textvariable=self.fair_time_var).grid(row=0, column=3, padx=5)

        # Chore capacity control
        cap_frame = tk.Frame(self)
        cap_frame.pack(pady=(5, 0))
        tk.Label(cap_frame, text="Chore capacity (per person/day):").pack(side='left')
        self.chore_capacity_var = tk.IntVar(value=2)
        tk.Spinbox(cap_frame, from_=1, to=10, width=4, textvariable=self.chore_capacity_var).pack(side='left', padx=5)

        # Generate and Launch buttons in a frame
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=20)
        self.generate_btn = ttk.Button(btn_frame, text="Generate Schedule", command=self.generate_schedule)
        self.generate_btn.pack(side='left', padx=10)
        self.launch_btn = ttk.Button(btn_frame, text="Open HTML Schedule", command=self.open_html)
        self.launch_btn.pack(side='left', padx=10)

        # Edit Chore List button
        self.edit_chore_btn = ttk.Button(self, text="Edit Chore List", command=self.open_chore_list_editor)
        self.edit_chore_btn.pack(pady=(0, 10))

        # Output
        self.output_label = tk.Label(self, text="", fg="green", wraplength=360, justify='center')
        self.output_label.pack(pady=5)
        self.output_text = tk.Text(self, height=18, width=48, wrap='word', state='disabled')
        self.output_text.pack(pady=5)

    def generate_schedule(self):
        people = [name for name, var in self.people_vars if var.get()]
        if len(people) < 2:
            messagebox.showerror("Too few people", "Please select at least two people.")
            return
        import tempfile, json
        with tempfile.NamedTemporaryFile('w', delete=False, suffix='.json') as tf:
            json.dump(people, tf)
            tf.flush()
            tfname = tf.name
        # Get fairness thresholds from GUI
        fair_score = str(self.fair_score_var.get())
        fair_time = str(self.fair_time_var.get())
        chore_capacity = str(self.chore_capacity_var.get())
        # First, generate the schedule JSON
        cmd1 = [sys.executable, 'generate_chore_schedule.py',
                '--fair-score-diff', fair_score, '--fair-time-diff', fair_time,
                '--chore-capacity', chore_capacity]
        # Then, generate the HTML
        cmd2 = [sys.executable, 'generate_chore_schedule_html.py']
        try:
            result1 = subprocess.run(cmd1, capture_output=True, text=True, check=True)
            result2 = subprocess.run(cmd2, capture_output=True, text=True, check=True)
            self.output_label.config(text="Schedule and HTML generated!\nSee chore_schedule.json and chore_schedule.html.", fg="green")
            output = (result1.stdout or '') + (result1.stderr or '') + '\n' + (result2.stdout or '') + (result2.stderr or '')
        except subprocess.CalledProcessError as e:
            self.output_label.config(text="Error: " + e.stderr, fg="red")
            output = e.stdout or ''
            if e.stderr:
                output += '\n' + e.stderr
        finally:
            os.unlink(tfname)
        self.output_text.config(state='normal')
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, output.strip())
        self.output_text.config(state='disabled')

    def open_html(self):
        import webbrowser
        html_path = os.path.abspath("chore_schedule.html")
        if os.path.exists(html_path):
            webbrowser.open(f"file://{html_path}")
        else:
            messagebox.showerror("Not Found", "chore_schedule.html not found. Please generate the schedule first.")

    def open_chore_list_editor(self):
        # Open the chore_list_editor.py script in a new process
        import subprocess, sys
        try:
            subprocess.Popen([sys.executable, 'chore_list_editor.py'])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open chore list editor: {e}")

if __name__ == '__main__':
    app = ChoreScheduleGUI()
    app.mainloop()
