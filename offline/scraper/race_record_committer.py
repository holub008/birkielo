import pandas as pd
import psycopg2.sql as pgs
import psycopg2.extras as pge

from scraper.racer_identity import RaceRecord
from scraper.racer_identity import RacerSource
from scraper.racer_matcher import RacerMatcher

_RACER_INSERT_QUERY = """
    INSERT INTO racer (first_name, middle_name, last_name, gender, age_lower, age_upper)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
"""

_RACER_RESULT_INSERT_QUERY = """
    INSERT INTO race_result
      (racer_id, race_id, overall_place, gender_place, duration, gender, age_lower, age_upper, name)
    VALUES %s
"""


# common utilities for processing (e.g. matching racers) & inserting (to db) event, race, and results
# note that we prefer psycopg2 to standard pandas to_sql because we want the generated ids of inserted rows
# (RETURNING clause). However, the order of RETURNING is not strictly guaranteed by postgres


def _insert_and_get_generic(cursor, df, table_name, required_columns,
                            page_size=10000):
    if not set(required_columns).issubset(df.columns):
        raise ValueError('Required column names are missing in input events!')

    if df.shape[0] > page_size:
        raise ValueError('Attempting to insert more records than page size - would result in missing returned values')

    values_for_insert = df[required_columns].values.tolist()
    # note we can't "safely" insert the table name here. still, we expect all table names to come internally, so string
    # concat is OK once https://github.com/psycopg/psycopg2/issues/794 is resolved, solution looks like:
    # query_value_format = pgs.SQL("INSERT INTO {} ({}) VALUES %s RETURNING *").format(pgs.Identifier(table_name),
    # pgs.SQL(', ').join(map(sql.Identifier, required_columns))
    query_value_format = "INSERT INTO " + table_name + ' (' + ','.join(required_columns) + ') VALUES %s RETURNING *'
    pge.execute_values(cursor, query_value_format, values_for_insert, page_size=page_size)
    result_set = cursor.fetchall()
    result_df = pd.DataFrame(result_set)
    # note, we assume that anything worth getting is returning an "id" column
    result_df.columns = ["id"] + required_columns
    return result_df


def insert_and_get_events(cursor, events):
    """
    insert event and get it in the same transaction.

    :param cursor: a writable cursor object. this function makes no mutation to it besides the insert and select
    :param events: a dataframe representing events. required columns: "name"
    :return: a dataframe representing the db backed events
    """
    cursor.execute("SELECT id, name from event")
    all_existing_events = pd.DataFrame(cursor.fetchall(), columns=['id', 'name'])
    joined_events = events.merge(all_existing_events, how="left", on='name')
    events_for_insert = joined_events[pd.isnull(joined_events.id)]
    existing_events = joined_events[~pd.isnull(joined_events.id)]

    if events_for_insert.shape[0] > 0:
        inserted_events = _insert_and_get_generic(cursor, events_for_insert, "event", ['name'])
        return pd.concat([inserted_events, existing_events])
    else:
        return existing_events


def insert_and_get_event_occurrences(cursor, event_occurrences):
    """
    insert an event occurrence and get it in the same transaction.

    :param cursor:  a writable connection object. this function makes no mutation to it besides the insert and select
    :param event_occurrences: a dataframe representing event occurrences. required columns: "event_id", "date"
    :return: a dataframe representing the inserted event occurrences
    """
    return _insert_and_get_generic(cursor, event_occurrences, "event_occurrence", ['event_id', 'date'])


def insert_and_get_races(cursor, races):
    """
    insert an event occurrence and get it in the same transaction.

    :param cursor:  a writable connection object. this function makes no mutation to it besides the insert and select
    :param races: a dataframe representing races. required columns: "event_occurrence_id", "discipline", "distance"
    :return: a dataframe representing the inserted races
    """
    return _insert_and_get_generic(cursor, races, "race", ['event_occurrence_id', 'discipline', 'distance'])


