# has pepsi 2012-2014: http://itiming.com/searchable/index.php?results=pepsi2014
# a follow on scraper for chronotrack could be used to scrape a TON of large / midsized races:
# http://www.itiming.com/html/raceresults.php?year=2014&EventId=99999&eventype=6
# the value added is high
# their result request looks like a nightmare:
# https://results.chronotrack.com/embed/results/results-grid?callback=results_grid4044366&sEcho=3&iColumns=11&sColumns=&iDisplayStart=0&iDisplayLength=15&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&mDataProp_8=8&mDataProp_9=9&mDataProp_10=10&raceID=14105&bracketID=138383&intervalID=22769&entryID=&eventID=6717&eventTag=event-6717&oemID=www.chronotrack.com&genID=4044366&x=1547015252568&_=1547015252569
# but can be boiled down to something exceptionally simpler:
# https://results.chronotrack.com/embed/results/results-grid?callback=no&iDisplayStart=0&iDisplayLength=1000&raceID=14105&eventID=6717
# where the eventId can be grabbed out of the itiming url, and the raceId from:
# https://results.chronotrack.com/embed/results/load-model?callback=no&modelID=event&eventID=6717
# there's a bunch of crap, but it provides a clean json object "race" with keys being the race ids
from enum import Enum
import re
import json
import requests

from bs4 import BeautifulSoup
import pandas as pd

ITIMING_LIST_PAGE_FORMAT = "http://www.itiming.com/html/raceresults.php?year=%d&EventId=99999&eventype=6"
CHRONOTRACK_EVENT_FORMAT = "https://results.chronotrack.com/embed/results/load-model?callback=no&modelID=event&eventID=%d"
CHRONOTRACK_RESULTS_FORMAT = "https://results.chronotrack.com/embed/results/results-grid?callback=no&iDisplayStart=0&iDisplayLength=5000&raceID=%d&eventID=%d"
ITIMING_RESULTS_FORMAT = "http://itiming.com/searchable/index.php?results=%s"

SCRAPABLE_ITIMING_REGEX = r'http://itiming.com/searchable/index.php\?results=(.*)$'
SCRAPABLE_CHRONOTRACK_REGEX = r'https://results.chronotrack.com/event/results/event/event\-([0-9]+)/?$'

STORAGE_DIRECTORY = '/Users/kholub/birkielo/offline/data/'

def extract_event_details(event_html):
    # the first anchor link is *always* the clickable event image - the second is the event name
    anchors = event_html.find_all('a')
    if len(anchors) < 2:
        raise ValueError('Could not extract event name')
    event_name = anchors[1].text

    date_tr = event_html.find_all('tr', {"id": "date"})
    if len(date_tr) < 1:
        raise ValueError('Could not extract event date')
    event_date = date_tr[0].find_all('td')[0].text

    results_link_tds = event_html.find_all('td', {"class": "ResultsLink"})
    if len(results_link_tds) < 1:
        raise ValueError('Could not extract results table data')
    results_urls = []
    for rlt in results_link_tds:
        anchor = rlt.find_all('a')
        if not anchor:
            raise ValueError('Could not extract results url')
        results_urls.append(anchor[0]['href'])

    return event_name, event_date, results_urls


