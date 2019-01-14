##########################################################
## this file ingests data scraped in incremental_scrapers/
##########################################################

import re
from datetime import datetime

import pandas as pd
import numpy as np
from gender_guesser import detector

import scraper.race_record_committer as rrc
from db import get_connection
from scraper.racer_identity import RaceRecord
from scraper.racer_identity import RacerSource
from scraper.racer_matcher import RacerMatcher
from scraper.racer_identity import extract_name
from scraper.racer_identity import parse_time_millis

# the following get_*_results() functions return dataframes with the same structure, i.e. can be trivially appended
# note that these functions are not generalized to be reused - they contain manual/custom tweaks to the data
# that were not time efficient to generalize
RESULTS_DIRECTORY = "/Users/kholub/birkielo/offline/data/"
GENDER_DETECTOR = detector.Detector()


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


def extract_distance_from_text(text):
    matches = re.search(r'([0-9\.]+) *(k|K)', text)
    if matches:
        return float(matches.group(1))
    # special cases for the vasaloppet
    elif text == 'Vasa':
        return 58.0
    elif text == 'Dala':
        return 35.0
    elif text == 'Classic':
        return 42.0
    return None


def gopher_state_extract_date(race_name,
                              date_format="%m/%d/%Y"):
    matches = re.search(r'\(([0-9]+/[0-9]+/[0-9]+)\)$', race_name)
    if matches:
        return datetime.strptime(matches.group(1), date_format)

    return None


