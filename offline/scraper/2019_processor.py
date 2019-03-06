import pandas as pd
import numpy as np

from db import get_connection

import scraper.race_record_committer as rrc
from scraper.racer_identity import RaceRecord
from scraper.racer_identity import RacerSource
from scraper.racer_identity import parse_time_millis
from scraper.result_parsing_utils import extract_discipline_from_race_name, attach_placements
from scraper.birkie_processor import process_2016_on_results
import scraper.host_scrapers.mtec_scraper as mts
import scraper.host_scrapers.myraceresults_scraper as mrrs

import scraper.host_scrapers.gopher_state_scraper as gss
import scraper.host_scrapers.myraceresults_scraper as mrrs
import scraper.host_scrapers.mtec_scraper as mts


DEFAULT_DATA_DIRECTORY = '/Users/kholub/birkielo/offline/data'

def get_event_occurrences():
    pass
    return {
        "Ski Rennet": "2019-01-19",
        "Noquemanon Ski Marathon": "2019-01-26",
        "SISU Ski Fest": "2019-01-12",
        "Vasaloppet USA": "2019-02-09"
    }


def get_birkie_results():
    results = pd.read_csv(DEFAULT_DATA_DIRECTORY + '/birkie2019.csv')
    results = process_2016_on_results(results)
    results['event_name'] = 'American Birkebeiner'
    results['date'] = '2019-02-23'
    results = results.rename({'City, State, Nation': 'location', 'Finish  Time': 'time',
                              'Overall Place': 'overall_place', 'Gender Place': 'gender_place',
                              'Name': 'name'}, axis='columns')

    return results


def get_gopher_state_results(event_names_to_distance = pd.DataFrame({'event_name': ['Turtle River Pursuit', 'Big Island and Back'],
                                           'distance': [11, 7.5]})):
    events_2019 = [e for e in gss.get_events() if '2019' in e[1]]
    races_2019 = gss.get_races_from_events(events_2019)
    results_2019 = gss.get_results_from_races(races_2019)
    # remove bike and team results
    results_2019 = results_2019[~results_2019.race_name.str.contains('Bike') & ~results_2019.race_name.str.contains('Tm')]
    results_2019['date'] = [gss.extract_date_from_race_name(n) for n in results_2019.event_name]
    results_2019['discipline'] = [extract_discipline_from_race_name(n) for n in results_2019.race_name]
    results_2019['event_name'] = [gss.extract_event(n) for n in results_2019.event_name]
    results_2019['name'] = results_2019.first_name + " " + results_2019.last_name
    results_2019['gender'] = np.where(results_2019.gender == 'M', 'male', 'female')
    results_2019['duration'] = [parse_time_millis(t) for t in results_2019.time]
    results_2019['location'] = None

    results = attach_placements(results_2019).merge(event_names_to_distance, how="inner", on=['event_name'])

    return results

def get_mtec_results(events=pd.DataFrame({
    "event_name": ['City of Lakes Loppet', 'Nordic Spirit', 'Mt. Ashwabay Summit Ski Race', 'Pre-Loppet'],
    "mtec_event_id": [2844, 2843, 2849, 2823],
    "discipline": [None, 'freestyle', 'freestyle', None]})):
    mtec_results = []
    for index, event in events.iterrows():
        all_races = mts.expand_event_to_races([event.mtec_event_id])
        races_with_metadata = mts.attach_race_metadata_and_filter_structured(all_races, event.discipline)
        results = mts.get_race_results(races_with_metadata)
        results = results.rename({'Time': 'time', 'Age': 'age', 'Name': 'name'}, axis='columns')
        results['distance'] = results['distance_meters'] / 1000.0
        if 'City' in results.columns and 'State' in results.columns:
            results['location'] = results.City + ', ' + results.State
        else:
            results['location'] = None
        results['gender'] = np.where(results.Sex == 'M', 'male', 'female')
        results['overall_place'] = [mts.extract_placement(p) for p in results.Overall]
        results['gender_place'] = [mts.extract_placement(p) for p in results['SexPl']]
        results['event_name'] = event.event_name
        mtec_results.append(results)

    return pd.concat(mtec_results)


def get_myraceresults_results(events=pd.DataFrame({
    "event_name": ['Vasaloppet USA', 'Noquemanon Ski Marathon', 'Pepsi Challenge'],
    "event_url": ['https://my3.raceresult.com/117060/', 'https://my5.raceresult.com/115565/',
                  'https://my2.raceresult.com/118903/']})):
    results = []
    for index, event in events.iterrows():
        races = mrrs.get_mrr_races(event.event_url)
        for contest_number, list_name, race_name, event_id, event_key in races:
            results = mrrs.get_mrr_results(event_id, event_key, list_name, contest_number)
            results_df = pd.DataFrame(results, columns = ['name', 'location', 'age_group', 'time'])
            results_df['gender'] = np.where(results_df.age_group.str.startswith('M'), 'male', 'female')


            results.append(results_df)

    return pd.concat(results)

def get_chronotrack_results(events=pd.DataFrame({})):
    pass


if __name__ == "__main__":
    all_results = pd.concat([
        get_birkie_results(),
        get_gopher_state_results(),
        get_mtec_results(),
        get_myraceresults_results(),
        get_chronotrack_results()
    ])

    con = None
    try:
        con = get_connection()
        cursor = con.cursor()

        rrc.insert_flattened_results(cursor, all_results)
        # I ran sanity/janitor.py right after this - they can be reasonably run independently,
        # but they would ideally be the same txn
        con.commit()
        cursor.close()
    finally:
        if con is not None:
            con.rollback()
            con.close()
