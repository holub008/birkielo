#!/bin/bash

#################################
## this is the production build script
## it builds any dependencies of the server application 
#################################

# build the react app as a set of static files

ABSOLUTE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

npm run build ../client --prefix "${ABSOLUTE_PATH}/../client"

