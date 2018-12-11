import psycopg2.extras as pge


def clear_prior_scores(cursor):
    """
    :param cursor: a psycopg2 cursor object. will not be mutated, outside of the deletion
    :return: void
    """
    query = "DELETE FROM racer_metrics"
    cursor.execute(query)


def insert_scores(cursor, scores):
    """
    :param cursor: a psycopg2 cursor object. will not be mutated, outside of the insertion
    :param scores: a dataframe including columns "racer_id", "date", "elo"
    :return: void
    """
    if not set(['racer_id', 'date', 'elo']).issubset(scores.columns):
        raise ValueError('Required column names are missing in input scores!')

    query_format = "INSERT INTO racer_metrics (racer_id, date, elo) VALUES %s"

    pge.execute_values(cursor, query_format, scores[['racer_id', 'date', 'elo']].values.tolist(),
                       page_size=1000)

