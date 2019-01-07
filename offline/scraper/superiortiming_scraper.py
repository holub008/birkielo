import requests
from bs4 import BeautifulSoup

def any_contains(target, keys):
    return any([key.lower() in target.lower() for key in keys])


def get_all_st_race_urls(discipline='Nordic Skiing',
                         race_keys=['bear', 'pepsi', 'seeley', 'noquemanon']):
    form_data = {
        "action": "getResults",
        "raceDiscipline": discipline
    }

    res = requests.post('http://www.superiortiming.com/wp-admin/admin-ajax.php', form_data)
    soup = BeautifulSoup(res.content,'lxml')
    anchors = soup.find_all('a')
    race_links = [(a['href'], a.contents[0]) for a in anchors]

    return [rl[0] for rl in race_links if any_contains(rl[1], race_keys) and not 'text message' in rl[1].lower()]


# not "my" race results, but "my race results"
def get_mrr_urls(st_urls,
                 link_keys=['searchable results', 'live results',
                            'noquemanon results', 'great bear chase results']):
    my_race_results_urls = []
    for url in st_urls:
        res = requests.get(url)
        soup = BeautifulSoup(res.content, 'lxml')
        anchors = soup.find_all('a')
        results_url = [a['href'] for a in anchors if len(a.contents) and (str(a.contents[0]), link_keys)]

        if len(results_url):
            # to avoid fussing with redirects later
            my_race_results_urls.append(results_url[0].replace("http://", "https://"))
        else:
            print("Found no mrr url at st url: %s" % (url,))

    return my_race_results_urls


###########################
## start control flow
###########################

st_urls = get_all_st_race_urls()
mrr_urls = get_mrr_urls(st_urls)
