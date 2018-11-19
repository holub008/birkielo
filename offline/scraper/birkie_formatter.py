import pandas as pd
import numpy as np

import race_record_processor as rrp
from RacerIdentity import RaceRecord
from RacerIdentity import RacerSource
from RacerMatcher import RacerMatcher

# TODO it seems like data is missing for 2007
DEFAULT_DATA_DIRECTORY = '/Users/kholub/birkielo/offline/data'


def handle_messups_2007(df):
    # these are all missing - not a scraping issue. hypothesis is DQs
    df_clean = pd.concat([df, pd.DataFrame({
        "OverallPlace": [118, 1264],
        "GenderPlace": [11, 141],
        "Name": ["Mystery Racer", "Mystery Racer"],
        "Finish Time": ["03:31:29.8", "03:24:16.7"],
        "Event": ["2008 50.2k Birkebeiner Classic", "2009 50k Birkebeiner Freestyle"]
    })], sort=False)

    return df_clean


def process_2007_to_2015_results(df):
    all_event_names = set(df.Event)
    for event_name in all_event_names:
        event_results = df[df.Event == event_name].sort_values('OverallPlace')
        female_indices = []
        female_rank = 1
        # algo is simple - iterate over all results, if gender rank equals the next female rank, it's female
        # of course this is breakable, but better than hitting birkie site with 100K+ requests
        # iterating from 1 onwards, assuming that finisher 1 is male
        for index, row in event_results[1:].iterrows():  # note we are skipping 1, which we assume to be a male result
            if row.GenderPlace == female_rank:
                female_indices.append(index)
                female_rank += 1
        df.loc[female_indices, 'gender'] = 'female'

    df = df.assign(gender=['male' if pd.isnull(x) else x for x in df.gender])

    return df


def process_2016_on_results(df):
    # since the age group isn't reported for cash winners, we just assume top 6 NaNs are men
    is_male = np.logical_or(np.logical_and(pd.isnull(df['Ag Grp  Place']), df['Overall Place'] < 7),
                            df['Ag Grp  Place'].str.contains('M'))
    df = df.assign(gender=['male' if (np.logical_and(x, not pd.isnull(x))) else 'female' for x in is_male])

    return df


def process_2006_results(df):
    df = df.assign(gender=['female' if (x.endswith('Women')) else 'male' for x in df.Event])

    return df


# I just grabbed these online by hand
def get_birkie_occurences(event_id):
    return pd.DataFrame(dict(event_id = [event_id for x in range(12)],
                             date=['2018-02-24', '2016-02-20', '2015-02-21', '2014-02-22', '2013-02-23',
                                   '2012-02-25', '2011-02-26', '2010-02-27', '2009-02-21', '2008-02-23', '2007-02-24',
                                   '2006-02-25']))


def attach_race_details_2006(cursor, processed_2006, event_occurrences):
    event_occurrences['year'] = [x.year for x in event_occurrences.date]
    event_occurrence = event_occurrences[event_occurrences.year == 2006]
    event_occurrence_id = event_occurrence.event_occurrence_id.values[0]
    # sic
    processed_2006['discipline'] = processed_2006.Dvision.str.lower()

    conditions = [
        (processed_2006.Event.str.lower().str.contains('birkebeiner')),
        (processed_2006.Event.str.lower().str.contains('kortelopet'))]
    condition_distances = [50.0, 30.0]
    processed_2006['distance'] = np.select(conditions, condition_distances, default=-1)

    unique_races = processed_2006[['distance', 'discipline']].drop_duplicates()
    unique_races['event_occurrence_id'] = event_occurrence_id

    inserted_races = rrp.insert_and_get_races(cursor, unique_races)
    inserted_races['distance'] = pd.to_numeric(inserted_races.distance)

    total_joined_results = processed_2006.merge(inserted_races, on=['distance', 'discipline'], how='inner')
    total_joined_results['race_id'] = total_joined_results.id
    total_joined_results = total_joined_results.drop('id', 1)

    return total_joined_results


def attach_race_details_2007(cursor, processed_2007, event_occurrences):
    event_occurrences['year'] = [x.year for x in event_occurrences.date]
    processed_2007['year'] = pd.to_numeric(processed_2007.Event.str.extract("^([0-9]+)")[0], errors="coerce")
    processed_2007['distance'] = pd.to_numeric(processed_2007.Event.str.extract(' ([0-9\\.]+)k')[0], errors="coerce")
    processed_2007['discipline'] = processed_2007.Event.str.extract(' ([a-zA-Z]+)$')[0].str.lower()

    # note that haakon events don't have a discipline, so are in fact "freestyle"
    # this is super clunky notation compared to R tidyverse, but I couldn't find a better way :/
    processed_2007['discipline'] = np.where(processed_2007['discipline'] == 'haakon', 'freestyle',
                                            processed_2007['discipline'])
    processed_2007_joined = processed_2007.merge(event_occurrences, on='year', how='inner')

    unique_races = processed_2007_joined[['distance', 'discipline', 'event_occurrence_id']].drop_duplicates()

    inserted_races = rrp.insert_and_get_races(cursor, unique_races)
    inserted_races['distance'] = pd.to_numeric(inserted_races.distance)

    total_joined_results = processed_2007_joined.merge(inserted_races,
                                                       on=['distance', 'discipline', 'event_occurrence_id'])
    total_joined_results['race_id'] = total_joined_results.id
    total_joined_results = total_joined_results.drop('id', 1)

    return total_joined_results


