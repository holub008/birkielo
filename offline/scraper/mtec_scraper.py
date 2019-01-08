import re
import pandas as pd
import requests
from bs4 import BeautifulSoup

# URL for getting all race years & ids
DATE_LIST_URL = "https://www.mtecresults.com/race/show/%d/"
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


def get_occurrences_to_parent_race_ids(event_id):
    res = requests.get(DATE_LIST_URL % (event_id,))
    soup = BeautifulSoup(res.content, 'lxml')

    all_lists = soup.find_all('ul')
    year_list = all_lists[6]
    occurrence_to_parent_ids = [(a.text, extract_race_id_from_url(a['href'])) for a in year_list.find_all('a')]

    return occurrence_to_parent_ids


#################################
## start control flow
#################################

# 4 years of vasaloppet: https://www.mtecresults.com/race/show/251/
# 6 years of marine o'brien: https://www.mtecresults.com/event/show/208/
event_ids ={'Vasaloppet USA': 251, "Marine O'Brien": 208}