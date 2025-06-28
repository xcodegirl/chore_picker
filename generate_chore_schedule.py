import json
import random
from collections import defaultdict
from copy import deepcopy

# Load chores from JSON file
with open('chore_data.json', 'r') as f:
    data = json.load(f)

people = ['Alice', 'Bob', 'Charlie', 'Dana', 'Eli']
days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
weeks = 4  # Changed from 8 to 4 for one month
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

# Prepare a list of all Sundays (week, person) pairs
sundays = [(week, person) for week in range(1, weeks+1) for person in people]
# Flatten to a list of (week, person) for all Sundays
num_sundays = len(sundays)
# Only assign as many monthly chores as there are Sundays, and each monthly chore exactly once
selected_monthly_chores = random.sample(monthly_chores, min(num_sundays, len(monthly_chores)))
# Map each (week, person) to a unique monthly chore, or leave blank if not enough chores
monthly_chore_assignments = {}
for idx, (week, person) in enumerate(sundays):
    if idx < len(selected_monthly_chores):
        monthly_chore_assignments[(week, person)] = selected_monthly_chores[idx]
    else:
        monthly_chore_assignments[(week, person)] = None

# Assign monthly chores at the start of the month (first Sunday)
num_months = 1
weeks_per_month = weeks // num_months
monthly_chores_split = [monthly_chores[i::num_months] for i in range(num_months)]
monthly_chore_assignments = {}
for month in range(num_months):
    start_week = month * weeks_per_month + 1
    end_week = start_week + weeks_per_month
    chores_this_month = monthly_chores_split[month]
    # Assign one unique monthly chore per person on the first Sunday of the month
    for idx, person in enumerate(people):
        week = start_week
        if idx < len(chores_this_month):
            monthly_chore_assignments[(week, person)] = chores_this_month[idx]
        else:
            monthly_chore_assignments[(week, person)] = None
    # If there are more chores than people, assign the rest to the next Sundays in this month
    extra_chores = chores_this_month[len(people):]
    for i, chore in enumerate(extra_chores):
        week = start_week + 1 + (i // len(people))
        person = people[i % len(people)]
        if week < end_week:
            monthly_chore_assignments[(week, person)] = chore

# Assign monthly chores every other week (on Sundays of weeks 1 and 3)
monthly_chore_assignments = {}
monthly_weeks = [1, 3]  # Weeks to assign monthly chores
monthly_chores_to_assign = monthly_chores[:len(monthly_weeks)*len(people)]
for i, week in enumerate(monthly_weeks):
    for j, person in enumerate(people):
        idx = i * len(people) + j
        if idx < len(monthly_chores_to_assign):
            monthly_chore_assignments[(week, person)] = monthly_chores_to_assign[idx]
        else:
            monthly_chore_assignments[(week, person)] = None

for week in range(1, weeks+1):
    used_slots = set()
    prev_day_chores = {person: None for person in people}
    # Track previous week's weekly chore assignments for each person
    prev_weekly_assignments = {person: set() for person in people}
    if week > 1:
        prev_week = f'Week {week-1}'
        for person in people:
            for day in days:
                for chore in schedule[prev_week][day].get(person, []):
                    if chore in weekly_chores or (isinstance(chore, dict) and chore.get('chore') in [w['chore'] for w in weekly_chores]):
                        prev_weekly_assignments[person].add(chore['chore'] if isinstance(chore, dict) else chore)
    # Assign fixed-day weekly chores to a random person on their specified day
    fixed_day_slots = [(chore['dayofweek'], chore) for chore in fixed_day_chores]
    assigned_weekly_this_week = set()
    assigned_people_days = set()
    # Assign each fixed-day weekly chore exactly once per week
    for day, chore in fixed_day_slots:
        available_people = [p for p in people if (day, p) not in assigned_people_days]
        if available_people:
            person = random.choice(available_people)
            schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
            assigned_weekly_this_week.add(chore['chore'])
            assigned_people_days.add((day, person))
    # Assign other weekly chores exactly once per week
    week_other_weekly_chores = random.sample(other_weekly_chores, min(len(other_weekly_chores), len(days)*len(people)-len(assigned_people_days)))
    # Find all available (day, person) slots not already used by fixed-day chores
    available_slots = [(d, p) for d in days for p in people if (d, p) not in assigned_people_days]
    random.shuffle(available_slots)
    for chore, slot in zip(week_other_weekly_chores, available_slots):
        day, person = slot
        schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
        assigned_weekly_this_week.add(chore['chore'])
        assigned_people_days.add((day, person))
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
            for person in people:
                monthly_choice = monthly_chore_assignments.get((week, person))
                if monthly_choice:
                    schedule[f'Week {week}']['Sunday'].setdefault(person, []).append(monthly_choice)
# Save to file
with open('chore_schedule.json', 'w') as f:
    json.dump(schedule, f, indent=2)

# Calculate summary stats
summary = {person: {'weeks': {}, 'month': {'score': 0, 'time': 0}, 'two_months': {'score': 0, 'time': 0}} for person in people}
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
        summary[person]['two_months']['score'] += week_score
        summary[person]['two_months']['time'] += week_time
        # For backward compatibility, keep 'month' as the first 4 weeks
        if int(week.split()[-1]) <= 4:
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
monthly_chore_counts = {ch['chore']: 0 for ch in monthly_chores}
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
                # Count monthly chore assignments
                if chore['chore'] in monthly_chore_counts:
                    monthly_chore_counts[chore['chore']] += 1

# Check for monthly chores assigned more than once
monthly_duplicates = [chore for chore, count in monthly_chore_counts.items() if count > 1]

if any(unassigned.values()) or monthly_duplicates:
    print('Unassigned or duplicate chores:')
    for k, chores in unassigned.items():
        if chores:
            print(f'  {k.capitalize()} chores not assigned: {sorted(chores)}')
    if monthly_duplicates:
        print(f'  Monthly chores assigned more than once: {sorted(monthly_duplicates)}')
else:
    print('All chores assigned at least once in the month, and no monthly chores assigned more than once.')

# Check that all daily chores are done at least 14 times and weekly chores at least 2 times in the month
chore_counts = {'daily': {ch['chore']: 0 for ch in daily_chores},
                'weekly': {ch['chore']: 0 for ch in weekly_chores}}
for week, week_data in schedule.items():
    for day in days:
        for person in people:
            for chore in week_data.get(day, {}).get(person, []):
                if chore['chore'] in chore_counts['daily']:
                    chore_counts['daily'][chore['chore']] += 1
                if chore['chore'] in chore_counts['weekly']:
                    chore_counts['weekly'][chore['chore']] += 1

daily_under_14 = [chore for chore, count in chore_counts['daily'].items() if count < 14]
daily_over_28 = [chore for chore, count in chore_counts['daily'].items() if count > 28]
weekly_under_2 = [chore for chore, count in chore_counts['weekly'].items() if count < 2]
weekly_over_4 = [chore for chore, count in chore_counts['weekly'].items() if count > 4]

if not daily_under_14 and not daily_over_28 and not weekly_under_2 and not weekly_over_4:
    print('All daily chores are done at least 14 times and no more than 28 times, and all weekly chores at least 2 times and no more than 4 times in the schedule period.')
else:
    if daily_under_14:
        print('Daily chores NOT done at least 14 times in the schedule period:', sorted(daily_under_14))
    if daily_over_28:
        print('Daily chores done MORE than 28 times in the schedule period:', sorted(daily_over_28))
    if weekly_under_2:
        print('Weekly chores NOT done at least 2 times in the schedule period:', sorted(weekly_under_2))
    if weekly_over_4:
        print('Weekly chores done MORE than 4 times in the schedule period:', sorted(weekly_over_4))

# Check fairness of summary (score and time) for all people
month_scores = [summary[person]['month']['score'] for person in people]
month_times = [summary[person]['month']['time'] for person in people]
max_score = max(month_scores)
min_score = min(month_scores)
max_time = max(month_times)
min_time = min(month_times)
score_diff = max_score - min_score
time_diff = max_time - min_time
print(f'Chore summary fairness check:')
print(f'  Score range: {min_score} - {max_score} (diff: {score_diff})')
print(f'  Time range: {min_time} - {max_time} (diff: {time_diff})')
if score_diff <= 2 and time_diff <= 30:
    print('  The schedule is FAIR: score and time are well balanced across all people.')
else:
    print('  The schedule is NOT FAIR: consider re-running or adjusting logic for better balance.')
