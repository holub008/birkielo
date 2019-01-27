import pandas as pd

from scoring.result_fetcher import ResultFetcher
from db import get_connection


def _remove_same_racer_in_same_race(results_fetcher, cursor):
    """
    :param results_fetcher: a result fetcher object in transaction with cursor
    :param cursor: a db cursor in transaction with the results_fetcher
    :return: void (updates the transaction)
    """
    results = result_fetcher.get_results()
    race_racer_counts = results.groupby(['race_id', 'racer_id']).size().reset_index(name='counts')
    problem_racers = race_racer_counts[race_racer_counts['counts'] > 1][['racer_id']].drop_duplicates()

    update_query = "UPDATE race_result SET racer_id = null WHERE racer_id IN %s"
    cursor.execute(update_query, (tuple(problem_racers['racer_id']), ))


def _resolve_gender_conflicts(result_fetcher, cursor):
    pass


def _camelcasify_racer_name(result_fetcher, cursor):
    pass


def _remap_known_names(result_fetcher, cursor, known_name_mapping_supplier = lambda: {
                 ('Matt', 'Liebsch'): ('Matthew', 'Liebsch'),
                 ('Caitlin', 'Compton'): ('Caitlin', 'Gregg')
             }):
    results = result_fetcher.get_results()
    name_mapping = known_name_mapping_supplier()

    name_mapping_list = []
    for name_from, name_to in name_mapping.items():
        name_mapping_list.append(list(name_from) + list(name_to))

    mapping_names_df = pd.DataFrame(name_mapping_list, columns=['from_first_name', 'from_last_name', 'to_first_name',
                                                                'to_last_name'])

    from_joinable_results = results.copy()
    from_joinable_results['from_first_name'] = from_joinable_results['first_name']
    from_joinable_results['from_last_name'] = from_joinable_results['last_name']

    to_joinable_results = results.copy()
    to_joinable_results['to_first_name'] = to_joinable_results['first_name']
    to_joinable_results['to_last_name'] = to_joinable_results['last_name']

    from_results = from_joinable_results.merge(mapping_names_df, how="inner", on=['from_first_name','from_last_name'])[
        ['to_first_name', 'to_last_name', 'racer_id', 'race_result_id']].drop_duplicates()
    to_results = to_joinable_results.merge(mapping_names_df, how="inner", on=['to_first_name', 'to_last_name'])[
        ['to_first_name', 'to_last_name', 'racer_id']].drop_duplicates()

    merged_results = from_results.merge(to_results, how="inner", on=['to_first_name', 'to_last_name'])

    racer_id_updates = merged_results[['racer_id_x', 'racer_id_y']].drop_duplicates()

    for index, update in racer_id_updates.iterrows():
        update_query = "UPDATE race_result SET racer_id = %s where racer_id = %s"
        cursor.execute(update_query, (update['racer_id_y'], update['racer_id_x']))

        metric_delete_query = "DELETE FROM racer_metric WHERE racer_id = %s"
        cursor.execute(metric_delete_query, (update['racer_id_x']))

        racer_delete_query = "DELETE FROM racer WHERE id = %s"
        cursor.execute(racer_delete_query, (update['racer_id_x']))


if __name__ == '__main__':
    con = None
    try:
        con = get_connection()
        cursor = con.cursor()

        result_fetcher = ResultFetcher(con)

        _camelcasify_racer_name(result_fetcher, cursor)
        _remap_known_names(result_fetcher, cursor)
        _remove_same_racer_in_same_race(result_fetcher, cursor)
        _resolve_gender_conflicts(result_fetcher, cursor)

        #con.commit()
        cursor.close()
    except Exception as e:
        print('Failed to clean up results: %s' % e)
    finally:
        if con:
            con.rollback()
            con.close()
