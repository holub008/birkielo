# TODO this should be shared
def extract_discipline_from_race_name(race_name):
    race_name_lower = race_name.lower()
    if 'skate' in race_name_lower or 'free' in race_name_lower:
        return 'freestyle'
    elif 'classic' in race_name_lower:
        return 'classic'
    elif 'pursuit' in race_name_lower or 'skiathlon' in race_name_lower:
        return 'pursuit'
    elif 'sitski' in race_name_lower or 'sit ski' in race_name_lower:
        return 'sitski'
    # sigh...
    elif race_name_lower == 'vasa':
        return 'freestyle'
    elif race_name_lower == 'dala':
        return 'freestyle'

    return None

# TODO this should be shared
def attach_placements(results):
    time_ordered_results = results.sort_values('duration')

    time_ordered_results['gender_place'] = time_ordered_results\
        .groupby(['date', 'discipline', 'gender'])\
        .cumcount() + 1
    time_ordered_results['overall_place'] = time_ordered_results\
        .groupby(['date', 'discipline'])\
        .cumcount() + 1

    return time_ordered_results