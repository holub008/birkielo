BEGIN;

WITH correctly_ranked_results AS (
    SELECT
        rr.id AS result_id,
        ROW_NUMBER() OVER (PARTITION BY rr.race_id ORDER BY rr.duration) AS overall_place,
        ROW_NUMBER() OVER (PARTITION BY rr.race_id, rr.gender ORDER BY rr.duration) AS gender_place -- note that using race_result gender may be a bit dodgy
    FROM race_result rr
    WHERE
        race_id IN (2743, 2745, 2772, 3636, 3639, 3640, 3641, 3642)
)
UPDATE race_result rr SET
  overall_place = crr.overall_place,
  gender_place = crr.gender_place
FROM correctly_ranked_results crr
WHERE
  crr.result_id = rr.id;

COMMIT;