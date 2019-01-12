##########################################################
## this file ingests data scraped in incremental_scrapers/
##########################################################

import re
from datetime import datetime

import pandas as pd
import numpy as np
from gender_guesser import detector

import race_record_committer as rrc
from db import get_connection
from racer_identity import RaceRecord
from racer_identity import RacerSource
from racer_matcher import RacerMatcher
from racer_identity import extract_name

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
    elif 'pursuit' in race_name_lower:
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
                              date_format = "%m/%d/%Y"):
    matches = re.search(r'\(([0-9]+/[0-9]+/[0-9]+)\)$', race_name)
    if matches:
        return datetime.strptime(matches.group(1), date_format)

    return None


def get_gopher_state_results(filename="gopher_state.csv",
                             custom_distances = pd.DataFrame(
                                                    [
                                                        ['Big Island and Back (2/3/2018)', 'Adult Skate', 10 * 1000],
                                                        ['Big Island and Back (2/3/2018)', 'Adult Classic', 10 * 1000],
                                                        ['Minnesota Pursuit Champs (2/28/2016)', 'Individual Pursuit', 10 * 1000],
                                                        ['Big Island and Back (1/30/2016)', 'Adult Skate', 10 * 1000],
                                                        ['Big Island and Back (1/30/2016)', 'Adult Classic', 10 * 1000],
                                                        ['MN Pursuit Champs (3/1/2015)', 'Indiv Pursuit', 10 * 1000]
                                                    ], columns = ['event_name', 'race_name', 'distance']),
                             ignore_races = pd.DataFrame(
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
    raw_results['discipline'] = [extract_discipline_from_race_name(name) for name in raw_results.race_name]
    # there's a bunch of snow shoe, team, and running events mixed in - filter them out if no discernible discipline
    raw_results = raw_results[~pd.isnull(raw_results.discipline)]

    raw_results['distance'] = np.where(pd.isnull(raw_results.distance),
                                       [1000 * extract_distance_from_text(name) if extract_distance_from_text(name)
                                            else None
                                            for name in raw_results.race_name],
                                       raw_results.distance)
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
    :param results: a dataframe with at least columns Name, DivisionPlace, and OverallPlace
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
            # first_name = extract_name(result.Name)[0]
            raise ValueError('Ran into indexing issues (missing division rank) inferring gender')

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
                                ['Pepsi Challenge Cup Cross Country Ski Race', 'Giants Ridge 10k', np.nan, 'freestyle', None],
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
                                       [extract_distance_from_text(name) for name in custom_results.Event],
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
                gender_inferred_race_results = infer_gender_from_gender_placement(race_results)
            except Exception as e:
                print(race)
                print(e)
            # TODO verify genders using the gender-guesser package
            results_with_gender = results_with_gender.append(gender_inferred_race_results)

    results_with_gender['name'] = results_with_gender.Name
    results_with_gender['age'] = np.nan
    results_with_gender['time'] = results_with_gender.FinishTime
    results_with_gender['date'] = results_with_gender.event_date

    return results_with_gender[['name', 'gender', 'age', 'discipline', 'distance', 'time', 'event_name', 'date']]


def get_chronotrack_results(filename="chronotrack_results.csv")
    pass


def get_mtec_vasa_results(filename="Vasaloppet USA_raw.csv"):
    pass


def get_mtec_mob_results(filename="Marine O'Brien_raw.csv"):
    pass


def get_mrr_results(filename="mrr_raw.csv"):
    pass


def get_orr_results(filename="vasa_pre2011.csv"):
    pass



##############################
## start control flow
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


