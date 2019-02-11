import pandas as pd
import numpy as np
from gender_guesser import detector
import psycopg2.extras as pge

from scoring.result_fetcher import ResultFetcher
from db import get_connection

GENDER_DETECTOR = detector.Detector()


def _remove_same_racer_in_same_race(result_fetcher, cursor):
    """
    :param result_fetcher: a result fetcher object in transaction with cursor
    :param cursor: a db cursor in transaction with the results_fetcher
    :return: void (updates the transaction)
    """
    results = result_fetcher.get_results()
    race_racer_counts = results.groupby(['race_id', 'racer_id']).size().reset_index(name='counts')
    problem_racers = race_racer_counts[race_racer_counts['counts'] > 1][['racer_id']].drop_duplicates()

    update_query = "UPDATE race_result SET racer_id = null WHERE racer_id IN %s"
    cursor.execute(update_query, (tuple(problem_racers['racer_id']), ))
    delete_query = "DELETE FROM racer WHERE id IN %s"
    cursor.execute(delete_query, (tuple(problem_racers['racer_id']), ))


def _rerank_races(results, race_ids_for_gender_reranking):
    """
    returns a dataframe with race_result_id to gender_place mapping updates to be made
    """
    rerankable_races = pd.DataFrame({"race_id": list(set(race_ids_for_gender_reranking))})
    results_copy = results.copy()
    # if a race_result has no racer, fall back to the race_result gender
    results_copy['racer_gender'] = np.where(pd.isnull(results_copy['racer_gender']), results_copy['race_result_gender'],
                                            results_copy['racer_gender'])
    rerankable_results = results_copy.merge(rerankable_races, how="inner", on=['race_id'])\
        .groupby(['race_id', 'racer_gender'])

    corrected_results = pd.DataFrame()
    for group, race_results in rerankable_results:
        # TODO duration may not always be present (in favor of overall place)
        race_results['gender_place'] = race_results.sort_values('overall_place')['duration']\
            .rank(method="first")

        corrected_results = corrected_results.append(race_results)

    return corrected_results


