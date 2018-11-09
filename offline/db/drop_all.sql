-- this file really shouldn't need to be run once this project is mature (i.e. it's dangerous)
-- but it's convenient in early development

BEGIN;

DELETE FROM race_result;

DELETE FROM racer;

DELETE FROM race;

DELETE FROM event_occurrence;

DELETE FROM event;

COMMIT;
