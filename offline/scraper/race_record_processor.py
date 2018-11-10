import pandas as pd
import psycopg2 as pg
import psycopg2.sql as pgs
import psycopg2.extras as pge


## common utilities for processing (e.g. matching racers) & inserting (to db) event, race, and results
## note that we prefer psycopg2 to standard pandas to_sql because we want the generated ids of inserted rows (RETURNING clause)

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
    at some point in the future, this function may be extended to return a pre-existing event, but since it requires already
    knowing the event details & some level of fuzzy matching, it's high effort & not currently implemented.
    same argument applies to below table insert

    :param cursor: a writable cursor object. this function makes no mutation to it besides the insert and select
    :param event: a dataframe representing events. required columns: "event_name"
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


def insert_and_get_racers(cursor, racers):
    """

    :param cursor: a writable connection object. this function makes no mutation to it besides the insert and select
    :param racers: a dataframe representing racers. required columns: "first_name", "middle_name", "last_name", "gender"
    :return: a dataframe representing the inserted racers
    """
    return _insert_and_get_generic(cursor, racers, "racers", ['first_name', 'middle_name', 'last_name', 'gender'])