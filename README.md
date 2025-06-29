# Chore Picker & Editor

This project provides several tools for managing, picking, and scheduling household chores from a JSON file, including both GUI and command-line utilities.

## Files

- `chore_picker.py`: Pick a random chore from a selected category or from all chores.
- `chore_list_editor.py`: Add, edit, or delete chores in the JSON file using a user-friendly interface.
- `generate_chore_schedule.py`: Generate a fair, balanced schedule for all people, assigning daily, weekly, and monthly chores.
- `generate_chore_schedule_html.py`: Create a full, color-coded HTML table of the entire schedule for all people and days.
- `chore_day_person_view.html`: Web-based viewer for per-person, per-day schedule lookup. Use URL parameters to select the view (see usage below).
- `chore_data.json`: The data file containing all chores, organized by category.
- `chore_schedule_gui.py`: Tkinter GUI to set the number of people and generate a schedule interactively.

## Requirements
- Python 3.x
- Tkinter (usually included with Python)

## Usage

### 1. Pick a Random Chore
Run:
```bash
python3 chore_picker.py
```
- Select a category (or "all" for any chore).
- Click "Pick Random Chore" to see a random selection.

### 2. Edit the Chore List
Run:
```bash
python3 chore_list_editor.py
```
- Select a category.
- Add, edit, or delete chores. All changes are saved to the JSON file.

### 3. Generate a Schedule (Command-line)
Run:
```bash
python3 generate_chore_schedule.py
```
- This will create `chore_schedule.json` and `chore_data.json` in the current directory.
- Use `--no-balance` to disable the fairness post-processing step if desired.
- Prints assignment and fairness reports to the terminal.

### 4. Generate a Schedule (GUI)
Run:
```bash
python3 chore_schedule_gui.py
```
- Set the number of people (2–10) and click "Generate Schedule".
- The schedule will be saved as `chore_schedule.json`.

### 5. View Schedule in Browser
1. **Start a local web server** in the `chore_picker` directory (required for browser security):
   ```bash
   python3 -m http.server 8000
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:8000/chore_day_person_view.html?person=Alice&week=2&day=Monday
   ```
   - Change `person`, `week`, and `day` in the URL to view any combination you want.
   - Valid values:
     - `person`: Alice, Bob, Charlie, Dana, Eli
     - `week`: 1, 2, 3, 4
     - `day`: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday

> **Note:** Opening the HTML file directly (with a `file://` URL) will not work due to browser security restrictions. Always use a local web server as shown above.

---

## Fairness Balancing in Chore Scheduling

The schedule generator (`generate_chore_schedule.py`) includes advanced fairness logic to ensure chores are distributed as evenly as possible among all participants:

- **Score and Time Balancing:**
  - Each chore has a "score" and "time_estimate" value.
  - The script checks that the total score and time assigned to each person are within configurable thresholds (see `FAIR_SCORE_DIFF` and `FAIR_TIME_DIFF` in the script).

- **Post-Processing for Fairness:**
  - After the initial schedule is created, the script can perform a post-processing step to swap chores between people, seeking to minimize the difference in total score and time.
  - This step uses a "best-of-all-pairs" swap algorithm to find the most effective swaps for balancing.
  - The process continues until the fairness thresholds are met or no further improvement is possible.
  - You can disable this step with the `--no-balance` command-line option.

- **Fairness Reporting:**
  - The script prints a summary showing the score and time range for all people, and whether the final schedule is considered "FAIR".
  - If not fair, it suggests re-running or adjusting the logic.

---

## Other Python Scripts

### `generate_chore_schedule.py`
- **Purpose:** Generates a fair, balanced schedule for all people, assigning daily, weekly, and monthly chores.
- **How to use:**
  ```bash
  python3 generate_chore_schedule.py
  ```
  - Outputs `chore_schedule.json` (the full schedule) and `chore_summary.json` (summary stats).
  - Use `--no-balance` to disable the fairness post-processing step if desired.
  - Prints assignment and fairness reports to the terminal.

### `generate_chore_schedule_html.py`
- **Purpose:** Creates a full, color-coded HTML table of the entire schedule for all people and days.
- **How to use:**
  ```bash
  python3 generate_chore_schedule_html.py
  ```
  - Outputs `chore_schedule.html` for easy viewing in a browser.

### `chore_schedule_gui.py`
- **Purpose:** Interactive GUI to set the number of people and generate a schedule.
- **How to use:**
  ```bash
  python3 chore_schedule_gui.py
  ```
  - Set the number of people (2–10) and click "Generate Schedule".
  - The schedule will be saved as `chore_schedule.json`.

### Command-line example for custom people file
You can also run the schedule generator directly with a custom people file:
```bash
python3 generate_chore_schedule.py --people-file people.json
```
- `people.json` should be a JSON array of names, e.g.:
  ```json
  ["Alice", "Bob", "Charlie", "Dana", "Eli"]
  ```


---

## Notes
- The JSON file must be in the same directory as the scripts.
- If you edit the JSON manually, ensure the format matches the examples.

## Example JSON Structure
```
{
  "household_chores": {
    "daily": [
      {"chore": "Make the bed", "score": 1, "time_estimate": 3},
      ...
    ],
    ...
  },
  "metadata": { ... }
}
```
## Author

xcodegirl

## License
MIT

## Disclaimer

The initial data file was generated by DeepSeek. The Python scripts and interface design were created with the assistance of GitHub Copilot (GPT 4.1).
