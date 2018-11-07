<p align="center"> 
<img src="/client/public/images/logo.png">
</p>

# Birkielo
Ranking & quantitative analysis of cross country skiers. Find an instance of the site running at [birkielo.com](http://birkielo.com).

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
Build the React app to a static resource and server the entire site from Express

```sh
npm run build --prefix client && NODE_ENV='production' npm start --prefix server
```

The site will be running on port 5000.
