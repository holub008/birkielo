import pandas as pd
import numpy as np

from db import get_connection

import scraper.race_record_committer as rrc
from scraper.racer_identity import RaceRecord
from scraper.racer_identity import RacerSource
from scraper.racer_matcher import RacerMatcher

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


def get_gopher_state_results():
    events_2019 = [e for e in gss.get_events() if '2019' in e[1]]
    races_2019 = gss.get_races_from_events(events_2019)
    results_2019 = gss.get_results_from_races(races_2019)

def get_myraceresults_results():
    event

#######################
# start control flow
#######################

event_occurrences = get_event_occurrences()

con = None
try:
    con = get_connection()
    cursor = con.cursor()

    events = rrc.insert_and_get_events(cursor, pd.DataFrame({"name": ['American Birkebeiner']}))

    event_occurrences = get_event_occurrences(events)
    event_occurrences = rrc.insert_and_get_event_occurrences(cursor, event_occurrences)
    event_occurrences['event_occurrence_id'] = event_occurrences.id
    event_occurrences = event_occurrences.drop('id', 1)

    race_records = create_race_records(processed_2006, processed_2007, processed_2016_on)

    matcher = RacerMatcher(race_records)
    racers_to_record_indices = matcher.merge_to_identities()
    rrc.insert_racers(cursor, racers_to_record_indices, race_records)

    con.commit()
    cursor.close()
finally:
    if con is not None:
        con.rollback()
        con.close()
