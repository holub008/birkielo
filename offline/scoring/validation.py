import math

import pandas as pd
import numpy as np
from scipy.stats import spearmanr

from scoring.result_fetcher import ResultFetcher
from scoring.elo import NaiveElo
from scoring.elo import NearestNeighborElo
from scoring.elo import MeanElo


class ForwardChainingValidator:
    def __init__(self, results,
                 statistic=lambda x,y: spearmanr(x,y).correlation):
        self._results = results
        self._rater_to_measured_statistics = {}
        self._statistic = statistic

    def add_rater(self, rater):
        ratings_by_race = rater.blank_run(self._results)
        default_score = rater.get_uninformed_default()

        rating_joined_results = self._results.merge(ratings_by_race, how='left', on=['racer_id'])\
            .groupby(['race_id', 'event_date_x'])

        race_to_statistic = pd.DataFrame()
        for race, rating_joined_race_results in rating_joined_results:
            race_id = race[0]
            race_date = race[1]
            eligible_prior_ratings = rating_joined_race_results[(rating_joined_race_results.event_date_y <= race_date)]\
                .groupby(['racer_id'])
            prior_racer_ratings = []
            for racer_id, racer_ratings in eligible_prior_ratings:
                racer_ratings_before_race = racer_ratings[racer_ratings.event_date_y < race_date]
                if racer_ratings_before_race.shape[0]:
                    prior_rating_ix = racer_ratings_before_race.event_date_y.values.argmax()
                    prior_rating = racer_ratings_before_race.iloc[prior_rating_ix]
                    prior_racer_ratings.append((racer_id, prior_rating.score))
                else:
                    prior_racer_ratings.append((racer_id,default_score))
            prior_racer_ratings = pd.DataFrame(prior_racer_ratings, columns=['racer_id', 'score'])
            prior_racer_ratings['predicted_ranking'] = prior_racer_ratings.score.rank(ascending=False)

            actual_race_results = rating_joined_race_results[['racer_id', 'overall_place']].drop_duplicates()
            prediction_joined_results = actual_race_results.merge(prior_racer_ratings, how="inner", on=['racer_id'])

            stat = self._statistic(prediction_joined_results.predicted_ranking, prediction_joined_results.overall_place)
            part = pd.DataFrame([(race_id, race_date, stat, actual_race_results.shape[0])],
                                columns=['race_id', 'race_date', 'statistic', 'racers'])
            race_to_statistic = race_to_statistic.append(part)

        self._rater_to_measured_statistics[str(rater)] = race_to_statistic

    def get_validation_results(self):
        return self._rater_to_measured_statistics

##########################
# start control flow
##########################
results = None
with ResultFetcher() as fetcher:
    results = fetcher.get_results()

# ignore unmatched results, since we have no racer to track scores over time
results = results[~pd.isnull(results['racer_id'])]

rater1 = NaiveElo(k_factor=1)
rater2 = NaiveElo(k_factor=2)
rater3 = NaiveElo(k_factor=.5)
rater4 = NearestNeighborElo()
rater5 = MeanElo()
rater6 = NaiveElo(k_factor=5)
rater7 = NearestNeighborElo(k_factor=20)
rater8 = NearestNeighborElo(k_factor=5, neighborhood_proportion=.2, max_neighborhood_size=100)
rater9 = NaiveElo(k_factor=5, max_score_change=1000, score_floor=0, score_ceiling=10000)

validator = ForwardChainingValidator(results)
validator.add_rater(rater1)
validator.add_rater(rater2)
validator.add_rater(rater3)
validator.add_rater(rater4)
validator.add_rater(rater5)
validator.add_rater(rater6)
validator.add_rater(rater7)
validator.add_rater(rater8)
validator.add_rater(rater9)

rater_to_validation = validator.get_validation_results()

year_rater_validation = []
for rater in rater_to_validation:
    validation = rater_to_validation[rater][~pd.isnull(rater_to_validation[rater].statistic)]
    validation['year'] = [d.year for d in validation['race_date']]

    for year in validation.year.drop_duplicates():
        checkpoints = [x.statistic for _, x in rater_to_validation[rater].iterrows() if not pd.isnull(x.statistic)
                       and x.race_date.year == year]
        weights = [x.racers for _, x in rater_to_validation[rater].iterrows() if not pd.isnull(x.statistic)
                   and x.race_date.year == year]
        avg = np.average(checkpoints, weights=weights)
        year_rater_validation.append([rater, year, avg])

year_rater_validation = pd.DataFrame(year_rater_validation, columns=['rater', 'year', 'avg_rho'])
year_rater_validation.to_csv('/Users/kholub/year_validations.csv')
# year_rater_validation.plot(x='year', y='avg_rho', color=['rater'])
# because pandas+matplotlib < tidyverse:
# df <- read.csv('~/year_validations.csv', stringsAsFactors = F)
# ggplot(df %>% filter(year < 2019)) +
#   geom_line(aes(x=year, y=avg_rho, color=rater)) +
#   ylab('Spearman Rank Correlation (predicted vs. observed)') +
#   xlab('Year') +
#   ggtitle('Yearly averaged ranking accuracy')