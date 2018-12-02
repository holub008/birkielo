import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# since we like the birkie, avoid straining their systems as we pull data
TIME_BETWEEN_REQUESTS = 10
MAX_RESPONSE_TIME = 10 # very generous - sometimes birkie site can be slow
STORAGE_DIRECTORY = '/Users/kholub/birkielo/offline/data/'
URL_FORMAT_2007 = "http://results.birkie.com/index.php?page_number=%d&test=1"
URL_FORMAT_2016 = "http://birkie.pttiming.com/results/%d/index.php?pageNum_rsOverall=%d&totalRows_rsOverall=3836&page=1150&r_page=division&divID=%d"
URL_FORMAT_2006 = "http://www.itiming.com/raceresults/2006birkie/gender.php?pageNum_rsOverall=%d&totalRows_rsOverall=692&EventID=%d&Gender=%s"

def get_2007_to_2015_results():
    current_page = 1
    total_results = pd.DataFrame()
    while True:
        res = requests.get(URL_FORMAT_2007 % (current_page,), timeout=MAX_RESPONSE_TIME)
        soup = BeautifulSoup(res.content,'lxml')
        tables = soup.find_all('table')
        # TODO: chase links to get gender
        # for now, we can hack-derive gender with high accuracy by lag-counting overall rank & gender rank
        # (of course, this is not a "correct" algorithm- it can fail under certain orderings)
        df = pd.read_html(str(tables[2]))[0]
        if df.shape[0] < 4:
            break
        else:
            # first, the 2nd row contains the true column metadata
            column_names = df.loc[[1]].values[0].tolist()
            df.columns = column_names
            # next, we know that the first two rows and last row are garbage
            results = df.loc[2:][:-1]
            total_results = total_results.append(results)
            time.sleep(TIME_BETWEEN_REQUESTS)
            current_page += 1
    total_results.to_csv(STORAGE_DIRECTORY + 'birkie2007to2015.csv')
    return total_results

def get_2016_on_results(year,
                        max_division_id = 5):
    total_results = pd.DataFrame()
    for division_id in range(1, max_division_id+1):
        current_page = 0 # note this is different from above
        while True:
            res = requests.get(URL_FORMAT_2016 % (year, current_page, division_id), timeout=MAX_RESPONSE_TIME)
            soup = BeautifulSoup(res.content,'lxml')
            tables = soup.find_all('table')
            results_table = tables[3]
            df = pd.read_html(str(results_table))[0]
            if df.shape[0] < 5: # unlike the other page, a dummy row NaN row is inserted if there are no results. this means we may throw out 1 legitimate result
                break
            else:
                # first, the 2nd row contains the true column metadata
                column_names = df.loc[[1]].values[0].tolist()
                df.columns = column_names
                # next, we know that the first two rows and last column are garbage
                results = df.loc[2:][:-1]
                # finally, since we don't have an event column
                event_name = results_table.find('th').find('div').string
                results['Event'] = event_name
                results['Year'] = year
                total_results = total_results.append(results)
                time.sleep(TIME_BETWEEN_REQUESTS)
                current_page += 1
    total_results.to_csv(STORAGE_DIRECTORY + 'birkie' + str(year) + ".csv")
    return total_results

def get_2006_results():
    total_results = pd.DataFrame()
    for event_id in [11000000, 12000000]:
        for gender in ['M', 'F']:
            current_page = 0
            while True:
                res = requests.get(URL_FORMAT_2006 % (current_page, event_id, gender), timeout=MAX_RESPONSE_TIME)
                soup = BeautifulSoup(res.content,'lxml')
                top_table = soup.find_all('table')[2]
                results_table = top_table.find_all('table')[5]
                df = pd.read_html(str(results_table))[0]
                event_name = df[0][1] # too lazy to figure out how to index pd df, this is column, row oriented
                if df.shape[0] < 7 or (df.shape[0] == 7 and any(df.loc[3].isnull())): # there's a dummy 4th row on empty pages
                    break
                else:
                    # first, the 3rd row contains the true column metadata
                    column_names = df.loc[[2]].values[0].tolist()
                    df.columns = column_names
                    # next, we know that the first three rows and last three are garbage
                    results = df.loc[3:][:-3]
                    # finally, since we don't have an event column
                    results['Event'] = event_name
                    results['Year'] = 2006
                    total_results = total_results.append(results)
                    time.sleep(TIME_BETWEEN_REQUESTS)
                    current_page += 1
    total_results.to_csv(STORAGE_DIRECTORY + 'birkie2006.csv')
    return total_results

def get_pdf_results(event_name_to_url = {
    "2005 Birkebeiner": "https://cdn.birkie.com/Results/2005/Birkie/birkie_overall_05.pdf",
    "2004 Birkebiener Women": "https://cdn.birkie.com/Results/2004/Birkie/b_f_gender_04.pdf",
    "2004 Birkebiener Men": "https://cdn.birkie.com/Results/2004/Birkie/b_m_gender_04.pdf",
    "2003 Birkebeiner Women": "https://cdn.birkie.com/Results/2003/Birkie/b_f_gender_03.pdf",
    "2003 Birkebeiner Men": "https://cdn.birkie.com/Results/2003/Birkie/b_m_gender_03.pdf",
    "2002 Birkebeiner Men": "https://cdn.birkie.com/Results/2002/Birkie/birkie_m_gender.pdf",
    "2002 Birkebeiner Women": "https://cdn.birkie.com/Results/2002/Birkie/birkie_f_gender.pdf",
    "2001 Birkebeiner Men": "https://cdn.birkie.com/Results/2001/Birkie/Abmen2001.pdf",
    "2001 Birkebeiner Women": "https://cdn.birkie.com/Results/2001/Birkie/Abfem2001.pdf",
    #2000 was a no snow year
    "1999 Birkebeiner Men": "https://cdn.birkie.com/Results/1999/Birkie/99bmen.pdf",
    "1999 Birkebeiner Women": "https://cdn.birkie.com/Results/1999/Birkie/99bfem.pdf"
}):
    for event, url in event_name_to_url.items():
        response = requests.get(url, stream=True)
        filename = STORAGE_DIRECTORY + event.replace(" ", "") + ".pdf"
        with open(filename, 'wb') as handle:
            for block in response.iter_content(2056):
                handle.write(block)

    # note that tabula provides excellent results for most documents
    # e.g. temp = read_pdf('/Users/kholub/birkielo/offline/data/2005Birkebeiner.pdf', pages = '2-5')
    # produces perfect results. however, some pages have extra data, which can cause problems
    # probably easiest to do this manually


results_2006 = get_2006_results()
results_2007 = get_2007_to_2015_results()
results_2016 = get_2016_on_results(2016)
results_2018 = get_2016_on_results(2018)

# 1999 - 2005 will require pdf parsing, which we'll look at later
get_pdf_results()