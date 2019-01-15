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


-- TODO: correct non-camel-cased names
-- TODO: I think it makes sense to remove any racer_id from a race_result (& corresponding racer) if coinciding
-- TODO: it looks like some of these races were double counted (e.g. 3283)


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


-- TODO this sitting around 1K is concerning