def scrape_chronotrack_results(event_id,
                             result_columns = ('uid', 'place', 'name', 'bib', 'time', 'pace', 'location', 'age',
                                               'gender', 'age_group', 'age_group_place')):
    event_res = requests.get(CHRONOTRACK_EVENT_FORMAT % (event_id,))
    match = re.search(r'no\((.*)\);$', event_res.text)
    if not match:
        raise ValueError('Unable to extract chronotrack json payload')
    json_payload = json.loads(match.group(1))

    if 'model' not in json_payload or 'races' not in json_payload['model']:
        raise ValueError('Unable to extract race data from event json')

    race_id_to_name = {int(race_id):race_details['name']
                       for race_id, race_details in json_payload['model']['races'].items() if 'name' in race_details}

    results = pd.DataFrame()
    for race_id, race_name in race_id_to_name.items():
        race_res = requests.get(CHRONOTRACK_RESULTS_FORMAT % (race_id, event_id))

        chrono_match = re.search(r'no\((.*)\);$', race_res.text)
        if not chrono_match:
            raise ValueError('Unable to extract chronotrack json payload')
        json_payload = json.loads(chrono_match.group(1))

        # alcoholics anonymous data?
        if not 'aaData' in json_payload:
            raise ValueError('Unable to query race result data')

        results_tuples = json_payload['aaData']
        part_results = pd.DataFrame(results_tuples, columns=result_columns)
        part_results['race_name'] = race_name

        results = results.append(part_results)

    return results


def _get_itiming_results(event_key):
    event_url = ITIMING_RESULTS_FORMAT % (event_key)
    results = pd.DataFrame()
    total_requests = 0
    # itiming allows 100 results at a time, unconfigurable
    # we expect no more than 5K results per race on itiming, so limit to 50 requests in case of error
    while total_requests < 50:
        total_requests += 1
        number_of_results = results.shape[0]
        res = requests.post(event_url, data={"limit": number_of_results})
        soup = BeautifulSoup(res.content)
        tables = soup.find_all('table')
        # TODO none of the tables are labelled, but this page appears very static
        if len(tables) == 7:
            result_table_html = tables[6]
            part_results = pd.read_html(str(result_table_html))[0]
            # the headers are given as standard td tags :/
            part_results_columns = list(part_results.iloc[1])
            part_results_valid = part_results.iloc[2:]
            part_results_valid.columns = part_results_columns

            if not part_results_valid.shape[0]:
                break
            if part_results_valid.shape[0] == 1 and part_results_valid.iloc[0]["Bib #"] == 'No Results Found!':
                break
            results = results.append(part_results_valid)
        else:
            break

    return results


class ResultSource(Enum):
    Itiming = "itiming"
    Chrono = "chrono"


def get_all_results_for_event(event):
    event_name, event_date, urls = event

    for url in urls:
        chronotrack_match = re.search(SCRAPABLE_CHRONOTRACK_REGEX, url)
        if chronotrack_match:
            event_id = int(chronotrack_match.group(1))
            results = scrape_chronotrack_results(event_id)
            results['event_name'] = event_name
            results['event_date'] = event_date

            # note - it is assumed there is only 1 scrapable url per race. this appears to be generally true
            # with some exceptions - e.g. junior olympics 2006
            return ResultSource.Chrono, results
        else:
            itiming_match = re.search(SCRAPABLE_ITIMING_REGEX, url)
            if itiming_match:
                event_key = itiming_match.group(1)
                results = _get_itiming_results(event_key)
                results['event_name'] = event_name
                results['event_date'] = event_date

                return ResultSource.Itiming, results

    return None


##########################
## start control flow
##########################

if __name__ == "main":
    # 2006 is the first year of non-pdf results
    all_years_results = []
    for year in range(2006, 2019):
        list_page_url = ITIMING_LIST_PAGE_FORMAT % (year,)
        res = requests.get(list_page_url)
        soup = BeautifulSoup(res.content, 'lxml')
        events_html = soup.find_all('table', {"id": "resultstable"})

        all_event_details = [extract_event_details(eh) for eh in events_html]
        all_results = [get_all_results_for_event(event) for event in all_event_details]

        all_years_results += all_results

    itiming_results = pd.DataFrame()
    chrono_results = pd.DataFrame()
    for source, event_results in [r for r in all_years_results if r]:
        if source == ResultSource.Chrono:
            chrono_results = chrono_results.append(event_results)
        else:
            itiming_results = itiming_results.append(event_results)


    chrono_results.to_csv(STORAGE_DIRECTORY + "/chronotrack_results.csv")
    itiming_results.to_csv(STORAGE_DIRECTORY + "/itiming_results.csv")