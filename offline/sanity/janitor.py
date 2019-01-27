import pandas as pd

from scoring.result_fetcher import ResultFetcher
from db import get_connection


def _remove_same_racer_in_same_race(results):
    pass


def _resolve_gender_conflicts(results):
    pass


def _remap_known_names(result_fetcher, known_name_mapping_supplier = lambda: {
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
    racers_for_deletion = merged_results[['racer_id_x']].drop_duplicates()

if __name__ == '__main__':
    con = None
    try:
        con = get_connection()
        result_fetcher = ResultFetcher(connection_supplier=lambda: con)


        con.commit()
    finally:
        if con:
            con.rollback()
            con.close()