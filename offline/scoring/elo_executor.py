from result_fetcher import ResultFetcher
from naive_elo import NaiveElo

fetcher = ResultFetcher()
results = fetcher.get_results()


elo_scorer = NaiveElo()
historical_elos = elo_scorer.blank_run(results)

