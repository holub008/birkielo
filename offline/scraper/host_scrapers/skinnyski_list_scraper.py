import requests
import re
from datetime import datetime
import time

from bs4 import BeautifulSoup
import pandas as pd

from scraper.event_occurrence_arbiter import EventOccurrenceArbiter
from scraper.host_scrapers import mtec_scraper as mts, myraceresults_scraper as mrrs, onlineraceresults_scraper as orrs

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
        event_year += 1

    event_date = datetime(year=event_year, month=_short_month_to_int_month(short_month), day=day)
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

    occurrence_arbiter = EventOccurrenceArbiter()

    event_occurrences_for_scraping = pd.DataFrame()
    for index, candidate_event in all_season_events_df.iterrows():
        scrape_event = occurrence_arbiter.should_keep(candidate_event.event_name, candidate_event.event_date)
        if scrape_event:
            candidate_event['event_name_enum'] = occurrence_arbiter.enumerate_event_name(candidate_event.event_name)
            event_occurrences_for_scraping = event_occurrences_for_scraping.append(candidate_event)

    mtec_events = event_occurrences_for_scraping[event_occurrences_for_scraping.event_link.str.contains('mtecresults')]
    orr_events = event_occurrences_for_scraping[event_occurrences_for_scraping.event_link.str.contains('onlineraceresults')]
    mrr_events = event_occurrences_for_scraping[event_occurrences_for_scraping.event_link.str.contains('.raceresult.com')]
    # from manual inspection, all of these appear to be pdfs
    # itiming_results = event_occurrences_for_scraping[event_occurrences_for_scraping.event_link.str.contains('itiming')]

    orr_results = []
    for index, event_occurrence in orr_events.iterrows():
        time.sleep(1)
        event_id = orrs.extract_event_id(event_occurrence.event_link)
        if event_id:
            races = orrs.get_races_for_event([(event_id, event_occurrence.event_date)])
        else:
            race_page_link = event_occurrence.event_link.replace('view_plain_text', 'view_race')
            events = orrs.get_events(race_page_url=race_page_link, event_date=event_occurrence.event_date)
            races = orrs.get_races_for_event(events)

        orr_results += [orrs.get_results_for_race(r) for r in races]


    for index, mtec_event_occurrence in mtec_events.iterrows():
        event_id = mts.extract_race_id_from_url(mtec_event_occurrence.event_link)
        all_races = mts.expand_event_to_races([event_id])
        races_with_metadata = mts.attach_race_metadata_and_filter_structured(all_races)
        results = mts.get_race_results(races_with_metadata)
