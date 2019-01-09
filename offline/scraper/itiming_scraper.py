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

import requests
from bs4 import BeautifulSoup

##########################
## start control flow
##########################
ITIMING_LIST_PAGE_FORMAT = "http://www.itiming.com/html/raceresults.php?year=%d&EventId=99999&eventype=6"


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


# 2006 is the first year of non-pdf results
for year in range(2006, 2019):
    list_page_url = ITIMING_LIST_PAGE_FORMAT % (year,)
    res = requests.get(list_page_url)
    soup = BeautifulSoup(res.content, 'lxml')
    events_html = soup.find_all('table', {"id": "resultstable"})

    all_event_details = [extract_event_details(eh) for eh in events_html]