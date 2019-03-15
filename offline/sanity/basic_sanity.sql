-- instances of 1 racer having multiple finishes for the same race
SELECT
  r.first_name,
  r.last_name,
  r.id,
  race.id,
  COUNT(1)
FROM racer r
JOIN race_result rr
  ON r.id = rr.racer_id
JOIN race
  on race.id = rr.race_id
GROUP BY
  r.id, race.id
HAVING
  COUNT(1) > 1;


-- instances of race results showing different genders for the same racer
SELECT
  r.first_name,
  r.last_name,
  rr.racer_id,
  COUNT(DISTINCT rr.gender),
  COUNT(1) as total_results
FROM race_result rr
JOIN racer r
  on r.id = rr.racer_id
GROUP BY
  1,2,3
HAVING
  COUNT(DISTINCT rr.gender) > 1;


-- a handful of races had results smooshed together :(
SELECT
  race_id,
  MIN(overall_place)
FROM race_result
GROUP BY 1
HAVING
  MIN(overall_place) > 1;
-- fixed in: https://github.com/holub008/birkielo/commit/586a21d5ba275eca8e28d4f5bde5227af1322e92