def _resolve_gender_conflicts(result_fetcher, cursor):
    results = result_fetcher.get_results()
    results_with_racer = results[~pd.isnull(results['racer_id'])]
    racer_gender_counts = results_with_racer.groupby('racer_id')['race_result_gender'].nunique()\
        .to_frame().reset_index()
    mixed_gender_racers = racer_gender_counts[racer_gender_counts['race_result_gender'] > 1]

    mixed_gender_results = results_with_racer.merge(mixed_gender_racers, how="inner", on=['racer_id'])
    mixed_gender_results['race_result_gender'] = mixed_gender_results['race_result_gender_x']
    grouped_results = mixed_gender_results.groupby(['racer_id'])

    race_ids_for_gender_reranking = []
    racer_ids_for_male_reassignment = []
    racer_ids_for_female_reassignment = []

    for racer_id, group in grouped_results:
        male_results = group[group['race_result_gender'] == 'male']
        female_results = group[group['race_result_gender'] == 'female']

        male_frequency = male_results.shape[0] / (female_results.shape[0] + male_results.shape[0])
        female_frequency = 1 - male_frequency

        # TODO obviously this doesn't capture statistical variation (confidence increases some amount at larger n)
        if female_frequency < .3:
            race_ids_for_gender_reranking += list(female_results['race_id'])
            racer_ids_for_male_reassignment.append(racer_id)
        elif male_frequency < .3:
            race_ids_for_gender_reranking += list(male_results['race_id'])
            racer_ids_for_female_reassignment.append(racer_id)
        else:
            first_name = male_results['first_name'].iloc[0]
            statistical_gender = GENDER_DETECTOR.get_gender(first_name)

            if statistical_gender == 'mostly_male' or statistical_gender == 'male':
                race_ids_for_gender_reranking += list(female_results['race_id'])
                racer_ids_for_male_reassignment.append(racer_id)
            elif statistical_gender == 'mostly_female' or statistical_gender == 'female':
                race_ids_for_gender_reranking += list(male_results['race_id'])
                racer_ids_for_female_reassignment.append(racer_id)
            # everyone else gets left behind :(
            # this means that not only are some genders incorrect, but gender rankings are increasingly inaccurate
            # towards the end of results

    ################
    # now to handle racers with only 1 result, which happened in an incorrectly gendered race
    # doing this naively would drag a lot of good results into the statistical regendering by name approach
    # e.g. 4000 results would be questionably regendered because "Maxwell Joda" was incorrectly entered into the
    # Birkie's system as a female: https://cdn.birkie.com/Results/2011/Birkie-Skate/b_skate_overall.pdf
    # to avoid this, we only look at races with a substantial proportion of misgendered racers (according to our
    # multi-race mislabelled racers)
    ################
    racer_counts = results_with_racer.groupby('racer_id').size().reset_index(name='n_results')
    single_race_results = racer_counts[racer_counts['n_results'] == 1]
    race_counts = results_with_racer.groupby('race_id').size().reset_index(name='n_racers')
    misgendered_races = [(r, race_ids_for_gender_reranking.count(r)) for r in set(race_ids_for_gender_reranking)]
    races_with_misgendered_counts = pd.DataFrame(misgendered_races, columns=['race_id', 'misgendered'])\
        .merge(race_counts, how="inner", on=['race_id'])
    races_for_reassignment = races_with_misgendered_counts[races_with_misgendered_counts['misgendered'] /
                                                           races_with_misgendered_counts['n_racers'] > .1]
    misgendered_race_results = results.merge(races_for_reassignment, how="inner", on=['race_id'])
    racers_for_reassignment = misgendered_race_results.merge(single_race_results, how="inner", on=['racer_id'])

    for index, result in racers_for_reassignment.iterrows():
        statistical_gender = GENDER_DETECTOR.get_gender(result['first_name'])

        if statistical_gender == 'male' and not result['racer_gender'] == 'male':
            racer_ids_for_male_reassignment.append(result['racer_id'])
        elif statistical_gender == 'female':
            racer_ids_for_female_reassignment.append(result['racer_id'])

    ################
    # now, write updated genders
    ################
    racer_query = "UPDATE racer SET gender = %s WHERE id IN %s"
    race_record_query = "UPDATE race_result SET gender = %s WHERE racer_id IN %s"

    cursor.execute(racer_query, ('male', tuple(racer_ids_for_male_reassignment)))
    cursor.execute(race_record_query, ('male', tuple(racer_ids_for_male_reassignment)))

    cursor.execute(racer_query, ('female', tuple(racer_ids_for_female_reassignment)))
    cursor.execute(race_record_query, ('female', tuple(racer_ids_for_female_reassignment)))

    ################
    # reload the results & re-rank gender placements
    # note we are on the same transaction, so new genders will be reflected in this round of fetched results
    # finally, note we are using a temp table for the bulk update, since there's substantial network overhead for
    # non-batched updates, of which we expect 10K+
    ################
    results = result_fetcher.get_results()
    reranked_results = _rerank_races(results, race_ids_for_gender_reranking)
    values_for_update = reranked_results[['race_result_id', 'gender_place']].values.tolist()

    temp_table_create = """
        CREATE TEMPORARY TABLE race_result_update (
            race_result_id INTEGER PRIMARY KEY, -- postgres docs specify that the sequence is also temporary
            gender_place INTEGER NOT NULL
        )
        ON COMMIT DROP
    """
    cursor.execute(temp_table_create)

    insert_query = "INSERT INTO race_result_update (race_result_id, gender_place) VALUES %s "
    pge.execute_values(cursor, insert_query, values_for_update, page_size=1000)

    update_query = """
        UPDATE race_result rr
        SET
            gender_place = rru.gender_place
        FROM race_result_update rru
        WHERE
            rr.id = rru.race_result_id
    """

    cursor.execute(update_query)


