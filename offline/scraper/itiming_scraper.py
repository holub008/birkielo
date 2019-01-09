# has pepsi 2012-2014: http://itiming.com/searchable/index.php?results=pepsi2014
# a follow on scraper for chronotrack could be used to scrape a TON of large / midsized races:
# http://www.itiming.com/html/raceresults.php?year=2014&EventId=99999&eventype=6
# the value added is high
# their result request looks like a nightmare:
# https://results.chronotrack.com/embed/results/results-grid?callback=results_grid4044366&sEcho=3&iColumns=11&sColumns=&iDisplayStart=0&iDisplayLength=15&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&mDataProp_5=5&mDataProp_6=6&mDataProp_7=7&mDataProp_8=8&mDataProp_9=9&mDataProp_10=10&raceID=14105&bracketID=138383&intervalID=22769&entryID=&eventID=6717&eventTag=event-6717&oemID=www.chronotrack.com&genID=4044366&x=1547015252568&_=1547015252569
# but can be boiled down to something exceptionally simpler:
# https://results.chronotrack.com/embed/results/results-grid?callback=no&iDisplayStart=0&iDisplayLength=1000&raceID=14105&eventID=6717
# where the eventId can be grabbed out of the itiming url, and the raceId from:
# https://results.chronotrack.com/embed/results/load-model?callback=no&modelID=event&eventID=6717' --compressed
# there's a bunch of crap, but it provides a clean json object "race" with keys being the race ids