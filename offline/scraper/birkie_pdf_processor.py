import tabula as tb
import re

STORAGE_DIRECTORY = '/Users/kholub/birkielo/offline/data/'

# pdfs for 99/01 the same format
results99m = tb.read_pdf(STORAGE_DIRECTORY + "1999BirkebeinerMen.pdf", pages="1-105", pandas_options={'header': None})
results99m.columns = ['rank_duration', 'bib_name', 'hometown', 'state', 'country', 'class', 'class_rank', '25_club']
results99f = tb.read_pdf(STORAGE_DIRECTORY + "1999BirkebeinerWomen.pdf", pages="all", pandas_options={'header': None})
results99f = results99f.iloc[2:]
results99f.columns = ['rank', 'duration', 'bib', 'name', 'hometown', 'state', 'country', 'class', 'class_rank',
                      '25_club', 'pace']
results01m = tb.read_pdf(STORAGE_DIRECTORY + "2001BirkebeinerMen.pdf", pages="all", pandas_options={'header': None})
results01m = results01m.iloc[1:]
results01m.columns = ['rank', 'duration', 'bib', 'name', 'hometown', 'state', 'country', 'class', 'class_rank',
                      '25_club', 'pace']
results01f = tb.read_pdf(STORAGE_DIRECTORY + "2001BirkebeinerWomen.pdf", pages="all", pandas_options={'header': None})
results01f = results01f.iloc[1:]
results01f.columns = ['rank', 'duration', 'bib', 'name', 'hometown', 'state', 'country', 'class', 'class_rank',
                      '25_club', 'pace']

# pdfs for 02/03/04 are the same format - first page parses differently from the remainders due to added text header
# note that it would be great to use the "area" argument of the read_pdf function, but it doesn't seem to work
def extract_location(cluster):
    matches = re.search(r'([a-zA-Z \-\\.]+,[a-zA-Z \-\\.]+, [a-zA-Z]+) ', cluster)
    if matches:
        return matches[0]
    return None


def extract_race_name(cluster):
    matches = re.search(r'.* (((Women\'s)|(Men\'s)) (Birkebeiner|Classic|Freestyle))', cluster)
    if matches:
        return matches[1]
    return None


def spread_first_page(first_page):
    first_page['gender_place'] = [int(x.split(" ")[1]) for x in first_page[0]]
    first_page['age_division_place'] = [x.split(" ")[2] for x in first_page[0]]
    first_page['name'] = [" ".join(x.split(" ")[4:]) for x in first_page[0]]
    first_page['location'] = [extract_location(x) for x in first_page[1]]
    first_page['race_name'] = [extract_race_name(x) for x in first_page[1]]

    return first_page

# TODO some name columns include the location
results02f_first = tb.read_pdf(STORAGE_DIRECTORY + "2002BirkebeinerWomen.pdf", pages="1",
                               pandas_options={'header': None})
results02f_first = spread_first_page(results02f_first.iloc[1:])
results02f_first = results02f_first.rename({3: "age", 4: "duration", 5: "pace"}, axis="columns")
results02f_first = results02f_first[['name', 'location', 'age', 'duration', 'gender_place', 'race_name']]
results02f_remainder = tb.read_pdf(STORAGE_DIRECTORY + "2002BirkebeinerWomen.pdf", pages="2-11",
                                   pandas_options={'header': None})
results02f_remainder['race_name'] = [extract_race_name(str(cluster)) for cluster in results02f_remainder[5]]
results02f_remainder['location'] = [extract_location(str(cluster)) for cluster in results02f_remainder[5]]
results02f_remainder.columns = ['discipline_blended_place', 'gender_place', 'age_group_place', 'bib', 'name',
                                'cluster', '_drop', 'age', 'duration', 'pace', 'race_name', 'location']
results02f = results02f_first.append(results02f_remainder[['name', 'location', 'age', 'duration', 'gender_place',
                                                           'race_name']])


def extract_name(cluster):
    matches = re.search(r'[0-9 ]+([a-zA-Z, \-\\.]+)$', cluster)
    if matches:
        return matches[1]
    return None

def extract_gender_placement(cluster):
    matches = re.search(r'^[0-9]+ ([0-9]+) ', cluster)
    if matches:
        return matches[1]
    return None

results02m_first = tb.read_pdf(STORAGE_DIRECTORY + "2002BirkebeinerMen.pdf", pages="1",
                               pandas_options={'header': None})
results02m_first = results02m_first.rename({1: 'location', 3: "race_name", 4: "age", 5: "duration"}, axis="columns")
results02m_first['name'] = [extract_name(cluster) for cluster in results02m_first[0]]
results02m_first['gender_place'] = [extract_gender_placement(cluster) for cluster in results02m_first[0]]
results02m_first = results02m_first[['name', 'location', 'age', 'duration', 'gender_place', 'race_name']]
results02m_first = results02m_first[results02m_first.name != 'Bank American Birkebeiner']
# TODO some name columns include the location
# TODO some of the race_names are bizarrely borked...
results02m_remainder = tb.read_pdf(STORAGE_DIRECTORY + "2002BirkebeinerMen.pdf", pages="2-64",
                                   pandas_options={'header': None})
results02m_remainder.columns = ['discipline_blended_place', 'gender_place', 'age_group_place', 'bib', 'name',
                                'location', 'race_name', 'age', 'duration', 'pace']
results02m = results02m_first.append(results02m_remainder[['name', 'location', 'age', 'duration', 'gender_place',
                                                           'race_name']])