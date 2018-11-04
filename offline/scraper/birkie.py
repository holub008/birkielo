import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from bs4 import BeautifulSoup
import time
from sqlalchemy import create_engine

def insert_to_db(table_name, data):
    url_format = 'postgresql://{}:{}@{}:{}/{}'
    #TODO!
    url = url_format % (user, password, host, port, db)
    engine = create_engine(url)

    data.to_sql(table_name, engine)

# since we like the birkie, avoid straining their systems as we pull data
TIME_BETWEEN_REQUESTS = 20
MAX_RESPONSE_TIME = 10 # very generous - sometimes birkie site can be slow
RESULTS_URL_FORMAT = "http://results.birkie.com/index.php?page_number=%d&test=1"
INDIVIDUAL_YEAR_URL_FORMAT = "http://birkie.pttiming.com/results/%d/index.php?pageNum_rsOverall=%d&totalRows_rsOverall=3836&page=1150&r_page=division&divID=%d"

def get_2007_to_2015_results():
    current_page = 1
    total_results = pd.DataFrame()
    while True:
        res = requests.get(RESULTS_URL_FORMAT % (current_page,), timeout=MAX_RESPONSE_TIME)
        soup = BeautifulSoup(res.content,'lxml')
        tables = soup.find_all('table')
        df = pd.read_html(str(tables[2]))[0]
        if df.shape[0] < 4:
            break
        else:
            # first, the 2nd row contains the true column metadata
            column_names = df.loc[[1]].values[0].tolist()
            df.columns = column_names
            # next, we know that the first two columns and last column are garbage
            results = df.loc[2:][:-1]
            total_results = total_results.append(results)
            time.sleep(TIME_BETWEEN_REQUESTS)
            current_page += 1

    total_results.to_csv('~/birkie2007to2015.csv')

    return total_results

def get_2016_on_results(year,
                        max_division_id = 5):
    current_page = 1
    total_results = pd.DataFrame()
    for division_id in range(1, max_division_id+1):
        while True:
            res = requests.get(INDIVIDUAL_YEAR_URL_FORMAT % (year, current_page, division_id), timeout=MAX_RESPONSE_TIME)
            soup = BeautifulSoup(res.content,'lxml')
            tables = soup.find_all('table')
            df = pd.read_html(str(tables[3]))[0]
            if df.shape[0] < 4:
                break
            else:
                # first, the 2nd row contains the true column metadata
                column_names = df.loc[[1]].values[0].tolist()
                df.columns = column_names
                # next, we know that the first two columns and last column are garbage
                results = df.loc[2:][:-1]
                total_results = total_results.append(results)
                time.sleep(TIME_BETWEEN_REQUESTS)
                current_page += 1
    total_results.to_csv('~/birkie' + str(year) + ".csv")
    return(total_results)


results_2007 = get_2007_to_2015_results()
results_2016 = get_2016_on_results(2016)
results_2018 = get_2016_on_results(2018)

all_results = pd.concat([results_2007, results_2016, results_2018])