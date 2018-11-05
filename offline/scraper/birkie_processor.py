import pandas as pd
import numpy as np

# TODO it seems like data is missing for 2007
DEFAULT_DATA_DIRECTORY = '/Users/kholub/birkielo/offline/data'

def handle_messups_2007(df):
    # these are all missing - not a scraping issue. hypothesis is DQs
    df_clean = pd.concat([df, pd.DataFrame({
        "OverallPlace":[118, 1264],
        "GenderPlace": [11, 141],
        "Name": ["Mystery Racer", "Mystery Racer"],
        "Finish Time": ["03:31:29.8", "03:24:16.7"],
        "Event": ["2008 50.2k Birkebeiner Classic", "2009 50k Birkebeiner Freestyle"]
    })], sort = False)
    return df_clean

def process_2007_to_2015_results(df):
    all_event_names = set(df.Event)
    for event_name in all_event_names:
        event_results = df[df.Event == event_name].sort_values('OverallPlace')
        female_indices = []
        female_rank = 1
        # algo is simple - iterate over all results and see gender rank equals the next female rank. if so, it's a female
        # of course this is breakable, but better than hitting birkie site with 100K+ requests
        # iterating from 1 onwards, assuming that finisher 1 is male
        for index, row in event_results[1:].iterrows(): # note we are skipping 1, which we assume to be a male result
            if row.GenderPlace == female_rank:
                female_indices.append(index)
                female_rank += 1
        df.loc[female_indices, 'gender'] = 'female'
    df = df.assign(gender = ['male' if pd.isnull(x) else x for x in df.gender])
    return df

clean_2007 = handle_messups_2007(pd.read_csv(DEFAULT_DATA_DIRECTORY + '/birkie2007to2015.csv'))
processed_2007 = process_2007_to_2015_results(clean_2007)
# TODO, not suprisingly, prince haakon 2012, 2014 are hosed because men and women overlap from the start
# these races aren't competitive, so we can safely ignore them for now
