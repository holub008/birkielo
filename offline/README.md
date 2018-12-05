# About
General tooling for scraping, matching, and scoring race results. Most everything is written in python, with the following structure:
* db/ contains schema definition (ddl) and python db tooling
* scraper/ contains scraping (requests, BeautifulSoup, and pandas), formatting,  matching (home rolled logic for matching results to a racer identity), and committing (to db) tooling
* scoring/ contains methods for scoring 


## Installation
Install depedencies & set up a virtualenv using pipenv:
```sh
pipenv install
```

## Running
Scripts can only be run from the parent directory (offline/), as follows:

### Birkie
```sh
pipenv run python scraper/birkie_scraper.py # scrapes all birkie results to local files
pipenv run python scraper/birkie_processor.py # formats, matches, and commits birkie results
```

### City of Lakes Loppet
```sh
pipenv run python scraper/coll_scraper.py
```
