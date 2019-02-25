# pick up latest years of vasaloppet, a few old marine o'brien runnings, 1 rennet, a few pre-loppets
# https://www.gopherstateevents.com/results/fitness_events/results.asp?event_type=46

import re
import requests
import json

from bs4 import BeautifulSoup
import pandas as pd

GS_LIST_PAGE = "https://www.gopherstateevents.com/results/fitness_events/results.asp?event_type=46"
GS_RESULTS_HOME_FORMAT = "https://www.gopherstateevents.com/results/fitness_events/results.asp?event_type=46&event_id=%d"
GS_RESULTS_FORMAT = "https://www.gopherstateevents.com/results/fitness_events/results_source.asp?race_id=%d&gender=B"

STORAGE_DIRECTORY = '/Users/kholub/birkielo/offline/data/'


def get_events():
    res = requests.get(GS_LIST_PAGE)
    soup = BeautifulSoup(res.content, features="lxml")
    selects = soup.find_all('select', {"id": "events"})
    if not selects or not len(selects) == 1:
        raise ValueError('Could not find expected event select list')

    options = selects[0].find_all('option')
    return [(int(o['value']), o.text) for o in options if o['value']]


def get_races_from_events(events):
    all_races = []
    for event_id, event_name in events:
        res = requests.get(GS_RESULTS_HOME_FORMAT % (event_id))
        soup = BeautifulSoup(res.content, features="lxml")

        selects = soup.find_all('select', {"id":"races"})
        if not selects:
            raise ValueError('Unable to find race selections')

        options = selects[0].find_all('option')
        if not options:
            raise ValueError('Unable to find race selection options')

        all_races += [(int(o['value']), o.text, event_id, event_name) for o in options]

    return all_races


def _get_anchor_content(html_content):
    soup = BeautifulSoup(html_content, features="lxml")
    anchors = soup.find_all('a')
    if not anchors:
        raise ValueError('Unexpected did not find anchor html')

    return anchors[0].text


def get_results_from_races(races):
    all_results = pd.DataFrame()
    for race_id, race_name, event_id, event_name in races:
        res = requests.get(GS_RESULTS_FORMAT % (race_id,))
        json_payload = json.loads(res.text)

        results_tuples_unparsed = json_payload['data']
        results_tuples = [r[0:2] + [_get_anchor_content(r[2])] + r[3:8] for r in results_tuples_unparsed]
        race_results = pd.DataFrame(results_tuples)
        race_results.columns = ['place', 'bib', 'first_name', 'last_name', 'gender', 'age', 'time', 'time2']
        race_results['race_name'] = race_name
        race_results['event_name'] = event_name

        all_results = all_results.append(race_results)

    return all_results

############################
## start control flow
############################
if __name__ == '__main__':
    events = get_events()
    races = get_races_from_events(events)
    results = get_results_from_races(races)

    # some running cruft making it in
    ski_results = results[~results.event_name.str.contains('Snow Shoe')]
    ski_results = ski_results[~ski_results.event_name.str.contains('Snowshoe')]
    ski_results = ski_results[~ski_results.event_name.str.contains('Snowshoe')]

    ski_results.to_csv(STORAGE_DIRECTORY + "gopher_state.csv")