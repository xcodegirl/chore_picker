import json

# Load the generated schedule
with open('chore_schedule.json', 'r') as f:
    schedule = json.load(f)

html = ['<html>', '<head><title>Chore Schedule</title>',
        '<style>body{font-family:sans-serif;} table{border-collapse:collapse;margin:20px;} th,td{border:1px solid #aaa;padding:6px;} th{background:#eee;} .week-title{font-size:1.3em;margin-top:30px;}</style>',
        '</head>', '<body>']
html.append('<h1>Monthly Chore Schedule</h1>')

for week, week_data in schedule.items():
    html.append(f'<div class="week-title">{week}</div>')
    html.append('<table>')
    html.append('<tr><th>Day</th><th>Alice</th><th>Bob</th><th>Charlie</th></tr>')
    for day in ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']:
        html.append(f'<tr><td>{day}</td>')
        for person in ['Alice', 'Bob', 'Charlie']:
            chore = week_data.get(day, {}).get(person)
            if chore:
                desc = f"<b>{chore['chore']}</b><br>Score: {chore['score']}<br>Time: {chore['time_estimate']} min"
            else:
                desc = ''
            html.append(f'<td>{desc}</td>')
        html.append('</tr>')
    html.append('</table>')

html.append('</body></html>')

with open('chore_schedule.html', 'w') as f:
    f.write('\n'.join(html))

print('Chore schedule HTML page generated as chore_schedule.html')
