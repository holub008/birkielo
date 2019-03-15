-- https://github.com/holub008/birkielo/commit/6452b8d6dee185a9ee8ff02f5131778a5aebb639
-- quickest way to resolve this bug is to clean out the two races that were pushed, and rerun all the chronotrack results

BEGIN;

DELETE FROM race_result WHERE race_id IN (3656, 3655);
DELETE FROM race WHERE id IN (3656, 3655);
DELETE FROM event_occurrence WHERE id IN (1135, 1136);
-- note that this may leave us with racers with no results, which means that some web pages may be borked
-- i.e. DB is in inconsistent state until results are rerun :/

COMMIT;