def insert_racers(cursor, racers_to_race_record_indices, race_results,
                  racers_per_result_batch=100):
    """
    note that this function does no batching in the name of correctness (postgres does not guarantee the order
    of returning statements), and is slow due to network overhead
    :param cursor: a writable connection object. this function makes no mutation to it besides the insert and select
    :param racers_to_race_record_indices: a list of tuples with racer identities in first position. will be mutated
    :param race_results: a list of raw race results, indexed by the prior argument
    :param racers_per_result_batch: for inserting race results in bulk - the number of racers to group in a batch. note
    that any new racers are inserted individually (not batched), so workloads with a large number of new racers aren't
    much optimized with this parameter
    :return: void
    """

    results_batch = []
    for ix, racer_to_ix in enumerate(racers_to_race_record_indices):
        if ix % racers_per_result_batch == 0 and ix != 0:
            pge.execute_values(cursor, _RACER_RESULT_INSERT_QUERY, results_batch)
            results_batch = []
            print("Inserted %s of %s racers" % (ix, len(racers_to_race_record_indices)))

        racer_identity = racer_to_ix[0]
        race_results_for_racer = [race_results[ix] for ix in racer_to_ix[1]]
        racer_identity_id = racer_identity.get_racer_id()
        if not racer_identity_id:
            cursor.execute(_RACER_INSERT_QUERY,
                           (racer_identity.get_first_name(), racer_identity.get_middle_name(),
                            racer_identity.get_last_name(), racer_identity.get_gender().value,
                            racer_identity.get_age_lower(), racer_identity.get_age_upper()))
            result_set = cursor.fetchall()
            racer_identity_id = result_set[0][0]
        race_result_name = "%s %s %s" % (racer_identity.get_first_name(),
                                         racer_identity.get_middle_name() if racer_identity.get_middle_name() else "",
                                         racer_identity.get_last_name())
        racer_results = [(racer_identity_id, rr.get_race_id(), rr.get_overall_place(), rr.get_gender_place(),
                              rr.get_duration(), rr.get_gender().value, rr.get_age_lower(), rr.get_age_upper(),
                              race_result_name)
                             for rr in race_results_for_racer]
        results_batch += racer_results

    if len(results_batch):
        pge.execute_values(cursor, _RACER_RESULT_INSERT_QUERY, results_batch)


def insert_flattened_results(cursor, results,
                             racers_per_result_batch=100):
    """
    :param cursor: a writable connection object. this function makes no mutation to it besides inserts and selects
    :param results: a dataframe with columns: ['age', 'date', 'discipline', 'distance', 'event_name', 'gender', 'gender_place', 'location', 'name', 'overall_place', 'time']
    :param racers_per_result_batch: as passed to insert_racers
    :return: void
    """
    events = results.drop_duplicates('event_name')[['event_name']]
    events = events.rename({'event_name': 'name'}, axis='columns')
    events_inserted = insert_and_get_events(cursor, events)
    events_inserted = events_inserted.rename({'name': 'event_name', 'id': 'event_id'}, axis='columns')

    results_joined = results.merge(events_inserted, how='inner', on=['event_name'])

    event_occurrences_for_insert = results_joined[['event_id', 'date']].drop_duplicates()
    event_occurrences_inserted = insert_and_get_event_occurrences(cursor, event_occurrences_for_insert)
    event_occurrences_inserted =  event_occurrences_inserted.rename({'id': 'event_occurrence_id'}, axis='columns')
    event_occurrences_inserted['date'] = pd.to_datetime(event_occurrences_inserted.date)

    results_joined = results_joined.merge(event_occurrences_inserted, how="inner", on=['event_id', 'date'])

    races_for_insert = results_joined[['event_occurrence_id', 'distance', 'discipline']].drop_duplicates()
    races_inserted = insert_and_get_races(cursor, races_for_insert)
    races_inserted = races_inserted.rename({'id': 'race_id'}, axis='columns')
    races_inserted['distance'] = pd.to_numeric(races_inserted.distance)

    results_joined = results_joined.merge(races_inserted, how="inner",
                                          on=['event_occurrence_id', 'discipline', 'distance'])
    race_records_for_insert = [RaceRecord(rr['name'], str(rr.age), rr.gender, rr.time, rr.overall_place,
                                          rr.gender_place, rr.race_id, RacerSource.RecordIngestion)
                               for ix, rr in results_joined.iterrows()]
    race_records_for_insert_valid = [rr for rr in race_records_for_insert if
                                     rr.get_first_name() and rr.get_last_name()]

    racer_matcher = RacerMatcher(race_records_for_insert_valid)

    matched_race_records = racer_matcher.merge_to_identities()

    insert_racers(cursor, matched_race_records, race_records_for_insert_valid, racers_per_result_batch)
