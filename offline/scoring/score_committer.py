import psycopg2.extras as pge


def insert_scores(cursor, scores):
    if not set(['racer_id', 'date', 'elo']).issubset(scores.columns):
        raise ValueError('Required column names are missing in input scores!')

    query_format = "INSERT INTO racer_metrics (racer_id, date, elo) VALUES %s"

    pge.execute_values(cursor, query_format, scores[['racer_id', 'date', 'elo']].values.tolist(),
                       page_size=1000)