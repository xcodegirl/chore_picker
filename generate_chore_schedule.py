import json
import math
import random
from collections import defaultdict

people = ['Archimedes', 'Ricardo', 'Curia', 'Joanne', 'Hypatia']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weeks = 10  # Number of weeks to generate

# Load chores from JSON file
with open('chore_data.json', 'r') as f:
    data = json.load(f)

weekly_chores = data['household_chores']['weekly']
daily_chores = data['household_chores']['daily']

# Randomize chore lists before starting
random.shuffle(weekly_chores)
random.shuffle(daily_chores)

fixed_day_chores = [ch for ch in weekly_chores if 'dayofweek' in ch]
other_weekly_chores = [ch for ch in weekly_chores if 'dayofweek' not in ch]
required_daily_chores = [ch for ch in daily_chores if ch.get('required_daily')]
other_daily_chores = [ch for ch in daily_chores if not ch.get('required_daily')]

schedule = defaultdict(lambda: defaultdict(dict))

start_idx = random.randrange(0,4)
for week in range(1, weeks + 1):
    # Assign required daily in round-robin
    for day in days:
        person_idx = start_idx
        for chore in required_daily_chores:
            person = people[person_idx % len(people)]
            schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
            person_idx += 1
        start_idx += 1

start_idx = random.randrange(0,4)
extra_idx = random.randrange(0,4)
done_extra = False
chore_idx = 0
for week in range(1, weeks + 1):
    day_idx = 0
    person_idx = start_idx
    for day in days:
        if (day != "Sunday"):
            for i in range(0,len(people)):
                person = people[person_idx % len(people)]
                if (len(schedule[f'Week {week}'][day].get(person, [])) == 0):                 
                    chore = other_daily_chores[chore_idx % len(other_daily_chores)]
                    chore_idx += 1
                    schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
                person_idx += 1                
        day_idx += 1
    start_idx += 1

week_idx = 0
chore_idx = 0
start_idx = random.randrange(0,4)
for week in range(1, weeks + 1):
    person_idx = start_idx
    day = "Sunday"
    for i in range(0,len(people)):
        person = people[person_idx % len(people)]
        if (len(schedule[f'Week {week}'][day].get(person, [])) == 0):                 
            chore = other_weekly_chores[chore_idx % len(other_weekly_chores)] 
            chore_idx += 1
            schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
        person_idx += 1
    start_idx += 1
    week_idx += 1


# Save to file
with open('chore_schedule.json', 'w') as f:
    json.dump({k: v for k, v in schedule.items()}, f, indent=2)

print('Chore schedule saved to chore_schedule.json')

# Run the HTML generation script at the end
import subprocess
subprocess.run(['python3', 'generate_chore_schedule_html.py'])