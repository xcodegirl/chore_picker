import json
import random
from collections import defaultdict
from copy import deepcopy

# Load chores from JSON file
with open('chore_data.json', 'r') as f:
    data = json.load(f)

people = ['Alice', 'Bob', 'Charlie']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weeks = 4

# Gather all chores to be done in a month
all_chores = []
all_chores.extend(data['household_chores']['daily'])
all_chores.extend(data['household_chores']['weekly'])
all_chores.extend(data['household_chores']['monthly'])

# Calculate total slots (3 people x 7 days x 4 weeks)
total_slots = len(people) * len(days) * weeks

# If chores < slots, repeat chores; if chores > slots, some people get more chores
chores_needed = deepcopy(all_chores)
while len(chores_needed) < total_slots:
    chores_needed.extend(deepcopy(all_chores))
chores_needed = chores_needed[:total_slots]
random.shuffle(chores_needed)

# Build the schedule
schedule = defaultdict(lambda: defaultdict(dict))
idx = 0
for week in range(1, weeks+1):
    for day in days:
        for person in people:
            schedule[f'Week {week}'][day][person] = chores_needed[idx]
            idx += 1

# Save to file
with open('chore_schedule.json', 'w') as f:
    json.dump(schedule, f, indent=2)

print('Chore schedule saved to chore_schedule.json')
