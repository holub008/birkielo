import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

from scraper.result_parsing_utils import extract_discipline_from_race_name

STORAGE_DIRECTORY = '/Users/kholub/birkielo/offline/data/'

# URL for getting all race years & ids
EVENT_PAGE_URL_FORMAT = "https://www.mtecresults.com/event/show/%d/"
RACE_PAGE_URL_FORMAT = "https://www.mtecresults.com/race/show/%d/"
# note that 1. version is a ridiculous parameter that serves no purpose 2. offset starts from 0
# 3. perPage is hardcoded to 50 anything else (including UI selections) causes 500s
RACE_RESULT_URL_FORMAT = "https://www.mtecresults.com/race/quickResults?raceid=%d&version=%d&overall=yes&offset=%d&perPage=50"


def extract_event_id_from_url(url):
    matches = re.search(r'/event/show/([0-9]+)', url)
    if matches:
        return int(matches.group(1))
    else:
        raise ValueError('Supplied url does not have expected structure')


def extract_race_id_from_url(url):
    matches = re.search(r'/race/show/([0-9]+)', url)
    if matches:
        return int(matches.group(1))
    else:
        raise ValueError('Supplied url does not have expected structure')


def _extract_discipline_from_race_name(race_name):
    race_name_lower = race_name.lower()
    if 'skate' in race_name_lower or 'free' in race_name_lower:
        return 'freestyle'
    elif 'classic' in race_name_lower or 'class...' in race_name_lower:
        return 'classic'
    elif 'pursuit' in race_name_lower:
        return 'pursuit'
    else:
        raise ValueError('Could not determine discipline of race from name: ' + race_name)


def _parse_result_div(result_div):
    return [d.find('a').text for d in result_div.find_all('div', {'class': 'runnersearch-cell'})]


def _parse_results_div_table(parent_div):
    header_div = parent_div.find('div', {'class': 'runnersearch-header-row'})
    headers = [d.text for d in header_div.find_all('div', {'class': 'runnersearch-header-cell'})]

    results_list = [_parse_result_div(result_div)
                    for result_div in parent_div.find_all('div', {'class': 'runnersearch-row'})]

    return pd.DataFrame(results_list, columns=headers)


def _search_year_list(lists):
    for li in lists:
        if li.find_all('a', {"class": "breadcrumb__toggle"}):
            return li
    raise ValueError('input list of li elements does not contain expected structure for finding year list')


def _extract_date_from_arbitrary_text(text):
    return re.findall(r'[0-9]+/[0-9]+/[0-9]+', text, re.MULTILINE)


def _extract_occurrence_date_from_event_page(soup):
    divs = soup.find_all('div', {"class": "raceinfobox box-shadow"})
    candidate_dates = [date for div in divs for date in _extract_date_from_arbitrary_text(div.text)]

    event_date = ""
    if len(candidate_dates):
        if len(candidate_dates) > 1:
            print('Warning: multiple candidates dates for event found - using first recovered date in html document')
        event_date = candidate_dates[0]
    else:
        raise ValueError('Could not find any event dates matching expected format and structure')

    return event_date


def extract_placement(placement):
    matches = re.search(r'([0-9]+) / [0-9]+', placement)
    if matches:
        return matches.group(1)
    else:
        raise ValueError('Unexpected mtec race placement: "%s"' % (placement, ))


def get_occurrences_to_event_ids(base_event_id):
    res = requests.get(EVENT_PAGE_URL_FORMAT % (base_event_id,))
    soup = BeautifulSoup(res.content, 'lxml')

    all_lists = soup.find_all('li')
    year_list = _search_year_list(all_lists)
    occurrence_to_parent_ids = [(int(a.text.strip()), extract_event_id_from_url(a['href']))
                                for a in year_list.find_all('a')]

    return occurrence_to_parent_ids


# since a parent occurrence is only one race among the occurrence, expand to all races
def expand_event_to_races(event_ids,
                          occurrence_date=None):
    all_races = []
    for event_id in event_ids:
        event_page_url = EVENT_PAGE_URL_FORMAT % (event_id,)
        res = requests.get(event_page_url)
        soup = BeautifulSoup(res.content, 'lxml')

        if not occurrence_date:
            occurrence_date = _extract_occurrence_date_from_event_page(soup)

        divs = soup.find_all('div')
        for div in divs:
            child_anchors = div.find_all('a')
            if child_anchors:
                hit_event_div = False
                for ca in child_anchors:
                    child_divs = ca.find_all('div', {"class": "box-shadow"})
                    if child_divs:
                        hit_event_div = True
                        race_name_headers = child_divs[0].find_all(re.compile('^h[1-6]$'))
                        if race_name_headers:
                            race_name = race_name_headers[0].text.strip()
                            race_id = extract_race_id_from_url(ca['href'])

                            all_races.append((
                                race_name,
                                occurrence_date,
                                race_id))
                if hit_event_div:
                    # avoid repeatedly hitting divs
                    break

    return all_races


