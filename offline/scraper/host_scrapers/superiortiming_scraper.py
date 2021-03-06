import requests
from bs4 import BeautifulSoup
import pandas as pd

from host_scrapers.myraceresults_scraper import get_mrr_races
from host_scrapers.myraceresults_scraper import get_mrr_results

STORAGE_DIRECTORY = '/Users/kholub/birkielo/offline/data/'


def any_contains(target, keys):
    return any([key.lower() in target.lower() for key in keys])


def get_all_st_events(discipline='Nordic Skiing',
                         race_keys=['bear', 'pepsi', 'seeley', 'noquemanon']):
    form_data = {
        "action": "getResults",
        "raceDiscipline": discipline
    }

    res = requests.post('http://www.superiortiming.com/wp-admin/admin-ajax.php', form_data)
    soup = BeautifulSoup(res.content,'lxml')
    table_rows = soup.find_all('tr')

    events = []
    for row in table_rows:
        data = row.find_all('td')
        if len(data) < 2:
            continue
        event = data[0]
        anchor = event.find_all('a')[0]
        st_event_url = anchor['href']
        event_name = anchor.contents[0].strip()
        date_data = data[1]
        event_date = date_data.contents[0].strip()

        if any_contains(event_name, race_keys) and not 'text message' in event_name.lower():
            events.append((st_event_url, event_name, event_date))

    return events


# not "my" race results, but "my race results"
def get_mrr_urls(st_urls,
                 link_keys=['searchable results', 'live results',
                            'noquemanon results', 'great bear chase results']):
    my_race_results_urls = []
    followable_indices = []
    for ix,url in enumerate(st_urls):
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        anchors = soup.find_all('a')
        results_url = [a['href'] for a in anchors if len(a.contents) and any_contains(str(a.contents[0]), link_keys)]

        if len(results_url):
            # to avoid fussing with redirects later
            my_race_results_urls.append(results_url[0].replace("http://", "https://"))
            followable_indices.append(ix)
        else:
            print("Found no mrr url at st url: %s" % (url,))

    return my_race_results_urls, followable_indices


def get_all_results(events):
    all_results = pd.DataFrame()
    for event_url, event_name, event_date in events:
        event_data_list = get_mrr_races(event_url)

        if not event_data_list:
            print('Failed to handle event at: ' + event_name)
            continue

        for contest_number, list_name, race_name, event_id, event_key in event_data_list:

            race_results, column_names = get_mrr_results(event_id, event_key, list_name, contest_number)
            if race_results:
                results_df = pd.DataFrame(race_results, columns=column_names)
                results_df['date'] = event_date
                results_df['event'] = event_name
                results_df['race'] = race_name

                all_results = all_results.append(results_df)
            else:
                print("Failed to handle race: " + race_name + " " + event_name)
    return all_results

###########################
## start control flow
###########################
if __name__ == '__main__':
    st_events = get_all_st_events()
    st_event_urls = [e[0] for e in st_events]

    mrr_urls, original_indices = get_mrr_urls(st_event_urls)
    st_events_followable = [st_events[ix] for ix in original_indices]

    # list of tuples: mrr url, event name, event date
    events = [(e[1], e[0][1], e[0][2]) for e in zip(st_events_followable, mrr_urls)]

    results = get_all_results(events)
    results.to_csv(STORAGE_DIRECTORY + "mrr_raw.csv")
    # TODO handle the following failures:
    # Failed to handle event at: https://www.superiortiming.com/2013/01/noquemanon-ski-marathon-2013-live-results/
    # Failed to handle event at: https://my3.raceresult.com/details/index.php?eventid=10035
    # Failed to handle event at: https://my2.raceresult.com/details/index.php?eventid=9194&lang=en