def get_gopher_state_results(filename="gopher_state.csv",
                             custom_distances=pd.DataFrame(
                                                    [
                                                        ['Big Island and Back (2/3/2018)', 'Adult Skate', 10 * 1000],
                                                        ['Big Island and Back (2/3/2018)', 'Adult Classic', 10 * 1000],
                                                        ['Minnesota Pursuit Champs (2/28/2016)', 'Individual Pursuit', 10 * 1000],
                                                        ['Big Island and Back (1/30/2016)', 'Adult Skate', 10 * 1000],
                                                        ['Big Island and Back (1/30/2016)', 'Adult Classic', 10 * 1000],
                                                        ['MN Pursuit Champs (3/1/2015)', 'Indiv Pursuit', 10 * 1000]
                                                    ], columns=['event_name', 'race_name', 'distance']),
                             ignore_races=pd.DataFrame(
                                 [
                                     # birkielo does not exploit the youth :)
                                     # (it could be fun to include, but these races have no distance)
                                     ['Big Island and Back (2/3/2018)', 'Youth Skate'],
                                     ['Big Island and Back (2/3/2018)', 'Youth Classic'],
                                     ['Minnesota Pursuit Champs (2/28/2016)', 'U 14 Freestyle'],
                                     ['Big Island and Back (1/30/2016)', 'HS School Skate'],
                                     # ... or use team results
                                     ['Minnesota Pursuit Champs (2/28/2016)', 'Ski Store Pursuit'],
                                     ['Minnesota Pursuit Champs (2/28/2016)', 'College Pursuit'],
                                     ['MN Pursuit Champs (3/1/2015)', 'Pursuit Relay'],
                                 ], columns=['event_name', 'race_name'])):
    raw_results = pd.read_csv(RESULTS_DIRECTORY + filename)

    raw_results = raw_results.merge(ignore_races, how='left', on=['event_name', 'race_name'], indicator=True)
    raw_results = raw_results[raw_results._merge == 'left_only']

    raw_results = raw_results.merge(custom_distances, how="left", on=['event_name', 'race_name'])

    raw_results['name'] = raw_results.first_name + " " + raw_results.last_name
    raw_results['gender'] = np.where(raw_results.gender == 'M', 'male', 'female')
    raw_results['discipline'] = [extract_discipline_from_race_name(name) for name in raw_results.race_name]
    # there's a bunch of snow shoe, team, and running events mixed in - filter them out if no discernible discipline
    raw_results = raw_results[~pd.isnull(raw_results.discipline)]

    raw_results['distance'] = np.where(pd.isnull(raw_results.distance),
                                       [1000 * extract_distance_from_text(name) if extract_distance_from_text(name)
                                            else None
                                            for name in raw_results.race_name],
                                       raw_results.distance)
    # the 'time' column (which is chip time) is unpopulated for some early races - time2 (gun time) is populated for all
    # when both are populated, they are equal, some time2 is superior
    raw_results['time'] = raw_results.time2
    raw_results['date'] = [gopher_state_extract_date(name) for name in raw_results.event_name]

    return raw_results[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date']]


def itiming_extract_date(date,
                         date_format="%m.%d.%y"):
    # note that many races have a range with two dates - we just take the first
    matches = re.search(r'^([0-9]+\.[0-9]+\.[0-9]+)', date)
    if matches:
        return datetime.strptime(matches.group(1), date_format)

    return None


def infer_gender_from_gender_placement(results):
    """
    :param results: a dataframe with at least columns DivisionPlace, and OverallPlace
    :return: a like dataframe with gender added
    """

    sorted_results = results.sort_values('OverallPlace')

    gender_place_column = 'GenderRank' if np.all(~pd.isnull(results.GenderRank)) else 'DivisionPlace'

    current_man_place = 1
    current_woman_place = 1
    # this is of course not reliable if either:
    # 1. a woman places first
    # 2. women's placements are interleaved with men's placements at all
    gender_inferred_results = pd.DataFrame()
    for index, result in sorted_results.iterrows():
        # sometimes results are missing - probably a DQ
        slack = result.OverallPlace - current_man_place - current_woman_place + 1

        if slack > 1:
            raise ValueError('More than 1 sequential racer was missing - failing for safety instead of slacking')

        if result[gender_place_column] == current_man_place or \
                        result[gender_place_column] == (current_man_place + slack):
            result['gender'] = 'male'
            gender_inferred_results = gender_inferred_results.append(result)
            current_man_place += (1 + slack)
        elif result[gender_place_column] == current_woman_place or \
                        result[gender_place_column] == (current_woman_place + slack):
            result['gender'] = 'female'
            gender_inferred_results = gender_inferred_results.append(result)
            current_woman_place += (1 + slack)
        else:
            raise ValueError('Ran into indexing issues (missing division rank) inferring gender')

    return gender_inferred_results


def infer_gender_from_name(results, placement_distance_threshold=.5):
    """
    very similar to the method using placement - although this is statistical (using name inference & distance
    measurements) vs. placement inference being closer to correct / deterministic
    NOTE, THIS METHOD WILL DROP RESULTS IF GENDER IS NOT CLEAR!
    :param results: a dataframe with Name, GenderRank, and DivisionPlace columns
    :param placement_distance_threshold: threshold on the ratio of absolute distance in gender rank from current gender
    count. e.g. if distnace from current female count is 1 and the current male count is 5, aforementioned ratio is .2
    :return: a similar dataframe with gender attached
    """
    sorted_results = results.sort_values('OverallPlace')

    gender_place_column = 'GenderRank' if np.all(~pd.isnull(results.GenderRank)) else 'DivisionPlace'

    current_man_place = 1
    current_woman_place = 1

    gender_inferred_results = pd.DataFrame()
    for index, result in sorted_results.iterrows():
        first_name, middle_name, last_name = extract_name(result.Name)
        if first_name:
            # note that gender-guesser doesn't do anything fancy - it's just a statistical corpus
            # I'm not sure what its FPRs are, but we'll just trust it :)
            name_gender = GENDER_DETECTOR.get_gender(first_name)
        else:
            # failure to parse name will in all likelihood result in downstream failure, but let it happen there
            name_gender = 'unknown'

        # as the distances increase (or, are close to each other), comparing in absolute terms will increasingly bias
        # towards male determination. ideally, we scale relative to # of males & females
        placement_distance_from_male = abs(result[gender_place_column] - current_man_place)
        placement_distance_from_female = abs(result[gender_place_column] - current_woman_place)
        placement_suggested_gender = 'male' if placement_distance_from_female > placement_distance_from_male \
            else 'female'

        if name_gender == 'male':
            result['gender'] = 'male'
        elif name_gender == 'female':
            result['gender'] = 'female'
        elif name_gender == 'mostly_male':
            if placement_suggested_gender == 'male':
                result['gender'] = 'male'
            else:
                continue
        elif name_gender == 'mostly_female':
            if placement_suggested_gender == 'female':
                result['gender'] = 'female'
            else:
                continue
        # andy for androgynous
        elif name_gender == 'andy' or name_gender == 'unknown':
            if placement_distance_from_male == 0 and placement_distance_from_female == 0:
                continue
            elif placement_distance_from_female == 0:
                result['gender'] = 'female'
            elif placement_distance_from_male == 0:
                result['gender'] = 'male'
            elif placement_distance_from_male / placement_distance_from_female < placement_distance_threshold:
                result['gender'] = 'male'
            elif placement_distance_from_female / placement_distance_from_male < placement_distance_threshold:
                result['gender'] = 'female'
            else:
                # there is no clear resolution - just skip it
                continue
        else:
            raise ValueError('gender-guesser gave something unexpected: ' + name_gender)

        if result.gender == 'male':
            current_man_place += 1
        else:
            current_woman_place += 1

        gender_inferred_results = gender_inferred_results.append(result)

    return gender_inferred_results


# this one is quite hairy
# on top of having a huge number of races compiling small quirks, there is a large issue
# the 80% majority of results don't report gender. we can use the DivisionPlace to
# hopefully derive gender (only works when men + women are buffered), but it's not guaranteed or fun
def get_itiming_results(filename="itiming_results.csv",
                        custom_metadata=pd.DataFrame(
                            [
                                ['The Great Bear Chase', '26 km', np.nan, 'freestyle', None],
                                ['The Great Bear Chase', '52 km', np.nan, 'freestyle', None],
                                ['24th Annual Hayward Lions Pre-Birkie', 'Pre-Birkie', 23 * 1000, 'freestyle', None],
                                ['Great Bear Chase', '50 km', np.nan, 'freestyle', None],
                                ['The Great Bear Chase', '50 km', np.nan, 'freestyle', None],
                                ['Pre-Birkie', 'Pre-Birkie', 23 * 1000, 'freestyle', None],
                                ['US Cross Country Ski Championship', 'Womens 5k Classic', np.nan, None, 'female'],
                                ['US Cross Country Ski Championship', 'Mens 10k Classic', np.nan, None, 'male'],
                                ['Book Across the Bay', 'Nordic Ski Race', 10 * 1000, 'freestyle', None],
                                ['Pre-Birkie', 'Pre-Birkie 42 km XC Ski Race', np.nan, 'freestyle', None],
                                ['Pre-Birkie', 'Pre-Birkie 26 km XC Ski Race', np.nan, 'freestyle', None],
                                ['Pepsi Challenge Cup', 'Pepsi Challenge Cup Classic', 52 * 1000, None, None],
                                ['Pepsi Challenge Cup', 'Laurentian Loppett Classic', 26 * 1000, None, None],
                                ['Pepsi Challenge Cup', 'Pepsi Challenge Cup Freestyle', 52 * 1000, None, None],
                                ['Pepsi Challenge Cup', 'Mini Challenge', 10 * 1000, 'freestyle', None],
                                ['Pepsi Challenge Cup', 'Laurentian Loppett Freestyle', 26 * 1000, None, None],
                                ['Seeley Hills Classic', '5 km High School', np.nan, 'classic', None],
                                ['Seeley Hills Classic', '2.5 km Youth', np.nan, 'classic', None],
                                ['Pepsi Challenge Ski Race', 'Pepsi Challenge Cup Classic', 52 * 1000, None, None],
                                ['Pepsi Challenge Ski Race', 'Laurentian Loppett Classic', 26 * 1000, None, None],
                                ['Pepsi Challenge Ski Race', 'Pepsi Challenge Cup Freestyle', 52 * 1000, None, None],
                                ['Pepsi Challenge Ski Race', 'Mini Challenge', 10 * 1000, 'freestyle', None],
                                ['Pepsi Challenge Ski Race', 'Laurentian Loppett Freestyle', 26 * 1000, None, None],
                                ['Lakeland Loppet', '2 km Beat the Bunny', np.nan, 'freestyle', None],
                                ['SISU Ski Fest', 'Heikki Lunta Half Marathon', 21 * 1000, 'freestyle', None],
                                ['SISU Ski Fest', 'SISU Marathon', 42 * 1000, 'freestyle', None],
                                ['Wolf Tracks Rendezvous', '24 km Ski Half Marathon', np.nan, 'freestyle', None],
                                ['Wolf Tracks Rendezvous', '42 km Ski Marathon', np.nan, 'freestyle', None],
                                # sic
                                ['Wolf Tracks Rendevous', '42 km Ski Marathon', np.nan, 'freestyle', None],
                                ['Pepsi Challenge Cup XC Ski Race', 'Giants Ridge 10k', np.nan, 'freestyle', None],
                                ['Book Across the Bay', 'Nordic Ski', 10 * 1000, 'freestyle', None],
                                ['Pre-Birkie', '42 km', np.nan, 'freestyle', None],
                                ['Pre-Birkie', '26 km', np.nan, 'freestyle', None],
                                ['Pepsi Challenge Cup Cross Country Ski Race', 'Giants Ridge 10k', np.nan, 'freestyle',
                                 None],
                                ['Squirrel Hill Pursuit Ski Race', '2k Beat the Bunny', np.nan, 'freestyle', None],
                                ['Pepsi Challenge Cup XC Ski Race', 'Giants Ridge 10k', np.nan, 'freestyle', None],
                                ['US Cross Country Ski Championship', 'Disabled Sit Ski', 12 * 1000, None, None]
                            ], columns=['event_name', 'Event', 'distance', 'discipline', 'gender'])):
    raw_results = pd.read_csv(RESULTS_DIRECTORY + filename)
    raw_results = raw_results[~pd.isnull(raw_results.Event)]

    # itiming had different html layout for 2 years of this race, custom fix
    raw_results['event_name'] = np.where(raw_results.event_name == 'Division Results',
                                         'Seeley Hills Classic', raw_results.event_name)
    raw_results['event_name'] = np.where(raw_results.event_name == 'Age Group Results',
                                         'Seeley Hills Classic', raw_results.event_name)

    custom_results = raw_results.merge(custom_metadata, how="left", on=['event_name', 'Event'])
    custom_results['date'] = [itiming_extract_date(d) for d in custom_results.event_date]
    custom_results['discipline'] = np.where(pd.isnull(custom_results.discipline),
                                       [extract_discipline_from_race_name(name) for name in custom_results.Event],
                                       custom_results.discipline)
    custom_results = custom_results[~pd.isnull(custom_results.discipline)]
    custom_results['distance'] = np.where(pd.isnull(custom_results.distance),
                                       [extract_distance_from_text(name) * 1000 if extract_distance_from_text(name)
                                        else None
                                        for name in custom_results.Event],
                                       custom_results.distance)

    results_with_gender = pd.DataFrame()
    distinct_races = custom_results[['event_name', 'Event', 'event_date']].drop_duplicates()
    for index, race in distinct_races.iterrows():
        race_results = custom_results[(custom_results.event_name == race.event_name) &
                                      (custom_results.Event == race.Event) &
                                      (custom_results.event_date == race.event_date)]

        if np.all(~pd.isnull(race_results.gender)):
            results_with_gender = results_with_gender.append(race_results)
        else:
            try:
                # this method is "deterministic", in that if the data obeys a set format, it is guaranteed to
                # produce correct results
                # if the data does not obey that format, we have a statistical approach that is less reliable
                gender_inferred_race_results = infer_gender_from_gender_placement(race_results)
            except ValueError:
                gender_inferred_race_results = infer_gender_from_name(race_results)

            results_with_gender = results_with_gender.append(gender_inferred_race_results)

    results_with_gender['name'] = results_with_gender.Name
    results_with_gender['age'] = np.nan
    results_with_gender['time'] = results_with_gender.FinishTime
    results_with_gender['location'] = results_with_gender['City, State']

    print('Gender inference resulted in loss of %d records' % (custom_results.shape[0] - results_with_gender.shape[0],))
    print('Total process removed %d records' % (raw_results.shape[0] - results_with_gender.shape[0],))

    return results_with_gender[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date',
                                'location']]


