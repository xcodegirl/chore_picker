import json
import random
from collections import defaultdict
from copy import deepcopy

# Load chores from JSON file
with open('chore_data.json', 'r') as f:
    data = json.load(f)

people = ['Alice', 'Bob', 'Charlie', 'Dana', 'Eli']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weeks = 4
chore_capacity = 2  # Number of chores per person per day

# Separate chores by type
weekly_chores = data['household_chores']['weekly']
daily_chores = data['household_chores']['daily']
monthly_chores = data['household_chores']['monthly']

# Identify weekly chores with a specific dayofweek
fixed_day_chores = []
other_weekly_chores = []
for chore in weekly_chores:
    if 'dayofweek' in chore:
        fixed_day_chores.append(chore)
    else:
        other_weekly_chores.append(chore)

# Identify required daily chores
required_daily_chores = [ch for ch in daily_chores if ch.get('required_daily')]
other_daily_chores = [ch for ch in daily_chores if not ch.get('required_daily')]

schedule = defaultdict(lambda: defaultdict(dict))
random.seed()

for week in range(1, weeks+1):
    used_slots = set()
    # Track previous day's assignments for each person
    prev_day_chores = {person: None for person in people}
    # Assign fixed-day weekly chores to a random person on their specified day
    for chore in fixed_day_chores:
        day = chore['dayofweek']
        available_people = [p for p in people if (day, p) not in used_slots or len(schedule[f'Week {week}'][day].get(p, [])) < chore_capacity]
        person = random.choice(available_people)
        count = len(schedule[f'Week {week}'][day].get(person, []))
        if count < chore_capacity:
            schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
            used_slots.add((day, person))
    # Shuffle and assign other weekly chores
    week_weekly_chores = random.sample(other_weekly_chores, len(other_weekly_chores))
    weekly_slots = [(d, p) for d in days for p in people if len(schedule[f'Week {week}'][d].get(p, [])) < chore_capacity]
    random.shuffle(weekly_slots)
    for chore, slot in zip(week_weekly_chores, weekly_slots):
        day, person = slot
        schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
        used_slots.add((day, person))
    # Fill remaining slots with daily/monthly chores
    for i, day in enumerate(days):
        assigned_daily = set()
        # Assign required daily chores first, one per person, round-robin
        people_cycle = people.copy()
        random.shuffle(people_cycle)
        for req_chore in required_daily_chores:
            assigned = False
            for person in people_cycle:
                chores_for_person = schedule[f'Week {week}'][day].get(person, [])
                # Don't assign same required daily chore as previous day
                if i > 0 and prev_day_chores[person] == req_chore['chore']:
                    continue
                if len(chores_for_person) < chore_capacity:
                    schedule[f'Week {week}'][day].setdefault(person, []).append(req_chore)
                    assigned_daily.add(req_chore['chore'])
                    prev_day_chores[person] = req_chore['chore']
                    assigned = True
                    break
            if not assigned:
                # If all people are at capacity or blocked, assign anyway to someone with capacity
                for person in people_cycle:
                    chores_for_person = schedule[f'Week {week}'][day].get(person, [])
                    if len(chores_for_person) < chore_capacity:
                        schedule[f'Week {week}'][day].setdefault(person, []).append(req_chore)
                        assigned_daily.add(req_chore['chore'])
                        prev_day_chores[person] = req_chore['chore']
                        break
        # Now fill remaining slots as before
        for person in people:
            chores_for_person = schedule[f'Week {week}'][day].get(person, [])
            count = len(chores_for_person)
            while count < chore_capacity:
                available_daily = [ch for ch in other_daily_chores if ch['chore'] not in assigned_daily and (i == 0 or prev_day_chores[person] != ch['chore'])]
                if available_daily:
                    chore = random.choice(available_daily)
                    assigned_daily.add(chore['chore'])
                    prev_day_chores[person] = chore['chore']
                else:
                    if monthly_chores:
                        chore = random.choice(monthly_chores)
                    else:
                        chore = random.choice(daily_chores)
                    prev_day_chores[person] = chore['chore']
                schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
                count += 1
        # Add one extra monthly chore to each Sunday for each person
        if day == 'Sunday':
            available_monthlies = monthly_chores.copy()
            random.shuffle(available_monthlies)
            for idx, person in enumerate(people):
                # Avoid assigning the same monthly chore twice to the same person in the same month
                already_assigned = set()
                for w in range(1, week+1):
                    for c in schedule[f'Week {w}']['Sunday'].get(person, []):
                        already_assigned.add(c['chore'])
                # Pick a monthly chore not already assigned to this person on any Sunday
                monthly_choice = None
                for m in available_monthlies:
                    if m['chore'] not in already_assigned:
                        monthly_choice = m
                        break
                if not monthly_choice:
                    monthly_choice = random.choice(monthly_chores)
                schedule[f'Week {week}']['Sunday'].setdefault(person, []).append(monthly_choice)
# Save to file
with open('chore_schedule.json', 'w') as f:
    json.dump(schedule, f, indent=2)

# Calculate summary stats
summary = {person: {'weeks': {}, 'month': {'score': 0, 'time': 0}} for person in people}
for week, week_data in schedule.items():
    for person in people:
        week_score = 0
        week_time = 0
        for day in days:
            chores = week_data.get(day, {}).get(person, [])
            for chore in chores:
                week_score += chore['score']
                week_time += chore['time_estimate']
        summary[person]['weeks'][week] = {'score': week_score, 'time': week_time}
        summary[person]['month']['score'] += week_score
        summary[person]['month']['time'] += week_time

with open('chore_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)

print('Chore schedule saved to chore_schedule.json')
print('Chore summary saved to chore_summary.json')

# Check for unassigned chores
unassigned = {'daily': set(ch['chore'] for ch in daily_chores),
              'weekly': set(ch['chore'] for ch in weekly_chores),
              'monthly': set(ch['chore'] for ch in monthly_chores)}
for week, week_data in schedule.items():
    for day in days:
        for person in people:
            for chore in week_data.get(day, {}).get(person, []):
                if chore['chore'] in unassigned['daily']:
                    unassigned['daily'].remove(chore['chore'])
                if chore['chore'] in unassigned['weekly']:
                    unassigned['weekly'].remove(chore['chore'])
                if chore['chore'] in unassigned['monthly']:
                    unassigned['monthly'].remove(chore['chore'])

if any(unassigned.values()):
    print('Unassigned chores:')
    for k, chores in unassigned.items():
        if chores:
            print(f'  {k.capitalize()} chores not assigned: {sorted(chores)}')
else:
    print('All chores assigned at least once in the month.')

# Check that all daily and weekly chores have been done at least once per month
unassigned_month = {'daily': set(ch['chore'] for ch in daily_chores),
                    'weekly': set(ch['chore'] for ch in weekly_chores)}
for week, week_data in schedule.items():
    for day in days:
        for person in people:
            for chore in week_data.get(day, {}).get(person, []):
                if chore['chore'] in unassigned_month['daily']:
                    unassigned_month['daily'].remove(chore['chore'])
                if chore['chore'] in unassigned_month['weekly']:
                    unassigned_month['weekly'].remove(chore['chore'])

if not unassigned_month['daily'] and not unassigned_month['weekly']:
    print('All daily and weekly chores have been assigned at least once this month.')
else:
    if unassigned_month['daily']:
        print('Daily chores NOT assigned at least once this month:', sorted(unassigned_month['daily']))
    if unassigned_month['weekly']:
        print('Weekly chores NOT assigned at least once this month:', sorted(unassigned_month['weekly']))
