import psycopg2 as pg

## common utilities for processing (e.g. matching racers) & inserting (to db) event, race, and results

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

def insert_and_get_events(cursor, events):
    """
    insert an event if not already present and get it in the same transaction

    :param cursor: a writable connection object. this function makes no mutation to it besides the insert and select
    :param event: a dataframe representing events. required columns: "name"
    :return: a dataframe representing the inserted or existing event (notably including the db backed event id)
    """
    # TODO these neither uses the input nor returns a dataframe
    cursor.execute("INSERT INTO event (name) VALUES ('blah') RETURNING *")
    return cursor.fetchall()

def insert_and_get_event_occurrences(cursor, event_occurrences):
    """
    insert an event occurrence if not already present get it in the same transaction

    :param cursor:  a writable connection object. this function makes no mutation to it besides the insert and select
    :param event_occurrences: a dataframe representing event occurrences. required columns: "event_id"
    :return:
    """