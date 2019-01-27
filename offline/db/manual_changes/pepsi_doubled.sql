-- apparently there were several links to this race (or I accidentally doubled the race somewhere)

BEGIN;

-- since every result is doubled, we can simply delete all odd overall_places, and then update final placements using
-- half the remaining even places

DELETE FROM race_result
WHERE
  race_id = 3283
  AND MOD(overall_place, 2) = 1
RETURNING *;

UPDATE race_result SET
  overall_place = overall_place / 2,
  gender_place = gender_place / 2
WHERE
  race_id = 3283
RETURNING *;

-- note that there are two Lori Ekmans, who finished right next to each other (sep by 4 mins), with
-- different locations and middle names - ie not a bug
-- http://itiming.com/searchable/index.php?results=pepsi2014

COMMIT;