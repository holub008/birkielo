import pandas as pd
import numpy as np

class NaiveElo:

    def __init__(self,
                 default_score=1000,
                 k_factor=1,
                 log_odds_oom_differential=400,
                 score_floor=100,
                 score_ceiling=3000):
        """
        for a simple mathemtical explanation of Elo parameters, see
        https://math.stackexchange.com/questions/1731991/why-does-the-elo-rating-system-work
        :param default_score: the prior score for a racer with no history
        :param k_factor: corresponds directly to the Elo k-factor, but much defaulting to lower than typical weight
         because an individual race (i.e. high variance) would be too highly weighted if the typical k=24 was used
        :param log_odds_oom_differential: if the odds are an order of magnitude (10x) higher of A beating B, we expect A
         to have a score log_odds_oom_differential higher than B
        :param score_floor: the minimum achievable score
        :param score_ceiling: the maximum achievable score
        """
        self._default_score = default_score
        self._k_factor = k_factor
        self._log_odds_oom_differential=log_odds_oom_differential
        self._score_floor = score_floor
        self._score_ceiling = score_ceiling

    def blank_run(self, results):
        """
        run the naive elo algorithm from a blank slate - i.e. no one has scores
        :param results: the race results to be considered in the updates
        :return: a dataframe with "sparse" scores over time for racers
        """
        previous_scores = results['racer_id'].drop_duplicates().to_frame()
        previous_scores['score'] = self._default_score

        return self.update_batch(previous_scores, results)

    def update_batch(self, previous_scores, results):
        """
        run the naive elo algorithm start from a set of previous scores
        :param previous_scores: a dataframe with columns "racer_id", "score"
        :param results: the race results to be considered in the updates
        :return: a dataframe with "sparse" scores over time for racers
        """
        time_ordered_grouped_races = results\
            .sort_values('event_date')\
            .groupby(['event_date', 'race_id', 'racer_gender'], sort=False)

        scores_through_time_sparse = pd.DataFrame()
        for race, results in time_ordered_grouped_races:
            race_scoped_updates = self._update_single_race(previous_scores, results)
            previous_scores = previous_scores.merge(race_scoped_updates, how='left', on=['racer_id'])
            previous_scores['score'] = np.where(pd.isnull(previous_scores.score_y),
                                                previous_scores.score_x,
                                                previous_scores.score_y)
            previous_scores = previous_scores.drop(columns=['score_x', 'score_y'])
            race_scoped_updates['event_date'] = race[0]
            scores_through_time_sparse = scores_through_time_sparse.append(race_scoped_updates)

        return scores_through_time_sparse

    def _update_single_race(self, previous_scores, results):
        prior_score_joined_results = results.merge(previous_scores, on='racer_id', how='left')
        prior_score_joined_results.fillna({'score': self._default_score})

        score_updates = pd.DataFrame()

        # the choice of unique racer_ids is because some "racers" participate in the same race more than once
        # of course, this is due to downstream matching issues- but we work around it here by only considering the first
        # TODO
        for race_result in prior_score_joined_results.drop_duplicates(['racer_id']).itertuples():
            linear_scale_racer_score = 10 ** (race_result.score / self._log_odds_oom_differential)
            accumulated_score_change = 0.0
            for competitor_race_result in prior_score_joined_results.itertuples():
                if competitor_race_result.racer_id != race_result.racer_id:
                    # TODO this is unnecessary repeated work
                    linear_scale_competitor_score = 10 ** (competitor_race_result.score /
                                                           self._log_odds_oom_differential)

                    p_racer = linear_scale_racer_score / (linear_scale_racer_score + linear_scale_competitor_score)
                    outcome = 1 if race_result.overall_place > competitor_race_result.overall_place else 0
                    accumulated_score_change += self._k_factor * (outcome - p_racer)

            updated_score = min(max(race_result.score + accumulated_score_change, self._score_floor),
                                self._score_ceiling)
            score_updates = score_updates.append({"racer_id": int(race_result.racer_id),
                                                  "score": updated_score},
                                                 ignore_index=True)

        return score_updates


