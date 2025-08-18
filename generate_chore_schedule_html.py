import json

def min_to_hrmin(minutes):
    h = minutes // 60
    m = minutes % 60
    return f"{h}hr {m:02d}min" if h else f"0:{m:02d}"

# Load the generated schedule
with open('chore_schedule.json', 'r') as f:
    schedule = json.load(f)

# Load the chore data to get required and type info
with open('chore_data.json', 'r') as f:
    chore_data = json.load(f)

# Load summary for display
with open('chore_summary.json', 'r') as f:
    summary = json.load(f)

# Always use hardcoded people list
people = ['Archimedes', 'Ricardo', 'Curia', 'Joanne', 'Hypatia']

# Build lookup for required chores and type
chore_type = {}
required_daily = set()
required_weekly = set()
required_monthly = set()
for ch in chore_data['household_chores']['daily']:
    chore_type[ch['chore']] = 'Daily'
    if ch.get('required_daily'):
        required_daily.add(ch['chore'])
for ch in chore_data['household_chores']['weekly']:
    chore_type[ch['chore']] = 'Weekly'
    if ch.get('required_daily') or ch.get('dayofweek'):
        required_weekly.add(ch['chore'])
for ch in chore_data['household_chores'].get('monthly', []):
    chore_type[ch['chore']] = 'Monthly'
    if ch.get('required_daily') or ch.get('required_monthly'):
        required_monthly.add(ch['chore'])

html = ['<html>', '<head><title>Chore Schedule</title>',
        '<style>body{font-family:sans-serif;} table{border-collapse:collapse;margin:20px;} th,td{border:1px solid #aaa;padding:6px;} th{background:#eee;} .week-title{font-size:1.3em;margin-top:30px;} .required{color:#b00;font-weight:bold;} .chore-type{font-size:0.9em;color:#555;} .daily{color:#0057b7;} .weekly{color:#2e8b57;} .monthly{color:#ff8800;}</style>',
        '</head>', '<body>']
html.append('<h1>Monthly Chore Schedule</h1>')

for week, week_data in schedule.items():
    # Add a page break before each week except the first
    if week != list(schedule.keys())[0]:
        html.append('<div style="page-break-before: always;"></div>')
    html.append(f'<div class="week-title">{week}</div>')
    html.append('<table>')
    # Header row: Days
    html.append('<tr><th>Person</th>' + ''.join(f'<th>{day}</th>' for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']) + '</tr>')
    for person in people:
        html.append(f'<tr><td>{person}</td>')
        for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
            chores = week_data.get(day, {}).get(person, [])
            if not isinstance(chores, list):
                chores = [chores]
            if chores:
                desc = '<ul style="margin:0;padding-left:18px">'
                for chore in chores:
                    ctype = chore_type.get(chore['chore'], '')
                    req = ''
                    ctype_class = ''
                    if ctype == 'Daily':
                        ctype_class = 'daily'
                    elif ctype == 'Weekly':
                        ctype_class = 'weekly'
                    elif ctype == 'Monthly':
                        ctype_class = 'monthly'
                    if chore['chore'] in required_daily or chore['chore'] in required_weekly or chore['chore'] in required_monthly:
                        req = ' <span class="required">(*)</span>'
                    desc += (
                        f"<li><b>{chore['chore']}</b>{req}<br>"
                        f"<span class='chore-type {ctype_class}'>"
                        f"{ctype}"
                        f"</span></li>"
                    )
                desc += '</ul>'
            else:
                desc = ''
            html.append(f'<td>{desc}</td>')
        html.append('</tr>')
    html.append('</table>')

html.append('</body></html>')

with open('chore_schedule.html', 'w') as f:
    f.write('\n'.join(html))

print('Chore schedule HTML page generated as chore_schedule.html')
