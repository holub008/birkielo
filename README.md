<p align="center"> 
<img src="/client/public/images/logo.png">
</p>

# Birkielo
Ranking & quantitative analysis of cross country skiers. Find an instance of the site running at [birkielo.com](https://birkielo.com).

## Installation

```sh
npm install --prefix server && npm install --prefix client
```

A `.pgpass` file ([docs here](https://www.postgresql.org/docs/current/libpq-pgpass.html)) is required for 
both `offline/` and `server/`. It should provide entries for the configured db [here](offline/db/connection.py) and 
[here](/server/start.bash), respectively.

## Running
### Development
Enjoy hot reloading of React (webpack development server) & Express (nodemon)

```sh
npm start --prefix server
```

The site will be running on port 3000, with API requests proxied to port 5000.

### Production
Build the React app to a static resource and serve the entire site from Express

```sh
npm run build --prefix client && NODE_ENV='production' npm start --prefix server
```

The site will be running on port 5000.

### Populating data
`offline/` houses scripts for scraping, matching, & scoring racers. The execution is currently adhoc, 
but here's an example execution:


```sh
(cd offline/ && 
    pipenv run python scraper/birkie_processor.py &&
    pipenv run python scraper/coll_scraper.py &&
    pipenv run python scoring/elo_executor.py)
```


## Feature Pipeline
In approximate order of `E[value/effort]`:

* Bring vasa/other results into the fold
* User selected skier comparison or head to head comparison
* Technical pages
 	- High level description of methodologies
 	- Stats and algos description
* Improve matching logic
    - Some obvious name shortening and hyphenation changes (e.g. matthew -> matt)
    - Check for more than one result in a single race (and handle or or throw out)
    - Parse out age and location data
* Pro results
* Log user searches (i.e. find the most popular racers)
* Allow user input for matching (e.g. if someone is incorrectly matched)
