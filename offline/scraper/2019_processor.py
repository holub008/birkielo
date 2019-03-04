import pandas as pd
import numpy as np

from db import get_connection

import scraper.race_record_committer as rrc
from scraper.racer_identity import RaceRecord
from scraper.racer_identity import RacerSource
from scraper.racer_identity import parse_time_millis
from scraper.result_parsing_utils import extract_discipline_from_race_name, attach_placements

import scraper.host_scrapers.gopher_state_scraper as gss
import scraper.host_scrapers.myraceresults_scraper as mrrs
import scraper.host_scrapers.mtec_scraper as mts


DEFAULT_DATA_DIRECTORY = '/Users/kholub/birkielo/offline/data'

def process_birkie_results(df):
    # since the age group isn't reported for cash winners, we just assume top 6 NaNs are men
    is_male = np.logical_or(np.logical_and(pd.isnull(df['Ag Grp  Place']), df['Overall Place'] < 7),
                            df['Ag Grp  Place'].str.contains('M'))
    df = df.assign(gender=['male' if (np.logical_and(x, not pd.isnull(x))) else 'female' for x in is_male])

    return df


def attach_birkie_race_details(processed_results):
    processed_results['distance'] = pd.to_numeric(processed_results.Event.str.extract("^([0-9]+)k")[0], errors="coerce")
    processed_results['discipline'] = processed_results.Event.str.extract(' ([a-zA-Z]+)$')[0].str.lower()

    conditions = [
        (processed_results.discipline == 'skate'),
        # haakon doesn't have a discipline and is therefore freestyle
        (processed_results.discipline == 'haakon'),
        (processed_results.discipline == 'classic')]
    condition_disciplines = ['freestyle', 'freestyle', 'classic']
    processed_results['discipline'] = np.select(conditions, condition_disciplines, default="to_fail")

    return processed_results


def create_birkie_race_results(results):
    racer_records = pd.DataFrame()
    for index, row in results.iterrows():
        ag_grp_place = row['Ag Grp  Place'] if (not pd.isna(row['Ag Grp  Place'])) else None
        race_record = RaceRecord(row.Name, ag_grp_place, row.gender, row['Finish  Time'],
                                 row['Overall Place'], row['Gender Place'], row.race_id,
                                 RacerSource.RecordIngestion)
        racer_records.append(race_record)

    return [rr for rr in racer_records if not rr.get_first_name() is None]


def get_event_occurrences():
    return {
        "American Birkebeiner": "2019-02-23",
        "City of Lakes Loppet": "2019-02-02",
        "Ski Rennet": "2019-01-19",
        "Noquemanon Ski Marathon": "2019-01-26",
        "SISU Ski Fest": "2019-01-12",
        "Pre-Loppet": "2019-01-06",
        "Big Island and Back": "2019-02-09",
        "Nordic Spirit": "2019-01-26",
        "Vasaloppet USA": "2019-02-09"
    }


def get_birkie_results():
    results = pd.read_csv(DEFAULT_DATA_DIRECTORY + '/birkie2019.csv')
    results = process_birkie_results(results)
    results = attach_birkie_race_details(results)
    results['event_name'] = 'American Birkebeiner'

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

def get_myraceresults_results():
    pass


if __name__ == "__main__":
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
