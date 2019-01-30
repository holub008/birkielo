from datetime import datetime
import pandas as pd

from db import get_connection

_RESULTS_QUERY_FORMAT = """
SELECT
  eo.date as event_date,
  r.id as race_id,
  rr.gender_place,
  rr.overall_place,
  rr.duration,
  rr.id as race_result_id,
  rr.gender as race_result_gender,
  ra.first_name,
  ra.middle_name,
  ra.last_name,
  ra.id as racer_id,
  ra.gender as racer_gender
FROM event_occurrence eo
JOIN race r
  ON eo.id = r.event_occurrence_id
JOIN race_result rr
  ON r.id = rr.race_id
LEFT JOIN racer ra
  ON rr.racer_id = ra.id
WHERE
  eo.date >= %s
  AND eo.date <= %s
"""

_METRICS_QUERY_FORMAT = """
SELECT
  rm.racer_id,
  first_value(rm.elo) OVER w AS elo,
  first_value(rm.date) OVER w AS date
FROM racer_metrics rm
WHERE
  rm.date >= %s
WINDOW w AS (
  PARTITION BY rm.racer_id
  ORDER BY date DESC
)
"""


class ResultFetcher:
    def __init__(self, connection=None):
        """

        :param connection: a nullable db connection. if not supplied, the fetcher may only be used in a context manager
         if supplied, the user is in control of proper shutdown and transaction management
        """
        self._connection = connection

    def _query_precondition(self):
        if not self._connection:
            raise ValueError('Connection is unset. Either supply and manually manage the connection, or use in context '
                             'manager')

    def get_results(self,
                    min_date=None,
                    max_date=None):
        """
        fetch all race results within a date range (inclusive)
        :param min_date: the minimum datetime.date for any race included in the result set. None implies unbounded
        :param max_date: the maximum datetime.date for any race included in the result set. None implies unbounded
        :return: a pandas dataframe corresponding to all matched results in the supplied date range
        """

        self._query_precondition()

        min_date = datetime.min.date() if min_date is None else min_date
        max_date = datetime.max.date() if max_date is None else max_date

        if min_date > max_date:
            raise ValueError('min_date argument cannot be greater than max_date argument')

        # just let any exceptions bubble - either the context manager will clean up, or client is handling
        cursor = self._connection.cursor()
        cursor.execute(_RESULTS_QUERY_FORMAT, (min_date, max_date))
        rs = cursor.fetchall()

        results_df = pd.DataFrame(rs)
        results_df.columns = ('event_date', 'race_id', 'gender_place', 'overall_place', 'duration', 'race_result_id',
                              'race_result_gender', 'first_name', 'middle_name', 'last_name', 'racer_id',
                              'racer_gender')

        # since pandas dislikes datetime.date types (https://github.com/pandas-dev/pandas/issues/8802)
        results_df['event_date'] = pd.to_datetime(results_df.event_date)

        return results_df

    def get_prior_metrics(self, date=None):
        """
        get racer metrics at a point in time
        :param date: the date in time (inclusive) up to which metrics are fetched
        :return: a dataframe with columns "date", "racer_id", "elo", unique on racer_id
        """

        self._query_precondition()

        date = datetime.max.date() if date is None else date

        cursor = self._connection.cursor()
        cursor.execute(_METRICS_QUERY_FORMAT, (date,))
        rs = cursor.fetchall()

        results_df = pd.DataFrame(rs)
        results_df.columns = ('racer_id', 'elo', 'date')

        return results_df

    def __enter__(self):
        self._connection = self._connection if self._connection else get_connection()
        return self

    def __exit__(self, type, value, traceback):
        if self._connection:
            self._connection.close()