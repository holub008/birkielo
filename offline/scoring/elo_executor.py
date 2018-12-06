from scoring.result_fetcher import ResultFetcher
from scoring.elo import MeanElo
from db import get_connection
from scoring.score_committer import insert_scores

fetcher = ResultFetcher()
results = fetcher.get_results()


elo_scorer = MeanElo()
historical_elos = elo_scorer.blank_run(results)
historical_elos['elo'] = historical_elos['score']
historical_elos['date'] = historical_elos['event_date']
historical_elos['racer_id'] = historical_elos.racer_id.astype(int)
# TODO this is an artifact of poor upstream matching
historical_elos = historical_elos.drop_duplicates(['racer_id', 'date'])

with get_connection() as con:
    cursor = con.cursor()
    insert_scores(cursor, historical_elos)

    con.commit()