def _correct_name(name):
    if not name:
        return name

    # https://docs.python.org/3/library/stdtypes.html#str.title
    # this function is a bit goofy, but handles the use case well - even caps after periods and apostrophes
    if name.islower() or name.isupper():
        return name.title()

    # if it's not all upper or all lower, assume that casing is correct (avoid disturbing mid-name captializations)
    return name


def _casify_racer_names(result_fetcher, cursor):
    results = result_fetcher.get_results()
    racers = results[~pd.isnull(results['racer_id'])][['first_name', 'middle_name', 'last_name',
                                                       'racer_id']].drop_duplicates()

    racers['updated_first_name'] = [_correct_name(fn) if fn else fn for fn in racers['first_name']]
    racers['updated_middle_name'] = [_correct_name(mn) if mn else mn for mn in racers['middle_name']]
    racers['updated_last_name'] = [_correct_name(ln) if ln else ln for ln in racers['last_name']]

    for index, racer in racers.iterrows():
        updated_values = []
        if not racer['first_name'] == racer['updated_first_name']:
            updated_values.append(('first_name', racer['updated_first_name']))
        if not racer['middle_name'] == racer['updated_middle_name']:
            updated_values.append(('middle_name', racer['updated_middle_name']))
        if not racer['last_name'] == racer['updated_last_name']:
            updated_values.append(('last_name', racer['updated_last_name']))

        # I could not find a general method for single & multi column updates in psycopg/postgres :(
        if len(updated_values) == 1:
            query_format = "UPDATE racer SET {} = %s WHERE id = %s"
            sql = query_format.format(updated_values[0][0])
            params = (updated_values[0][1], racer['racer_id'],)
            cursor.execute(sql, params)
        elif updated_values:
            query_format = "UPDATE racer SET ({}) = (%s) WHERE id = %s"
            sql = query_format.format(' ,'.join(p[0] for p in updated_values))
            params = (tuple(p[1] for p in updated_values), racer['racer_id'],)
            cursor.execute(sql, params)


# these two get special treatment because they are both the number 1 ranked skiers, & they both have name variants
def _remap_known_names(result_fetcher, cursor, known_name_mapping_supplier=lambda: {
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

    from_results = from_joinable_results.merge(mapping_names_df, how="inner", on=['from_first_name', 'from_last_name'])[
        ['to_first_name', 'to_last_name', 'racer_id', 'race_result_id']].drop_duplicates()
    to_results = to_joinable_results.merge(mapping_names_df, how="inner", on=['to_first_name', 'to_last_name'])[
        ['to_first_name', 'to_last_name', 'racer_id']].drop_duplicates()

    merged_results = from_results.merge(to_results, how="inner", on=['to_first_name', 'to_last_name'])

    racer_id_updates = merged_results[['racer_id_x', 'racer_id_y']].drop_duplicates()

    for index, update in racer_id_updates.iterrows():
        update_query = "UPDATE race_result SET racer_id = %s WHERE racer_id = %s"
        cursor.execute(update_query, (int(update['racer_id_y']), int(update['racer_id_x'])))

        metric_delete_query = "DELETE FROM racer_metrics WHERE racer_id = %s"
        cursor.execute(metric_delete_query, (int(update['racer_id_x']), ))

        racer_delete_query = "DELETE FROM racer WHERE id = %s"
        cursor.execute(racer_delete_query, (int(update['racer_id_x']), ))


if __name__ == '__main__':
    con = None
    try:
        con = get_connection()
        cursor = con.cursor()

        result_fetcher = ResultFetcher(con)

        _casify_racer_names(result_fetcher, cursor)
        _remap_known_names(result_fetcher, cursor)
        _remove_same_racer_in_same_race(result_fetcher, cursor)
        _resolve_gender_conflicts(result_fetcher, cursor)

        con.commit()
        cursor.close()
    except Exception as e:
        print('Failed to clean up results: %s' % e)
    finally:
        if con:
            con.rollback()
            con.close()
