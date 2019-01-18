BEGIN;

-- at the time of writing, all race_results join to a racer
UPDATE race_result
SET name = coalesce(r.first_name || ' ', '') || coalesce(r.middle_name || ' ', '') || coalesce(r.last_name, '')
FROM racer r
WHERE
  racer_id = r.id;

COMMIT;