def attach_race_details_2016(cursor, processed_results, event_occurrences):
    processed_results['distance'] = pd.to_numeric(processed_results.Event.str.extract("^([0-9]+)k")[0], errors="coerce")
    processed_results['discipline'] = processed_results.Event.str.extract(' ([a-zA-Z]+)$')[0].str.lower()

    conditions = [
        (processed_results.discipline == 'skate'),
        # haakon doesn't have a discipline and is therefore freestyle
        (processed_results.discipline == 'haakon'),
        (processed_results.discipline == 'classic')]
    condition_disciplines = ['freestyle', 'freestyle', 'classic']
    processed_results['discipline'] = np.select(conditions, condition_disciplines, default="to_fail")

    processed_results_joined = processed_results.merge(event_occurrences, on='year', how='inner')

    unique_races = processed_results_joined[['distance', 'discipline', 'event_occurrence_id']].drop_duplicates()

    inserted_races = rrp.insert_and_get_races(cursor, unique_races)
    inserted_races['distance'] = pd.to_numeric(inserted_races.distance)

    total_joined_results = processed_results_joined.merge(inserted_races,
                                                          on=['distance', 'discipline', 'event_occurrence_id'])
    total_joined_results['race_id'] = total_joined_results.id
    total_joined_results = total_joined_results.drop('id', 1)

    return total_joined_results


def create_race_records(processed_2006, processed_2007, processed_2016_on):
    racer_records = []
    for index, row in processed_2006.iterrows():
        race_record = RaceRecord(row.Name, None, row.gender, row['Finish  Time'],
                                 row['Overall Place'], row['Gender  Overall Place'], row.race_id,
                                 RacerSource.RecordIngestion)
        racer_records.append(race_record)

    for index, row in processed_2007.iterrows():
        race_record = RaceRecord(row.Name, None, row.gender, row['Finish Time'],
                                 row.OverallPlace, row.GenderPlace, row.race_id,
                                 RacerSource.RecordIngestion)
        racer_records.append(race_record)

    for index, row in processed_2016_on.iterrows():
        ag_grp_place = row['Ag Grp  Place'] if (not pd.isna(row['Ag Grp  Place'])) else None
        race_record = RaceRecord(row.Name, ag_grp_place, row.gender, row['Finish  Time'],
                                 row['Overall Place'], row['Gender Place'], row.race_id,
                                 RacerSource.RecordIngestion)
        racer_records.append(race_record)

    return [rr for rr in racer_records if not rr.get_first_name() is None]

####################################
# start control flow
####################################

clean_2007 = handle_messups_2007(pd.read_csv(DEFAULT_DATA_DIRECTORY + '/birkie2007to2015.csv'))
processed_2007 = process_2007_to_2015_results(clean_2007)
# TODO, not suprisingly, prince haakon 2012, 2014 are hosed because men and women overlap from the start
# these races aren't competitive, so low priority for now

results_2016 = pd.read_csv(DEFAULT_DATA_DIRECTORY + '/birkie2016.csv')
results_2016['year'] = 2016
results_2018 = pd.read_csv(DEFAULT_DATA_DIRECTORY + '/birkie2018.csv')
results_2018['year'] = 2018
results_2016_on = pd.concat([results_2016, results_2018])
processed_2016_on = process_2016_on_results(results_2016_on)

results_2006 = pd.read_csv(DEFAULT_DATA_DIRECTORY + '/birkie2006.csv')
processed_2006 = process_2006_results(results_2006)

con = None
try:
    con = rrp.get_db_connection()
    cursor = con.cursor()

    events = rrp.insert_and_get_events(cursor, pd.DataFrame({"name": ['American Birkebeiner']}))
    event_id = events.id[0]

    event_occurrences = get_birkie_occurences(event_id)
    event_occurrences = rrp.insert_and_get_event_occurrences(cursor, event_occurrences)
    event_occurrences['event_occurrence_id'] = event_occurrences.id
    event_occurrences = event_occurrences.drop('id', 1)

    processed_2006 = attach_race_details_2006(cursor, processed_2006, event_occurrences)
    processed_2007 = attach_race_details_2007(cursor, processed_2007, event_occurrences)
    processed_2016_on = attach_race_details_2016(cursor, processed_2016_on, event_occurrences)

    race_records = create_race_records(processed_2006, processed_2007, processed_2016_on)

    matcher = RacerMatcher(race_records)
    racers_to_record_indices = matcher.merge_to_identities()
    rrp.insert_racers(cursor, racers_to_record_indices, race_records)

    con.commit()
    cursor.close()
finally:
    if con is not None:
        con.rollback()
        con.close()
