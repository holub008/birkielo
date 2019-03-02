import re

import tabula as tb
import pandas as pd
import numpy as np

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
    matches = re.search(r'([a-zA-Z \-\.]+,[a-zA-Z \-\.]+, [a-zA-Z]+) ', cluster)
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
    matches = re.search(r'[0-9 ]+([a-zA-Z, \-\.]+)$', cluster)
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

def extract_name_from_location_fused_cluster(cluster):
    matches = re.match(r'[0-9 ]+([a-zA-Z\-\. ]+, *[a-zA-Z\-\.]+)', cluster)
    if matches:
        return matches.group(1)
    return None


def extract_location_from_name_fused_cluster(cluster):
    matches = re.match(r'[0-9 ]+[a-zA-Z\-\.]+, *[a-zA-Z\-\.]+( [a-zA-Z])? ([a-zA-Z\.\- ,]+)', cluster)
    if matches:
        return matches.group(2)
    return None


def spread_first_page_no_race_name(first_page):
    first_page['gender_place'] = [int(x.split(" ")[1]) for x in first_page[0]]
    first_page['age_division_place'] = [x.split(" ")[2] for x in first_page[0]]
    first_page['name'] = [extract_name_from_location_fused_cluster(x) for x in first_page[0]]
    first_page['location'] = [extract_location_from_name_fused_cluster(x)  for x in first_page[0]]

    return first_page


results03f_first = tb.read_pdf(STORAGE_DIRECTORY + "2003BirkebeinerWomen.pdf", pages="1",
                               pandas_options={'header': None})
results03f_first = spread_first_page_no_race_name(results03f_first.iloc[1:])
results03f_first = results02f_first.rename({1: "race_name", 5: "duration"}, axis="columns")
results03f_first = results02f_first[['name', 'age', 'duration', 'gender_place', 'race_name']]
results03f_remainder = tb.read_pdf(STORAGE_DIRECTORY + "2003BirkebeinerWomen.pdf", pages="2-11",
                                   pandas_options={'header': None})
results03f_remainder['name'] = [extract_name_from_location_fused_cluster(cluster) for cluster in results03f_remainder[3]]
results03f_remainder['race_name'] = results03f_remainder[4]
results03f_remainder.columns = ['discipline_blended_place', 'gender_place', 'age_group_place', 'bib_name', 'location_race',
                                '_drop', '_drop', 'age', 'duration', 'pace', 'name', 'race_name']
results03f = results03f_first.append(results03f_remainder[['name', 'age', 'duration', 'gender_place',
                                                           'race_name']])

results03m_first = tb.read_pdf(STORAGE_DIRECTORY + "2003BirkebeinerMen.pdf", pages="1",
                               pandas_options={'header': None})
results03m_first = spread_first_page_no_race_name(results03m_first.iloc[1:])
results03m_first = results03m_first.rename({2: "race_name", 3: "age", 4: "duration"}, axis="columns")
results03m_first = results03m_first[['name', 'location', 'age', 'duration', 'gender_place', 'race_name']]
results03m_remainder = tb.read_pdf(STORAGE_DIRECTORY + "2003BirkebeinerMen.pdf", pages="2-66",
                                   pandas_options={'header': None})
results03m_remainder['name'] = [extract_name_from_location_fused_cluster(cluster) for cluster in results03m_remainder[3]]
results03m_remainder = results03m_remainder.rename({1: "gender_place", 4: "location", 5: "race_name", 6: "age", 7: "duration"},
                                                   axis='columns')
results03m = results03m_first.append(results03m_remainder[['name', 'age', 'duration', 'gender_place',
                                                           'race_name']])


results04f_first = tb.read_pdf(STORAGE_DIRECTORY + "2004BirkebeinerWomen.pdf", pages="1",
                               pandas_options={'header': None})
results04f_first = spread_first_page_no_race_name(results04f_first.iloc[1:])
results04f_first['name'] = [extract_name_from_location_fused_cluster(cluster) for cluster in results04f_first[0]]
results04f_first = results02f_first.rename({1: "location", 2: "race_name", 3: "age", 4: "duration"}, axis="columns")
results04f_first = results02f_first[['name', 'age', 'duration', 'gender_place', 'race_name']]
results04f_remainder = tb.read_pdf(STORAGE_DIRECTORY + "2004BirkebeinerWomen.pdf", pages="2-12",
                                   pandas_options={'header': None})
results04f_remainder['name'] = [extract_name_from_location_fused_cluster(cluster) for cluster in results04f_remainder[3]]
results04f_remainder = results04f_remainder.rename({1: "gender_place", 4: "race_name", 6: "age", 7: "duration"},
                                                   axis="columns")
results04f = results04f_first.append(results04f_remainder[['name', 'age', 'duration', 'gender_place',
                                                           'race_name']])


results04m_first = tb.read_pdf(STORAGE_DIRECTORY + "2004BirkebeinerMen.pdf", pages="1",
                               pandas_options={'header': None})
results04m_first = spread_first_page_no_race_name(results04m_first.iloc[1:])
results04m_first = results04m_first.rename({1: 'race_name', 2: "age", 3: "duration"}, axis="columns")
results04m_first = results04m_first[['name', 'location', 'age', 'duration', 'gender_place', 'race_name']]
results04m_remainder = tb.read_pdf(STORAGE_DIRECTORY + "2004BirkebeinerMen.pdf", pages="2-67",
                                   pandas_options={'header': None})
results04m_remainder['name'] = [extract_name_from_location_fused_cluster(cluster) for cluster in results04m_remainder[3]]
results04m_remainder = results04m_remainder.rename({1: "gender_place", 4: "location", 5: "race_name", 6: "age", 7: "duration"},
                                                   axis='columns')
results04m = results04m_first.append(results04m_remainder[['name', 'age', 'duration', 'gender_place',
                                                           'race_name']])


results05_first = tb.read_pdf(STORAGE_DIRECTORY + "2005Birkebeiner.pdf", pages="1",
                               pandas_options={'header': None})
results05_first = results05_first.iloc[7:]
results05_first['Name'] = [extract_name(cluster) for cluster in results05_first[0]]
results05_first['Technique'] = "Men's Freestyle"
results05_first['Time'] = [x.split(' ')[3] for x in results05_first[2]]
results05_first['Age'] = [x.split(' ')[2] for x in results05_first[2]]
results05_first['Location'] = results05_first[1]
results05_first = results05_first.drop([0, 1, 2], axis='columns')

# all tables have 9 or 10 columns. in the 9 cases, the div (gender) place and age group place are clustered
results05_remainder_list = tb.read_pdf(STORAGE_DIRECTORY + "2005Birkebeiner.pdf", pages="2-78",
                               multiple_tables=True,
                               pandas_options={'header': None})
results05_remainder = pd.DataFrame()
for results_df in results05_remainder_list:
    results_df.columns = list(results_df.iloc[1])
    results_df = results_df.iloc[2:]
    if results_df.shape[1] == 9:
        results_df['Div'] = [x.split(' ')[0] for x in results_df['Div Age Grp']]
        results_df['Age Grp'] = [x.split(' ')[1] if len(x.split(' ')) > 1 else None for x in results_df['Div Age Grp']]
        results_df = results_df.drop('Div Age Grp', axis='columns')
    results05_remainder = results05_remainder.append(results_df)

results05 = results05_first.append(results05_remainder)
cluster_technique = [' '.join(x.split(' ')[-2:]) if not pd.isnull(x) else None for x in results05['City, State, Nation Technique']]
results05['Technique'] = np.where(pd.isnull(results05['Technique']), cluster_technique , results05.Technique)