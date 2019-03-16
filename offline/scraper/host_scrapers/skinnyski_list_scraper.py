import requests
import re

from bs4 import BeautifulSoup
import pandas as pd

SKINNYSKI_LIST_PAGE_URL = "https://www.skinnyski.com/racing/results/default.asp"


def _short_month_to_int_month(short_month):
    if short_month == 'nov':
        return 11
    elif short_month == 'dec':
        return 12
    elif short_month == 'jan':
        return 1
    elif short_month == 'feb':
        return 2
    elif short_month == 'mar':
        return 3
    elif short_month == 'apr':
        return 4
    elif short_month == 'may':
        return 5

def _parse_event_element(element, season_year):
    date_part = str(element.contents[0])
    if 'img' in date_part:
        # some events are labelled as new via an image - skip that descendant
        date_part = str(element.contents[1])
    event_anchor = element.find_all('a')[0]

    date_matches = re.search(r'([A-Z][a-z]{2})\.([0-9]+)', date_part)
    if not date_matches:
        raise ValueError('Unable to extract date from: %s' % (date_part, ))

    short_month = date_matches.group(1).lower()
    day = int(date_matches.group(2))
    event_year = season_year
    if short_month not in ('nov', 'dec'):
        event_year -= 1

    event_date = "%d-%02d-%02d" % (event_year, _short_month_to_int_month(short_month), day)
    event_name = event_anchor.text
    event_link = event_anchor['href']

    return event_date, event_name, event_link


def get_all_result_links(year,
                         category=103): # 103 is citizen
        if year > 2003:
            post_data = {
                "cat": category,
                "season": year,
                "Submit": "Go"}
            resp = requests.post(SKINNYSKI_LIST_PAGE_URL, post_data)
            soup = BeautifulSoup(resp.text, 'lxml')
            event_list = soup.find_all('ul')[0]
            unparsed_events = event_list.find_all('li')
            parsed_events = [_parse_event_element(el, year) for el in unparsed_events]

            return pd.DataFrame(parsed_events, columns = ['event_date', 'event_name', 'event_link'])
        else:
            raise ValueError('Not yet equipped to handle years before 2004!')



if __name__ == '__main__':
    all_season_events = [get_all_result_links(y) for y in range(2004, 2019)]
    all_season_events_df = pd.concat(all_season_events)