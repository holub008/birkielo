import re
import requests
import json
from bs4 import BeautifulSoup

EVENT_URL = "https://my5.raceresult.com/RRPublish/data/config.php?callback=no&eventid=%d"
# expected args are event id, listname, and contest number
RESULTS_URL = "https://my5.raceresult.com/RRPublish/data/list.php?callback=no&eventid=%d&key=%s&listname=%s&page=results&contest=%d&r=all"


# given an event results page, returns the races in the event
def get_mrr_races(mrr_url):
    # some links have the id as a query param, others in the path
    matches = re.search(r'.+(=|/)([0-9]+)/?#?$', mrr_url)
    event_id = -1
    if matches:
        event_id = int(matches.group(2))
    else:
        return None

    res = requests.get(EVENT_URL % (event_id,))
    if res.status_code != 200:
        return None

    soup = BeautifulSoup(res.content, 'lxml')

    json_payload = ""
    matches = re.search(r'no\((.*)\);$', res.text)
    if matches:
        json_payload = matches.group(1)
    else:
        return None
    event_dict = json.loads(json_payload)

    event_key = event_dict['key']
    race_id_lists = event_dict['lists']
    # yes, this is bizarre / cruel and unusual. there are "Name"s, "ID"s, & "Contest"s which all uniquely identify
    # races and key into different data. it's debatable if using a headless browser would be simpler than hitting API
    # oh and we have event id & event key...
    contest_id_to_race_id = [(ril['Contest'], ril['Name'], event_id, event_key) for ril in race_id_lists
                              if ril['ShowAs'] == 'Division Results']

    return contest_id_to_race_id


def _index_subset(lst, ixs):
    return [lst[ix] for ix in ixs]


def _get_column_names_from_required_columns(required_columns):
    return [c[0] for c in required_columns]


def _get_desired_column_indices(column_names, required_columns):
    column_indices = []
    for required_column_set in required_columns:
        matches = [ix for ix,col in enumerate(column_names) if col in required_column_set]
        if len(matches):
            column_indices.append(matches[0])
        else:
            column_indices.append(-1)
    return column_indices


def _is_iterable(x):
    try:
        iterator = iter(x)
    except TypeError:
        return False

    return True


def _recursive_unnest(dictionary):
    for value in dictionary.values():
        if isinstance(value, dict):
            yield from _recursive_unnest(value)
        else:
            # this is a shallow yield out
            if _is_iterable(value):
                yield from value
            else:
                yield value


def get_mrr_results(event_id, event_key, race_name, contest_number,
                    required_columns=(('Name',), ('City/State',),
                                      ('AG (Rank)', 'AG', 'AG/Rank'), ('Finish', 'Time'))):
    url = RESULTS_URL % (event_id, event_key, race_name, contest_number)
    res = requests.get(url)

    matches = re.search(r'no\((.*)\);$', res.text)
    if matches:
        json_payload = matches.group(1)
    else:
        return None, None
    event_dict = json.loads(json_payload)

    if 'list' not in event_dict or 'data' not in event_dict:
        return None, None

    if 'Fields' not in event_dict['list']:
        return None, None

    column_names = [col['Label'] for col in event_dict['list']['Fields']]
    desired_column_indices = _get_desired_column_indices(column_names, required_columns)

    if any(x < 0 for x in desired_column_indices):
        return None, None

    result_data = event_dict['data']
    results = list(_recursive_unnest(result_data))
    # off by 1 fun times - must be an implicit id column
    results_subset = [_index_subset(result[1:], desired_column_indices) for result in results]

    column_names = _get_column_names_from_required_columns(required_columns)

    return results_subset, required_columns
