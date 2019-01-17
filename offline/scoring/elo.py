import pandas as pd
import numpy as np
from scipy import stats


class NaiveElo:

    def __init__(self,
                 default_score=1000,
                 k_factor=2,
                 log_odds_oom_differential=200,
                 score_floor=100,
                 score_ceiling=3000,
                 max_score_change=200):
        """
        for a simple mathematical explanation of Elo parameters, see
        https://math.stackexchange.com/questions/1731991/why-does-the-elo-rating-system-work
        :param default_score: the prior score for a racer with no history
        :param k_factor: corresponds directly to the Elo k-factor, but much defaulting to lower than typical weight
         because an individual race (i.e. high variance) would be too highly weighted if the typical k=24 was used
        :param log_odds_oom_differential: if the odds are an order of magnitude (10x) higher of A beating B, we expect A
         to have a score log_odds_oom_differential higher than B
        :param score_floor: the minimum achievable score
        :param score_ceiling: the maximum achievable score
        :param max_score_change the maximum change in score that may occur in any one race
        """
        self._default_score = default_score
        self._k_factor = k_factor
        self._log_odds_oom_differential=log_odds_oom_differential
        self._score_floor = score_floor
        self._score_ceiling = score_ceiling
        self._max_score_change = max_score_change

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
            .groupby(['event_date', 'race_id'], sort=False)

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
                    outcome = 1 if race_result.overall_place < competitor_race_result.overall_place else 0
                    accumulated_score_change += self._k_factor * (outcome - p_racer)

            capped_score_change = max(min(accumulated_score_change, self._max_score_change), -self._max_score_change)
            updated_score = min(max(race_result.score + capped_score_change, self._score_floor),
                                self._score_ceiling)
            score_updates = score_updates.append({"racer_id": int(race_result.racer_id),
                                                  "score": updated_score},
                                                 ignore_index=True)

        return score_updates


class MeanElo(NaiveElo):
    def __init__(self,
                 prior_score_mean=1000,
                 # this is actually about a quarter of what I expect - reflecting a desire to smooth towards the mean
                 # since 1 race does not provide a reliable point estimate
                 prior_score_standard_deviation=100,
                 # k factor is much higher than the naive implementation because we are making only 2 updates per race
                 k_factor=30,
                 log_odds_oom_differential=400,
                 score_floor=100,
                 score_ceiling=3000):
        """
        :param prior_score_mean: mean of the prior score (gaussian) distribution (in the event of a missing score)
        :param prior_score_standard_deviation: sd of the prior score (gaussian) distribution (in the event of a missing score)
        """
        # default scores aren't used by this implementation since cold start needs some signal
        default_score = -1
        super().__init__(default_score, k_factor, log_odds_oom_differential, score_floor, score_ceiling)
        self._prior_score_mean = prior_score_mean
        self._prior_score_standard_deviation = prior_score_standard_deviation

    # this is used to overcome the cold start problem.
    # if everyone starts with a flat score as in the naive implementation, no differentiation occurs(except in 1st/last)
    # to overcome this, we inject a small signal from get-go; this prior is used to create scores for the heuristic
    # that higher placing skiers (in any given race, even their 1st) should generally be expected to have a higher score
    def _get_smoothed_prior_score(self, percentile):
        """
        we assume that scores are normally distributed (TODO empirically verify this) with preconfigured mean &
        variance. the normal quantile corresponding to this culmulative density = percentile is returned
        :param percentile: a 0-1 float representing the racer ranking among general population
        :return: the estimated score based on rank percentile
        """
        return stats.norm.ppf(percentile, self._prior_score_mean, self._prior_score_standard_deviation)

    def blank_run(self, results):
        """
        run the naive elo algorithm from a blank slate - i.e. no one has scores
        :param results: the race results to be considered in the updates
        :return: a dataframe with "sparse" scores over time for racers
        """
        previous_scores = results['racer_id'].drop_duplicates().to_frame()
        # this is quite goofy, since it's piped through and ignored
        # I'm not sure of a pythonic/low-overhead way to abstract it, so hacking for now. NaNs will bubble if trouble
        previous_scores['score'] = np.NaN

        return self.update_batch(previous_scores, results)

    def _update_single_race(self, previous_scores, results):
        total_racers = np.max(results.gender_place)
        prior_score_joined_results = results.merge(previous_scores, on='racer_id', how='left')
        # TODO does it make sense to re-run the racer through this Elo iteration after assigning a prior?
        # TODO some cases where gender place is larger than total # of racers because we dropped some in parsing
        # can fix by re-assigning ranks based on placement or duration
        prior_score_joined_results['score'] = [rr.score if not pd.isnull(rr.score) else
                                               self._get_smoothed_prior_score(
                                                   1 - min(max(rr.gender_place / total_racers, .01), .99))
                                               for ix,rr in prior_score_joined_results.iterrows()]
        score_updates = pd.DataFrame()

        # the choice of unique racer_ids is because some "racers" participate in the same race more than once
        # of course, this is due to upstream matching issues- but we work around it here by only considering the first
        # TODO
        for ix, race_result in prior_score_joined_results.drop_duplicates(['racer_id']).iterrows():
            linear_scale_racer_score = 10 ** (race_result.score / self._log_odds_oom_differential)

            other_race_results = prior_score_joined_results[prior_score_joined_results.racer_id != race_result.racer_id]
            beat_race_results = other_race_results[other_race_results.overall_place >= race_result.overall_place]
            loss_race_results = other_race_results[other_race_results.overall_place < race_result.overall_place]

            accumulated_score_change = 0.
            if beat_race_results.shape[0]:
                mean_beat_elo = np.mean(beat_race_results.score)
                linear_scale_beat_elo = 10 ** (mean_beat_elo / self._log_odds_oom_differential)
                p_racer = linear_scale_racer_score / (linear_scale_racer_score + linear_scale_beat_elo)
                accumulated_score_change += self._k_factor * (1 - p_racer)

            if loss_race_results.shape[0]:
                mean_loss_elo = np.mean(loss_race_results.score)
                linear_scale_loss_elo = 10 ** (mean_loss_elo / self._log_odds_oom_differential)
                p_racer = linear_scale_racer_score / (linear_scale_racer_score + linear_scale_loss_elo)
                # only difference from the above code block is here we scale inversely to the probability of beating
                accumulated_score_change += self._k_factor * -p_racer

            updated_score = min(max(race_result.score + accumulated_score_change, self._score_floor),
                                self._score_ceiling)
            score_updates = score_updates.append({"racer_id": int(race_result.racer_id),
                                                  "score": updated_score},
                                                 ignore_index=True)

        return score_updates
