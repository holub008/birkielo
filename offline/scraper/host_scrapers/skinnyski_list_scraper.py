import requests
import re
from datetime import datetime
import time

from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

import scraper.host_scrapers.onlineraceresults_scraper as orrs
from scraper.event_occurrence_arbiter import EventOccurrenceArbiter
from scraper.result_parsing_utils import extract_gender_from_age_group_string, extract_discipline_from_race_name, extract_distance_from_race_name

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
        time.sleep(5)
        print(event_occurrence)
        event_id = orrs.extract_event_id(event_occurrence.event_link)
        if event_id:
            races = orrs.get_races_for_event([(event_id, event_occurrence.event_date)])
        else:
            race_page_link = event_occurrence.event_link.replace('view_plain_text', 'view_race')
            events = orrs.get_events(race_page_url=race_page_link, event_date=event_occurrence.event_date)
            races = orrs.get_races_for_event(events)

        added_results = [orrs.get_results_for_race(r) for r in races]
        for r in added_results:
            r['event_name'] = event_occurrence.event_name_enum

        orr_results += added_results

    orr_results_df = pd.concat(orr_results)
    # we occassionally get a row of column headers & other cruft mixed in - clear it out
    orr_results_df = orr_results_df[orr_results_df['TIME'] != 'TIME']
    # who knows what these are :O
    orr_results_df = orr_results_df[(orr_results_df['LN'] != 'Not Found') & (orr_results_df['LN'] != 'Unknown') & (orr_results_df['FN'] != 'Unknown')]
    orr_results_df['DIVISION'] = orr_results_df['DIVISION'].astype('str')
    orr_results_df['gender'] = np.where(pd.isnull(orr_results_df['SEX']),
                                        [extract_gender_from_age_group_string(div) for div in orr_results_df['DIVISION']],
                                        ['male' if s == 'M' else 'female' for s in orr_results_df['SEX']])
    orr_results_df['discipline'] = [extract_discipline_from_race_name(rn) for rn in orr_results_df.race_name]
    orr_results_df['distance'] = [extract_distance_from_race_name(rn) for rn in orr_results_df.race_name]

    # LMAO, so I probably didn't even need a list page scraper here :/
    orr_event_overrides = pd.DataFrame({
        "event_name": ["Snowflake / Inga-lami", "Snowflake / Inga-lami", "City of Lakes Loppet",
                       "City of Lakes Loppet", "City of Lakes Loppet", "City of Lakes Loppet", "City of Lakes Loppet",
                       "City of Lakes Loppet", "City of Lakes Loppet", "City of Lakes Loppet",
                       "Governor's Cup", "Governor's Cup", "Governor's Cup", "Governor's Cup",
                       "Vasaloppet USA", "Vasaloppet USA", "Vasaloppet USA", "Vasaloppet USA",
                       "Pre-Loppet"
                        ],
        "event_date": ["2006-02-18", "2006-02-18", "2007-02-04",
                 "2007-02-04", "2008-02-03", "2009-02-01", "2010-02-07",
                 "2008-02-03", "2009-02-01", "2010-02-07",
                 "2009-01-24", "2009-01-24", "2008-01-26", "2007-03-03",
                 "2007-02-11", "2007-02-11", "2007-02-11", "2007-02-11",
                 "2010-01-09"
                 ],
        "race_name": ["Women's Race - Searchable", "Men's Race - Searchable", "Loppet Freestyle",
                      "Hoigaard's Classic", "Hoigaard's Classic", "Hoigaard's Classic", "Hoigaard's Classic",
                      "Freestyle Loppet", "City of Lakes Freestyle Loppet", "City of Lakes Freestyle Loppet",
                      "Freestyle Race Results", 'Classic Race Results', '25K Results', '25K Results',
                      "58km Searchable", "42km Searchable", "35km Searchable", "13km Searchable",
                      "15.5K Results"
                        ],
        "discipline": ['freestyle', 'freestyle', 'freestyle',
                       'classic', 'classic', 'classic', 'classic',
                       'freestyle', 'freestyle', 'freestyle',
                       'freestyle', 'classic', 'freestyle', 'freestyle',
                       'freestyle', 'classic', 'freestyle', 'freestyle',
                       'freestyle'
                       ],
        "distance": [10.0, 10.0, 35.0,
                     25.0, 25.0, 25.0, 25.0,
                     35.0, 35.0, 33.0,
                     25.0, 25.0, 25.0, 25.0,
                     58.0, 42.0, 35.0, 13.0,
                     15.5
                    ]
    })

    orr_results_temp = orr_results_df.copy()
    orr_results_temp['event_date'] = orr_results_temp.event_date.astype('str')
    orr_results_joined = orr_results_temp.merge(orr_event_overrides, how='inner',
                                              on=['event_name', 'event_date', 'race_name'], suffixes=['', '_overrides'])
    orr_results_joined['distance'] = np.where(pd.isnull(orr_results_joined.distance),
                                              orr_results_joined.distance_overrides,
                                              orr_results_joined.distance)
    orr_results_joined['discipline'] = np.where(pd.isnull(orr_results_joined.discipline),
                                              orr_results_joined.discipline_overrides,
                                              orr_results_joined.discipline)