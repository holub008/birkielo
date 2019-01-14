#!/bin/bash

export PGUSER=birkielo
# TODO really need to cname this
export PGHOST=birkielo2.cb5jkztmh9et.us-east-2.rds.amazonaws.com
export PGDATABASE=birkielo
export PGPORT=5432

if [ "$NODE_ENV" = "production" ]; then
  node index.js;
else
  # this is crummy, in that we use the location of this script to locate our react project
  # it is preferred to using relative pathing which relies on running from a specific location
  ABSOLUTE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

  # nodemon hot-reloads changes, which is ideal in dev
  # furthermore, webpack can proxy api requests to the server while hot-reloading the react app
  # so we bounce both in parallel, so that both server & client changes are picked up in real time
  concurrently "nodemon index.js" "npm start --prefix ${ABSOLUTE_PATH}/../client"
fi

