import pandas as pd
import psycopg2 as pg
import psycopg2.sql as pgs
import psycopg2.extras as pge

_RACER_INSERT_QUERY = """
    INSERT INTO racer (first_name, middle_name, last_name, gender, age_lower, age_upper)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING id
"""

_RACER_RESULT_INSERT_QUERY = """
    INSERT INTO race_result (racer_id, race_id, overall_place, gender_place, duration, gender, age_lower, age_upper)
    VALUES %s
"""


# common utilities for processing (e.g. matching racers) & inserting (to db) event, race, and results
# note that we prefer psycopg2 to standard pandas to_sql because we want the generated ids of inserted rows
# (RETURNING clause). However, the order of RETURNING is not strictly guaranteed by postgres

def get_db_connection(host="birkielo.cb5jkztmh9et.us-east-2.rds.amazonaws.com",
                      port=5432,
                      username="kholub",
                      database="birkielo"):
    """
    get a connection to the birkielo database. note that this currently relies on a local pgpass entry
    which obviously is not checked into source control. also note any exceptions in creation are bubbled

    :param host: db host to connect to
    :param port: port to connect to on host
    :param username: username for db auth
    :param database: database to connect to
    :return: a birkielo database connection object
    """
    return pg.connect(dbname = database, user = username, host = host, port = port)


def _insert_and_get_generic(cursor, df, table_name, required_columns):
    if not set(required_columns).issubset(df.columns):
        raise ValueError('Required column names are missing in input events!')
    values_for_insert = df[required_columns].values.tolist()
    # note we can't "safely" insert the table name here. still, we expect all table names to come internally, so string concat is OK
    # once https://github.com/psycopg/psycopg2/issues/794 is resolved, solution looks like:
    # query_value_format = pgs.SQL("INSERT INTO {} ({}) VALUES %s RETURNING *").format(pgs.Identifier(table_name), pgs.SQL(', ').join(map(sql.Identifier, required_columns))
    query_value_format = "INSERT INTO " + table_name + ' (' + ','.join(required_columns) + ') VALUES %s RETURNING *'
    pge.execute_values(cursor, query_value_format, values_for_insert)
    result_set = cursor.fetchall()
    result_df = pd.DataFrame(result_set)
    # note, we assume that anything worth getting is returning an "id" column
    result_df.columns = ["id"] + required_columns
    return result_df


def insert_and_get_events(cursor, events):
    """
    insert event and get it in the same transaction. note it is assumed this event does not exist in db yet.
    at some point in the future, this function may be extended to return a pre-existing event, but since it requires
    already knowing the event details & some level of fuzzy matching, it's high effort & not currently implemented.

    :param cursor: a writable cursor object. this function makes no mutation to it besides the insert and select
    :param events: a dataframe representing events. required columns: "event_name"
    :return: a dataframe representing the inserted events (notably including the db backed event id)
    """
    return _insert_and_get_generic(cursor, events, "event", ['name'])


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


def insert_racers(cursor, racers_to_race_record_indices, race_results):
    """
    note that this function does no batching in the name of correctness (postgres does not guarantee the order
    of returning statements), and is slow due to network overhead
    :param cursor: a writable connection object. this function makes no mutation to it besides the insert and select
    :param racers_to_race_record_indices: a list of tuples with racer identities in first position. will be mutated
    :param race_results: a list of raw race results, indexed by the prior argument
    :return: void
    """

    # TODO this should be batched
    for ix, racer_to_ix in enumerate(racers_to_race_record_indices):
        if ix % 1000 == 0 and ix != 0:
            print("Inserted %s of %s racers" % (ix, len(racers_to_race_record_indices)))

        racer_identity = racer_to_ix[0]
        race_results_for_racer = [race_results[ix] for ix in racer_to_ix[1]]
        cursor.execute(_RACER_INSERT_QUERY,
                       (racer_identity.get_first_name(), racer_identity.get_middle_name(),
                        racer_identity.get_last_name(), racer_identity.get_gender().value,
                        racer_identity.get_age_lower(), racer_identity.get_age_upper()))
        result_set = cursor.fetchall()
        racer_identity_id = result_set[0][0]

        values_for_insert = [(racer_identity_id, rr.get_race_id(), rr.get_overall_place(), rr.get_gender_place(),
                              rr.get_duration(), rr.get_gender().value, rr.get_age_lower(), rr.get_age_upper())
                             for rr in race_results_for_racer]
        pge.execute_values(cursor, _RACER_RESULT_INSERT_QUERY, values_for_insert)
