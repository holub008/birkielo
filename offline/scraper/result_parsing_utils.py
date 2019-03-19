import re

def extract_discipline_from_race_name(race_name):
    race_name_lower = race_name.lower()
    if 'skate' in race_name_lower or 'free' in race_name_lower:
        return 'freestyle'
    elif 'classic' in race_name_lower:
        return 'classic'
    elif 'pursuit' in race_name_lower or 'skiathlon' in race_name_lower:
        return 'pursuit'
    elif 'sitski' in race_name_lower or 'sit ski' in race_name_lower or 'adaptive' in race_name_lower:
        return 'sitski'
    elif 'skijor' in race_name_lower:
        return 'skijor'
    # sigh...
    elif 'vasa' in race_name_lower:
        return 'freestyle'
    elif 'dala' in race_name_lower:
        return 'freestyle'
    elif 'bell ringer' in race_name_lower:
        return 'freestyle'

    return None


def extract_distance_from_race_name(race_name):
    race_name_lower = race_name.lower()
    matches = re.search(r'([0-9]+)k', race_name_lower)

    if matches:
        return int(matches.group(1))

    return None

# this is pretty darn imprecise, but there's a lot of variability in what this is expected to parse, so we go simple
def extract_gender_from_age_group_string(age_group):
    if age_group.lower().startswith('m'):
        return 'male'
    elif age_group.lower().startswith('f'):
        return 'female'
    else:
        return None


def attach_placements(results):
    time_ordered_results = results.sort_values('duration')

    time_ordered_results['gender_place'] = time_ordered_results\
        .groupby(['event_name', 'date', 'discipline', 'distance', 'gender'])\
        .cumcount() + 1
    time_ordered_results['overall_place'] = time_ordered_results\
        .groupby(['event_name', 'date', 'discipline', 'distance'])\
        .cumcount() + 1

    return time_ordered_results