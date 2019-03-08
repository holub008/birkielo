import re

# TODO this should be shared
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


def attach_placements(results):
    time_ordered_results = results.sort_values('duration')

    time_ordered_results['gender_place'] = time_ordered_results\
        .groupby(['event_name', 'date', 'discipline', 'gender'])\
        .cumcount() + 1
    time_ordered_results['overall_place'] = time_ordered_results\
        .groupby(['event_name', 'date', 'discipline'])\
        .cumcount() + 1

    return time_ordered_results