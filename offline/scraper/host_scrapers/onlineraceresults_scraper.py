import requests
import re

from bs4 import BeautifulSoup
import pandas as pd

ORR_SEARCH_URL = "http://onlineraceresults.com/search/#results"
ORR_EVENT_FORMAT = "http://onlineraceresults.com/event/view_event.php?event_id=%d"

ORR_PRELOAD_URL = "http://onlineraceresults.com/race/view_race.php?race_id=%d&submit_action=select_result&order_by=default&group_by=default"
ORR_RESULTS_URL = "http://onlineraceresults.com/race/view_race.php?race_id=%d&relist_record_type=result&lower_bound=0&upper_bound=9999&use_previous_sql=1&group_by=default"

STORAGE_DIRECTORY = '/Users/kholub/birkielo/offline/data/'


def extract_event_id(content):
    match = re.search(r'/event/view_event.php\?event_id=([0-9]+)', content)
    if not match:
        return None

    return int(match.group(1))


# note, this does not fail on unexpected format
def _extract_race_id(race_url):
    match = re.search(r'/race/view_race.php\?race_id=([0-9]+)', race_url)
    if not match:
        return None

    return int(match.group(1))


def _extract_event_data(row):
    date_td = row.find_all('td', {"class": "two"})
    if not date_td:
        raise ValueError('Could not find expected search table rows')
    span = date_td[0].find_all('span')
    if not span:
        raise ValueError('Could not not find expected search table date span')
    event_date = span[0].text

    anchor = row.find_all('a')
    if not anchor:
        raise ValueError('Unable to find event link in search result row')
    event_id = extract_event_id(anchor[0]['href'])

    return event_id, event_date


def get_events(query=None, race_page_url=None, event_date=None):
    if race_page_url:
        res = requests.get(race_page_url)
        event_id = extract_event_id(res.text)

        return [(event_id, event_date)]

    elif query:
        res = requests.post(ORR_SEARCH_URL, data={"name": query})
        soup = BeautifulSoup(res.content, 'lxml')

        tables = soup.find_all('table', {"class":"search-results"})
        if not tables:
            raise ValueError('Could not find expected results table')

        rows = tables[0].find_all('tr')
        if len(rows) < 2:
            raise ValueError('Could not find expected results rows')

        return [_extract_event_data(row) for row in rows[1:]]
    else:
        raise ValueError('need to supply either a race url or query')


def _extract_race_details(anchor):
    url = anchor['href']
    race_id = _extract_race_id(url)
    return race_id, anchor.text


def get_races_for_event(events):
    all_races = []
    for event_id, event_date in events:
        event_url = ORR_EVENT_FORMAT % (event_id,)
        res = requests.get(event_url)
        soup = BeautifulSoup(res.content, 'lxml')

        races_div = soup.find_all('div', {"id": "orr-event-races"})
        if not races_div:
            raise ValueError("Failed to find race list for event")

        races = [(event_id, event_date) + _extract_race_details(a) for a in races_div[0].find_all('a')]
        all_races += races

    return [r for r in all_races if r[2]]


def get_results_for_race(race,
                         cookie_session_id = '1337hax'):
    # Today in WEBDEV 101, we study abuse of stateful services
    # 1. the view_race.php endpoint only allows a full results load if the endpoint has been previously
    #    hit by a submit_action=select_result request
    # 2. the view_race.php full result request will crap out if any other request to a different
    #    race occurs under the same PHPSESSID. this is presumably due to sql caching
    # 3. the use_previous_sql query parameter, which would ideally remove this statefulness, does not
    #
    # so, here we are, submitting 2 sequential requests under a session to pull results
    event_id, event_date, race_id, race_name = race

    cookie = {"PHPSESSID": cookie_session_id}
    requests.get(ORR_PRELOAD_URL % (race_id,), cookies=cookie)
    res = requests.get(ORR_RESULTS_URL % (race_id,), cookies=cookie)
    soup = BeautifulSoup(res.content, 'lxml')

    result_div = soup.find_all('div',{"id": "race-results-table"})
    if not result_div:
        raise ValueError('Could not find results table div')
    result_table = result_div[0].find_all('table')
    if not result_table:
        raise ValueError('Could not find results table')

    results_df = pd.read_html(str(result_table[0]))[0]
    results_df['event_date'] = event_date
    results_df['race_name'] = race_name

    return results_df

def attach_gender_from_sex_place(results):
    results.groupby(['race_name', 'event_name'])

######################
## start control flow
######################
if __name__ == '__main__':
    events = get_events(query='vasa')
    races = get_races_for_event(events)
    # it's a copy of 7216 for some reason
    races_deduped = [r for r in races if not r[2] == 7217]
    all_results = [get_results_for_race(r) for r in races_deduped]

    total_results = pd.DataFrame()
    for result in all_results:
        total_results = total_results.append(result)

    # remove dummy rows
    total_results_clean = total_results[total_results.TIME != 'TIME']
    total_results_clean = total_results_clean[['CITY', 'DIVISION', 'DIVPL', 'FN', 'LN', 'OVERALL', 'SEXPL', 'STATE',
                                               'TIME', 'event_date', 'race_name']]

    total_results_clean.to_csv(STORAGE_DIRECTORY + "vasa_pre2011.csv")
