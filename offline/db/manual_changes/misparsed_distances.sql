-- https://github.com/holub008/birkielo/blob/c110daa44f542425f25210c499826e2dd19633fa/offline/scraper/result_parsing_utils.py#L26
-- note that the regex did not include "." characters, so only the decimal places are counted as the distance :O
BEGIN;

UPDATE race
SET
  distance = 13.5 -- used to be 5.0
WHERE
  id = 3634;

COMMIT;