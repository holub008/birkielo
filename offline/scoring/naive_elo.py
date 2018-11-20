import pandas as pd

class NaiveElo:

    def __init__(self, default_score=1000):
        self._default_score = default_score

    def blank_run(self, results):
        """
        run the naive elo algorithm from a blank slate - i.e. no one has scores
        :param results: the race results to be considered in the updates
        :return: a dataframe with "sparse" scores over time for racers
        """
        previous_scores = results['racer_id'].drop_duplicates()
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
            .groupby(['event_date', 'race_id'])\
            .apply(lambda x: x.sort_values('event_date'))

        scores_through_time_sparse = pd.DataFrame()
        for race, results in time_ordered_grouped_races:
            race_scoped_updates = self._update_singe_race(previous_scores, results)
            # todo this is busted, need to actually make the merge on left joined columns
            previous_scores = previous_scores.merge(race_scoped_updates, how='left', on=['racer_id'])
            scores_through_time_sparse = scores_through_time_sparse.append(race_scoped_updates)

        return scores_through_time_sparse

    def _update_single_race(self, previous_scores, results):
        pass

