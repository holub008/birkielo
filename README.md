<p align="center"> 
<img src="/client/public/images/logo.png">
</p>

# Birkielo
Ranking & quantitative analysis of cross country skiers. Find an instance of the site running at [birkielo.com](https://birkielo.com).

## Installation

```sh
npm install --prefix server && npm install --prefix client
```

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

## Feature Pipeline
In approximate order of `E[value/effort]`:

* Bring vasa/other results into the fold
* Refactor elo calculation
   - Take mean of below & above finishers, treating as a single defeat/victory. This will reduce some undesirable variability.
   - Normalize results to make comparisons between men and women possible.
* Improve matching logic
 	- Some obvious name shortening and hyphenation changes (e.g. matthew -> matt)
 	- Check for more than one result in a single race (and handle or or throw out)
 	- Parse out age and location data
* Technical pages
 	- High level description of methodologies
 	- Stats and algos description
* Improve site layout to be less janky on mobile
* Cleaner ranking & listing pages
* Aggregate level analysis (e.g. top 10 skiers over all time)
    - User selected skier comparison or head to head comparison
* Pro results
* Log requests and user actions on site
* Allow user input for matching (e.g. if someone is incorrectly matched)