# this adds in "version" - a seemingly pointless but required parameter, distance, & discipline
# additionally, thin down the results pages to only those including structured results
def attach_race_metadata_and_filter_structured(all_races, fallback_discipline=None):
    races_with_metadata = []
    for race in all_races:
        race_name = race[0]
        occurrence_date = race[1]
        race_id = race[2]

        res = requests.get(RACE_PAGE_URL_FORMAT % (race_id,))
        soup = BeautifulSoup(res.content, 'lxml')
        menu_div = soup.find_all('div', {"id": "minimenu"})

        race_version = -1
        if menu_div:
            results_anchor = menu_div[0].find_all('a')
            if results_anchor:
                results_url = results_anchor[0]['href']
                matches = re.search(r'version=([0-9]+)', results_url)
                if matches:
                    race_version = int(matches.group(1))
                else:
                    raise ValueError('Race page or result link does not have expected structure')
            else:
                raise ValueError('Race page or result link does not have expected structure')
        else:
            raise ValueError('Race page or result link does not have expected structure')

        spans = soup.find_all('span', {"class":"raceinfotexthigher"})
        if spans:
            distance_span = [span for span in spans if ('KIL' in span.text or 'kil' in span.text)]
            if distance_span:
                matches = re.search(r'^([0-9]+(\.[0-9]+?))+ ?K', distance_span[0].text)
                if matches:
                    distance_meters = float(matches.group(1)) * 1000
                else:
                    raise ValueError('Race page or distance does not have expected structure')
            else:
                raise ValueError('Race page or distance does not have expected structure')
        else:
            # this div not being present is an indicator that it's a text result summary - not structured results
            continue

        discipline = extract_discipline_from_race_name(race_name)
        if not discipline:
            page_title = soup.find('title').text
            # this is pretty hacky, but mte seems to do this with
            discipline = extract_discipline_from_race_name(page_title)
        if not discipline:
            if fallback_discipline:
                discipline = fallback_discipline
            else:
                print("skipping race with no identifiable discpline: '%s'" % (race_name, ))
                continue


        races_with_metadata.append((occurrence_date, distance_meters, discipline, race_id, race_version))

    return races_with_metadata


def get_race_results(races):
    results = pd.DataFrame()
    for date, distance, discipline, race_id, version in races:
        # this a safety check (as opposed to while True) in case unexpected behavior occurs - prevent hammering the site
        # we don't expected to scrape more than 5K results from an individual race on mtec
        total_requests = 0
        while total_requests < 5000 / 50:
            offset = total_requests * 50
            url = RACE_RESULT_URL_FORMAT % (race_id, version, offset)
            res = requests.get(url)  # requests automatically handles the compressed response for us :)
            soup = BeautifulSoup(res.content, 'lxml')

            table = soup.find('div', {'class': 'runnersearch'})

            if table:
                partial_results = _parse_results_div_table(table)
                partial_results['mtec_race_id'] = race_id
                partial_results['date'] = date
                partial_results['distance_meters'] = distance
                partial_results['discipline'] = discipline

                if partial_results.shape[0] > 0:
                    results = results.append(partial_results, sort=False)
                else:
                    break  # there must be no results left for this race
            else:
                break

            total_requests += 1

    return results


if __name__ == '__main__':
    # 4 years of vasaloppet: https://www.mtecresults.com/race/show/251/
    # 6 years of marine o'brien: https://www.mtecresults.com/event/show/208/
    events ={'Vasaloppet USA': 82, "Marine O'Brien": 208}

    final_results = {}
    for event_name, event_id in events.items():
        occurrence_to_event_ids = get_occurrences_to_event_ids(event_id)
        event_ids = [ey[1] for ey in occurrence_to_event_ids]
        all_races = expand_event_to_races(event_ids)
        races_with_metadata = attach_race_metadata_and_filter_structured(all_races)
        results = get_race_results(races_with_metadata)
        final_results[event_name] = results

    for event_name,results in final_results.items():
        results.to_csv(STORAGE_DIRECTORY + event_name + "_raw.csv")