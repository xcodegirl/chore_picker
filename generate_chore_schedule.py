import json
import math
import random
from collections import defaultdict

people = ['Archimedes', 'Ricardo', 'Curia', 'Joanne', 'Hypatia']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weeks = 5  # Number of weeks to generate

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
start_idx = 0
max_assigned_length = 0  # Track the maximum length of any assigned chore list

for week in range(1, weeks + 1):
    person_idx = start_idx
    # Assign fixed-day weekly chores in round-robin
    for chore in fixed_day_chores:
        person = people[person_idx % len(people)]
        day = chore['dayofweek']
        schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
        person_idx += 1
    start_idx += 1

for week in range(1, weeks + 1):
    # Assign required daily in round-robin
    for day in days:
        person_idx = start_idx
        for chore in required_daily_chores:
            max_chores = 99
            for assign in people:
                if len(schedule[f'Week {week}'][day].get(assign, [])) < max_chores:
                    max_chores = len(schedule[f'Week {week}'][day].get(assign, []))  
            print('Max assigned chore list length:', max_chores)
            person = people[person_idx % len(people)]
            loop_count = 0
            while (len(schedule[f'Week {week}'][day].get(person, [])) != max_chores and loop_count < len(people)):
                person_idx += 1
                loop_count += 1
                person = people[person_idx % len(people)]
                print('compare:', len(schedule[f'Week {week}'][day].get(person, [])))
            schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
            person_idx += 1
        start_idx = person_idx + 1

start_idx = 0
for week in range(1, weeks + 1):
    for day in days:
        person_idx = start_idx
        if (day != "Saturday") and (day != "Sunday"):
            for chore in other_daily_chores:
                max_chores = 99
                for assign in people:
                    if len(schedule[f'Week {week}'][day].get(assign, [])) < max_chores:
                        max_chores = len(schedule[f'Week {week}'][day].get(assign, []))                 
                person = people[person_idx % len(people)]
                loop_count = 0
                while (len(schedule[f'Week {week}'][day].get(person, [])) != max_chores and loop_count < len(people)):
                    person_idx += 1
                    loop_count += 1
                    person = people[person_idx % len(people)]
                schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
                person_idx += 1
        start_idx += 1

week_idx = 0
for week in range(1, weeks + 1):
        person_idx = start_idx
        day = "Sunday"
        chore_idx = 0
        for chore in other_weekly_chores:
            max_chores = 99
            for assign in people:
                if len(schedule[f'Week {week}'][day].get(assign, [])) < max_chores:
                    max_chores = len(schedule[f'Week {week}'][day].get(assign, []))                 
            if (week_idx % 2 == chore_idx % 2) and week_idx != 4:                 
                person = people[person_idx % len(people)]
                loop_count = 0
                while (len(schedule[f'Week {week}'][day].get(person, [])) != max_chores and loop_count < len(people)):
                    person_idx += 1
                    loop_count += 1
                    person = people[person_idx % len(people)]
                schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
                person_idx += 1
            chore_idx += 1
        start_idx += 1
        week_idx += 1

# Save to file
with open('chore_schedule.json', 'w') as f:
    json.dump({k: v for k, v in schedule.items()}, f, indent=2)

print('Chore schedule saved to chore_schedule.json')

# Run the HTML generation script at the end
import subprocess
subprocess.run(['python3', 'generate_chore_schedule_html.py'])