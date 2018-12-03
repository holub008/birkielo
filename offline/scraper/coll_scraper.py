import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

import race_record_committer as rrc
from db import get_connection

# URL for getting all race years & ids
DATE_LIST_URL = "https://www.mtecresults.com/race/show/245/"
RACE_PAGE_URL_FORMAT = "https://www.mtecresults.com/race/show/%d/"
# note that 1. version is a ridiculous parameter that serves no purpose 2. offset starts from 0
# 3. perPage is hardcoded to 50 anything else (including UI selections) causes 500s
RACE_RESULT_URL_FORMAT = "https://www.mtecresults.com/race/quickResults?raceid=%d&version=%d&overall=yes&offset=%d&perPage=50"


def extract_race_id_from_url(url):
    matches = re.search(r'/race/show/([0-9]+)', url)
    if matches:
        return int(matches.group(1))
    else:
        raise ValueError('Supplied url does not have expected structure')


# returns None if the event shouldn't / can't be scraped
def extract_discpline_from_race_name(race_name):
    race_name_lower = race_name.lower()
    if 'skate' in race_name_lower or 'free' in race_name_lower:
        return 'freestyle'
    elif 'classic' in race_name_lower:
        return 'classic'
    else:
        return None


def extract_date_from_soup(soup):
    matches = re.findall(r'[0-9]+/[0-9]+/[0-9]+', soup, re.MULTILINE)
    if matches:
        return matches[0]
    else:
        return None


def extract_distance_from_span(span):
    matches = re.search(r'[0-9\\.]+', span)
    if matches:
        return float(matches.group())
    else:
        return None


def get_occurrences_to_parent_race_ids():
    res = requests.get(DATE_LIST_URL)
    soup = BeautifulSoup(res.content, 'lxml')

    all_lists = soup.find_all('ul')
    year_list = all_lists[6]
    occurrence_to_parent_ids = [(a.text, extract_race_id_from_url(a['href'])) for a in year_list.find_all('a')]
    # since this is our entry point, manually add in
    occurrence_to_parent_ids.append(('2011', '245'))

    return occurrence_to_parent_ids


# since a parent occurrence is only one race among the occurrence, expand to all races
def expand_children_occurrences(occurrence_to_race_ids):
    all_races = []
    for occurrence_to_race_id in occurrence_to_race_ids:
        year = int(occurrence_to_race_id[0])
        race_id = int(occurrence_to_race_id[1])

        race_page_url = RACE_PAGE_URL_FORMAT % (race_id,)
        res = requests.get(race_page_url)
        soup = BeautifulSoup(res.content, 'lxml')

        occurrence_dates = [extract_date_from_soup(str(div)) for div in soup.find_all('div') if extract_date_from_soup(str(div))]
        occurrence_date = occurrence_dates[0]  # eff it, it's late

        # more late night eff it, since the page format seems to change on the early years & nothing has an id
        if year >= 2014:
            child_races = soup.find_all('li')[8].find_all('a')
        elif year == 2011:
            child_races = soup.find_all('li')[32].find_all('a')
        elif year == 2012:
            child_races = soup.find_all('li')[31].find_all('a')
        elif year == 2013:
            child_races = soup.find_all('li')[30].find_all('a')

        child_races_parsed = [(occurrence_date,
                             extract_race_id_from_url(a['href']),
                             extract_discpline_from_race_name(a.text)) for a in child_races
                            if extract_discpline_from_race_name(a.text)]
        all_races = all_races + child_races_parsed

    return all_races


def extract_version_id_from_soup(soup):
    anchors = soup.find_all('a')

    if len(anchors) > 0:
        for anchor in anchors:
            spans = anchor.find_all('span')
            if len(spans) > 0 and spans[0].text.lower().strip() == 'overall results':
                results_href = anchor['href']
                matches = re.search(r'version=([0-9]+)', results_href)
                if matches:
                    return int(matches.group(1))

    return None


def attach_race_distances_and_version_ids(race_tuples):
    all_races = []
    for date, race_id, discipline in race_tuples:
        race_page_url = RACE_PAGE_URL_FORMAT % (race_id,)
        res = requests.get(race_page_url)
        soup = BeautifulSoup(res.content, 'lxml')

        candidate_spans = soup.find_all('span', class_='raceinfotexthigher')
        if len(candidate_spans) == 0:
            continue
        distance_span = candidate_spans[0]
        distance_kilometers = extract_distance_from_span(distance_span.text)

        version_id = extract_version_id_from_soup(soup)
        if not version_id:
            continue

        all_races.append((date, race_id, version_id, discipline, distance_kilometers))

    return all_races


def get_race_results(races):
    results = pd.DataFrame()
    for index, race in races.iterrows():
        # this a safety check (as opposed to while True) in case unexpected behavior occurs - prevent hammering the site
        # we don't expected to scrape more than 5K results from an individual race on mtec
        total_requests = 0
        while total_requests < 5000 / 50:
            offset = total_requests * 50
            url = RACE_RESULT_URL_FORMAT % (race.mtec_race_id, race.mtec_version_id, offset)
            res = requests.get(url)  # requests automatically handles the compressed response for us :)
            soup = BeautifulSoup(res.content, 'lxml')

            tables = soup.find_all('table')

            if len(tables) > 1:
                results_table = tables[1]
                # gosh this is awesome. it even reads in the headers as col names
                partial_results = pd.read_html(str(results_table))[0]
                partial_results['mtec_race_id'] = race.mtec_race_id

                if partial_results.shape[1] > 0:
                    results = results.append(partial_results, sort=False)
                else:
                    break  # there must be no results left for this race
            else:
                break

            total_requests += 1

    return results


########################
## start control flow
########################

occurrence_to_race_ids = get_occurrences_to_parent_race_ids()
all_races = expand_children_occurrences(occurrence_to_race_ids)
all_races = attach_race_distances_and_version_ids(all_races)

races_data_frame = pd.DataFrame(all_races)
races_data_frame.columns = ['date', 'mtec_race_id', 'mtec_version_id', 'discipline', 'distance']

races_data_frame['date'] = pd.to_datetime(races_data_frame.date, format='%m/%d/%Y')

races_data_frame.to_csv('/Users/kholub/coll_races.csv')

race_results = get_race_results(races_data_frame)

con = None
try:
    con = get_connection()
    cursor = con.cursor()

    event_inserted = rrc.insert_and_get_events(cursor, pd.DataFrame([{"name":"City of Lakes Loppet"}]))
    event_occurrences = races_data_frame.drop_duplicates(['date'])
    event_occurrences['event_id'] = event_inserted.id[0]
    event_occurrences_inserted = rrc.insert_and_get_event_occurrences(cursor, event_occurrences)

    event_occurrences_inserted['date'] = pd.to_datetime(event_occurrences_inserted.date)
    races_for_insert = races_data_frame.merge(event_occurrences_inserted, how='inner', on=['date'])
    races_for_insert['event_occurrence_id'] = races_for_insert.id
    races_inserted = rrc.insert_and_get_races(cursor, races_for_insert)

    con.commit()
    cursor.close()
finally:
    if con is not None:
        con.rollback()
        con.close()
