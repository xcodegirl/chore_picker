day_idx = 0
week = 0
for week in range(1, weeks + 1):
    start_idx += 1
    person_idx = start_idx
    # Assign other daily and weekly in round-robin
    for chore in other_weekly_chores:
        person = people[person_idx % len(people)]
        day = "Sunday"
        #schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
        person_idx += 1

for week in range(1, weeks + 1):
    start_idx += 1
    person_idx = start_idx
    for day in days:
        if (day != "Saturday") and (day != "Sunday"):
            for chore in other_daily_chores:
                person = people[person_idx % len(people)]
                #schedule[f'Week {week}'][day].setdefault(person, []).append(chore)
                person_idx += 1
