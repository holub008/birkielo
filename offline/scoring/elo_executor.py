import pandas as pd

from scoring.result_fetcher import ResultFetcher
from scoring.elo import NaiveElo
from db import get_connection
from scoring.score_committer import insert_scores
from scoring.score_committer import clear_prior_scores

results = None
with ResultFetcher() as fetcher:
    results = fetcher.get_results()

# ignore unmatched results, since we have no racer to track scores over time
results = results[~pd.isnull(results['racer_id'])]

elo_scorer = NaiveElo()
historical_elos = elo_scorer.blank_run(results)
historical_elos['elo'] = historical_elos['score']
historical_elos['date'] = historical_elos['event_date']
historical_elos['racer_id'] = historical_elos['racer_id'].astype(int)
# this isn't strictly necessary if the janitor has been run recently - but in case results have been ingested
# without being cleaned up first, defensively make sure racer_ids are unique to a date
historical_elos = historical_elos.drop_duplicates(['racer_id', 'date'])

with get_connection() as con:
    cursor = con.cursor()

    clear_prior_scores(cursor)
    insert_scores(cursor, historical_elos)

    con.commit()