def chronotrack_extract_date(date_string,
                             date_format='%m.%d.%y'):
    return datetime.strptime(date_string, date_format)


def get_chronotrack_results(filename="chronotrack_results.csv",
                            custom_metadata=pd.DataFrame(
                                [
                                    ['Squirrel Hill Pursuit', '2k Kids Beat the Bunny', 'freestyle', np.nan],
                                    ['Pepsi Challenge Cup XC Ski Race', '10K', 'freestyle', np.nan],
                                    ['Book Across the Bay', 'Ski', 'freestyle', 10],
                                    ['Seeley Hills Classic Ski Race', '5K High School Race', 'classic', np.nan],
                                    ['Seeley Hills Classic Ski Race', '2.5k High School Race', 'classic', np.nan],
                                    ['Seeley Hills Classic', '5K High School Race', 'classic', np.nan],
                                    ['Seeley Hills Classic', '2.5k Middle School Race', 'classic', np.nan],
                                    ['SISU Ski Fest', '5K Junior SISU (ages12-19)', 'freestyle', np.nan],
                                    ['SISU Ski Fest', '3K Junior SISU (ages 6-13)', 'freestyle', np.nan],
                                    ['Pepsi Challenge Cup XC Ski Race', '10 km', 'freestyle', np.nan],
                                    ['SISU Ski Fest', '5k Junior SISU', 'freestyle', np.nan],
                                    ['SISU Ski Fest', '3k Junior SISU', 'freestyle', np.nan]
                                ],
                                columns=['event_name', 'race_name', 'discipline', 'distance'])
                            ):
    raw_results = pd.read_csv(RESULTS_DIRECTORY + filename)
    raw_results = raw_results[raw_results.gender != 'NOT SPECIFIED']
    raw_results['gender'] = np.where(raw_results.gender == 'M', 'male', 'female')

    custom_results = raw_results.merge(custom_metadata, how="left", on=['event_name', 'race_name'])

    custom_results['discipline'] = np.where(pd.isnull(custom_results.discipline),
                                            [extract_discipline_from_race_name(name)
                                             for name in custom_results.race_name],
                                            custom_results.discipline)
    custom_results = custom_results[~pd.isnull(custom_results.discipline)]

    custom_results['distance'] = np.where(pd.isnull(custom_results.distance),
                                          [extract_distance_from_text(name) for name in custom_results.race_name],
                                          custom_results.distance)
    custom_results['distance'] = custom_results.distance * 1000

    custom_results['date'] = [chronotrack_extract_date(d) for d in custom_results.event_date]

    return custom_results[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date', 'location']]


def mtec_extract_date(date_string,
                      date_format='%m/%d/%Y'):
    return datetime.strptime(date_string, date_format)


def get_mtec_vasa_results(filename="Vasaloppet USA_raw.csv"):
    raw_results = pd.read_csv(RESULTS_DIRECTORY + filename)

    raw_results['gender'] = np.where(raw_results.Sex == 'M',
                                     'male',
                                     'female')
    raw_results['distance'] = raw_results.distance_meters
    raw_results['name'] = raw_results.Name
    raw_results['age'] = raw_results.Age
    raw_results['time'] = raw_results.Time
    raw_results['event_name'] = 'Vasaloppet USA'
    raw_results['date'] = [mtec_extract_date(d) for d in raw_results.date]
    raw_results['location'] = raw_results.State

    return raw_results[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date', 'location']]


def get_mtec_mob_results(filename="Marine O'Brien_raw.csv"):
    raw_results = pd.read_csv(RESULTS_DIRECTORY + filename)

    raw_results['distance'] = raw_results.distance_meters
    raw_results['gender'] = ['male' if g == 'M' else 'female' for g in raw_results.Sex]
    raw_results['name'] = raw_results.Name
    raw_results['time'] = raw_results.Time
    raw_results['age'] = raw_results.Age
    raw_results['event_name'] = "Marine O'Brien"
    raw_results['date'] = [mtec_extract_date(d) for d in raw_results.date]
    raw_results['location'] = raw_results.City + ", " + raw_results.State

    return raw_results[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date', 'location']]


def extract_mrr_gender(age_group):
    age_group_lower = age_group.lower()
    if age_group_lower.startswith('m'):
        return 'male'
    elif age_group_lower.startswith('f'):
        return 'female'
    else:
        print('Unexpected age group format: "%s"' % (age_group,))
        return None


def infer_gender(name):
    first_name = extract_name(name)[0]
    if name:
        inferred_gender = GENDER_DETECTOR.get_gender(first_name)
        if inferred_gender == 'male' or inferred_gender == 'mostly_male':
            return 'male'
        elif inferred_gender == 'female' or inferred_gender == 'mostly_female':
            return 'female'

    return None


def extract_age_range(age_group):
    match = re.search(r'[0-9]+(\-|\+| |(&U))([0-9]+)?', age_group)
    if match:
        return match.group()

    return None


def mrr_extract_date(date_string,
                     date_format='%b %d, %Y'):
    return datetime.strptime(date_string, date_format)


def get_mrr_results(filename="mrr_raw.csv"):
    raw_results = pd.read_csv(RESULTS_DIRECTORY + filename)
    raw_results['event_name'] = raw_results.event
    raw_results['discipline'] = [extract_discipline_from_race_name(name) for name in raw_results.race]
    raw_results = raw_results[~pd.isnull(raw_results.discipline)]
    raw_results['distance'] = [extract_distance_from_text(name) * 1000 for name in raw_results.race]
    raw_results['name'] = raw_results.Name
    raw_results['time'] = raw_results.Finish
    raw_results['gender'] = [extract_mrr_gender(ag) for ag in raw_results['AG (Rank)']]
    raw_results['gender'] = np.where(pd.isnull(raw_results.gender),
                                     [infer_gender(name) for name in raw_results.name],
                                     raw_results.gender)
    raw_results = raw_results[~pd.isnull(raw_results.gender)]
    raw_results['age'] = [extract_age_range(ag) for ag in raw_results['AG (Rank)']]
    raw_results['date'] = [mrr_extract_date(d) for d in raw_results['date']]
    raw_results['location'] = raw_results['City/State']

    return raw_results[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date', 'location']]


def extract_orr_gender(division):
    division = str(division).lower()
    if division.startswith('m'):
        return 'male'
    elif division.startswith('f'):
        return 'female'
    else:
        return None


def extract_gender_place(place):
    match = re.search(r'([0-9]+)/', place)
    if match:
        return int(match.group(1))

    return None


def orr_infer_gender_from_gender_placement(race_results):
    # create columns as expected by earlier function
    race_results['OverallPlace'] = race_results.OVERALL
    race_results['GenderRank'] = race_results.gender_place

    return infer_gender_from_gender_placement(race_results)


def orr_extract_date(date_string,
                     date_format='%b %d, %Y'):
    return datetime.strptime(date_string, date_format)


def orr_extract_age_range(division):
    match = re.search(r'([0-9]{2})([0-9]{2})?', str(division))
    if match:
        return "%s-%s" % (match.group(1), match.group(2))

    return None


def get_orr_results(filename="vasa_pre2011.csv",
                    distance_to_discipline=pd.DataFrame(
                        [
                            [13 * 1000, 'freestyle'],
                            [35 * 1000, 'freestyle'],
                            [42 * 1000, 'classic'],
                            [58 * 1000, 'freestyle']
                        ],
                        columns=['distance', 'discipline']
                    )):
    raw_results = pd.read_csv(RESULTS_DIRECTORY + filename)

    raw_results['name'] = raw_results.FN + " " + raw_results.LN
    raw_results = raw_results[(raw_results.name != 'Unknown Skier') & (raw_results.DIVISION != '-') &
                              (raw_results.DIVISION != 'III')]

    raw_results['distance'] = [extract_distance_from_text(name) * 1000 for name in raw_results.race_name]
    raw_results = raw_results.merge(distance_to_discipline, how="inner", on=['distance'])

    raw_results['gender'] = [extract_orr_gender(div) for div in raw_results.DIVISION]

    # apparently in 2006, the 42K and 35K racers did not have gender :(
    raw_results['gender_place'] = [extract_gender_place(place) for place in raw_results.SEXPL]
    results_without_gender = raw_results[pd.isnull(raw_results.gender)]
    races_without_gender = results_without_gender[['event_date', 'race_name']].drop_duplicates()
    for index, race in races_without_gender.iterrows():
        race_results = raw_results[(raw_results.event_date == race.event_date) &
                                   (raw_results.race_name == race.race_name)]
        raw_results = raw_results[(raw_results.event_date != race.event_date) |
                                  (raw_results.race_name != race.race_name)]

        gender_inferred_results = orr_infer_gender_from_gender_placement(race_results)

        raw_results = raw_results.append(gender_inferred_results)

    raw_results['age'] = [orr_extract_age_range(div) for div in raw_results.DIVISION]

    raw_results['time'] = raw_results.TIME
    raw_results['location'] = raw_results.CITY + ', ' + raw_results.STATE
    raw_results['date'] = [orr_extract_date(d) for d in raw_results.event_date]
    raw_results['event_name'] = 'Vasaloppet USA'

    return raw_results[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date']]


##############################
# functions shared across many races
##############################

def enumerate_event_name(event_name):
    event_name_lower = event_name.lower()

    if 'great bear chase' in event_name_lower:
        return 'Great Bear Chase'
    elif 'noquemanon' in event_name_lower:
        return 'Noquemanon Ski Marathon'
    elif 'seeley' in event_name_lower:
        return 'Seeley Hills Classic'
    elif 'pepsi' in event_name_lower:
        return 'Pepsi Challenge'
    elif 'marine' in event_name_lower:
        return "Marine O'Brien"
    elif 'vasaloppet' in event_name_lower:
        return 'Vasaloppet USA'
    elif 'wolf track' in event_name_lower:
        return 'Wolf Track Rendezvous'
    elif 'nordic spirit' in event_name_lower:
        return 'Nordic Spirit'
    elif 'north end' in event_name_lower:
        return 'North End Classic'
    elif 'prebirkie' in event_name_lower or 'pre-birkie' in event_name_lower:
        return 'Pre-Birkie'
    elif 'squirrel' in event_name_lower:
        return 'Squirrel Hill Ski Race'
    elif 'sisu' in event_name_lower:
        return 'SISU Ski Fest'
    elif 'ashwabay' in event_name_lower:
        return 'Mt. Ashwabay Summit Ski Race'
    elif 'boulder lake' in event_name_lower:
        return 'Boulder Lake Ski Race'
    elif 'lakeland' in event_name_lower:
        return 'Lakeland Loppet'
    elif 'badger' in event_name_lower:
        return 'Badget State Games'
    elif 'book across' in event_name_lower:
        return 'Book Across the Bay'
    elif 'blue hills' in event_name_lower:
        return 'Blue Hills Ascent'
    elif 'pre-loppet' in event_name_lower:
        return 'Pre-Loppet'
    elif 'pursuit champs' in event_name_lower:
        return 'MN Pursuit Champs'
    elif ('three rivers' in event_name_lower) or ('ski rennet' in event_name_lower):
        return 'Ski Rennet'
    elif 'big island' in event_name_lower:
        return 'Big Island and Back'
    elif ('us' in event_name_lower) and ('championship' in event_name_lower):
        return 'US Cross Country Ski Championship'
    elif 'double pole derby' in event_name_lower:
        return 'Double Pole Derby'

    return None


def attach_placements(results):
    time_ordered_results = results.sort_values('time_parsed')

    time_ordered_results['gender_place'] = time_ordered_results\
        .groupby(['date', 'event_name_enumeration', 'distance', 'discipline', 'gender'])\
        .cumcount() + 1
    time_ordered_results['overall_place'] = time_ordered_results\
        .groupby(['date', 'event_name_enumeration', 'distance', 'discipline'])\
        .cumcount() + 1

    return time_ordered_results


##############################
# start control flow
##############################

results = pd.concat([
    get_gopher_state_results(),
    get_itiming_results(),
    get_chronotrack_results(),
    get_mtec_vasa_results(),
    get_mtec_mob_results(),
    get_mrr_results(),
    get_orr_results(),
])
# results.to_csv('~/all_results_parsed.csv')
# results = pd.read_csv('~/all_results_parsed.csv')

results = results[~pd.isnull(results.time)]
results['time_parsed'] = [parse_time_millis(t) for t in results.time]
# note, this knocks off a handful of labelled DNFs & DQs
results = results[~pd.isnull(results.time_parsed)]

results['event_name_enumeration'] = [enumerate_event_name(name) for name in results.event_name]
results['date'] = pd.to_datetime(results.date)
results['distance'] = pd.to_numeric(results.distance / 1000)

results = attach_placements(results)

con = None
try:
    con = get_connection()
    cursor = con.cursor()

    events_for_insert = results[['event_name_enumeration']].drop_duplicates()
    events_for_insert.columns = ['name']
    events_inserted = rrc.insert_and_get_events(cursor, events_for_insert)
    events_inserted.columns = ['event_id', 'event_name_enumeration']

    results_joined = results.merge(events_inserted, how='inner', on=['event_name_enumeration'])

    event_occurrences_for_insert = results_joined[['event_id', 'date']].drop_duplicates()
    event_occurrences_inserted = rrc.insert_and_get_event_occurrences(cursor, event_occurrences_for_insert)
    event_occurrences_inserted.columns = ['event_occurrence_id', 'event_id', 'date']
    event_occurrences_inserted['date'] = pd.to_datetime(event_occurrences_inserted.date)

    results_joined = results_joined.merge(event_occurrences_inserted, how="inner", on=['event_id', 'date'])

    races_for_insert = results_joined[['event_occurrence_id', 'distance', 'discipline']].drop_duplicates()
    races_inserted = rrc.insert_and_get_races(cursor, races_for_insert)
    races_inserted.columns = ['race_id', 'event_occurrence_id', 'discipline', 'distance']
    races_inserted['distance'] = pd.to_numeric(races_inserted.distance)

    results_joined = results_joined.merge(races_inserted, how="inner",
                                                 on=['event_occurrence_id', 'discipline', 'distance'])
    race_records_for_insert = [RaceRecord(rr['name'], str(rr.age), rr.gender, rr.time, rr.overall_place,
                                          rr.gender_place, rr.race_id, RacerSource.RecordIngestion)
                               for ix, rr in results_joined.iterrows()]
    race_records_for_insert_valid = [rr for rr in race_records_for_insert if rr.get_first_name() and rr.get_last_name()]

    racer_matcher = RacerMatcher(race_records_for_insert_valid)

    matched_race_records = racer_matcher.merge_to_identities()

    con.rollback()
    con.close()

    con.commit()
    cursor.close()
finally:
    if con is not None:
        con.rollback()
        con.close()