import psycopg2 as pg

def get_connection(host="birkielo.cb5jkztmh9et.us-east-2.rds.amazonaws.com",
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


