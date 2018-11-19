CREATE TABLE IF NOT EXISTS event (
  id   SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL
);

COMMENT ON TABLE event IS 'an enum-like table representing the distinct set of events';

CREATE TABLE IF NOT EXISTS event_occurrence (
  id       SERIAL PRIMARY KEY,
  event_id INTEGER NOT NULL, -- TODO foreign key
  date     DATE    NOT NULL
);

-- note this will error if it already exists - no easy solution :(
CREATE TYPE ski_discipline AS ENUM('classic', 'freestyle');

CREATE TABLE IF NOT EXISTS race (
  id                  SERIAL PRIMARY KEY,
  event_occurrence_id INTEGER        NOT NULL, -- TODO foreign key
  discipline          SKI_DISCIPLINE NOT NULL,
  distance            NUMERIC(4, 1), -- allow for up to thousand KM races :)
  UNIQUE (event_occurrence_id, discipline, distance)
);

COMMENT ON COLUMN race.distance IS 'the distance of the race in kilometers';

CREATE TYPE gender AS ENUM('male', 'female');

CREATE TABLE IF NOT EXISTS racer (
  id            SERIAL PRIMARY KEY,
  first_name    VARCHAR(128) NOT NULL,
  middle_name   VARCHAR(128),
  last_name     VARCHAR(128) NOT NULL,
  gender        GENDER NOT NULL,
  age_lower     INTEGER,
  age_upper     INTEGER,
  location      VARCHAR(128)
);

COMMENT ON TABLE racer IS 'contains the set of unique set of racers believed to exist';
COMMENT ON COLUMN racer.middle_name IS 'can be a full middle name or a ';
COMMENT ON COLUMN racer.location IS 'a potentially unstructured string for the most recent residential location';
-- "believe" because 1. some racers share names 2. some racers may have several different names in results (e.g. name change)
-- this table exists to accommodate amendment when either of the cases are discovered

CREATE TABLE IF NOT EXISTS race_result (
  id            SERIAL PRIMARY KEY,
  racer_id      INTEGER, --TODO foreign key?
  race_id       INTEGER NOT NULL, --TODO foreign key
  overall_place INTEGER,
  gender_place  INTEGER,
  duration      BIGINT,
  gender        GENDER,
  age_lower     INTEGER,
  age_upper     INTEGER,
  location      VARCHAR(128),
  -- since an entry is worthless if it doesn't imply an ordering, constrain
  -- intended usage is to group result records by race & reported gender, then infer rank from gender or overall place
  CONSTRAINT orderable CHECK (overall_place IS NOT NULL OR gender_place IS NOT NULL OR duration IS NOT NULL)
);

COMMENT ON TABLE race_result IS 'the base, racer-level of storage for a race result record. will contain records not tied to a racer identity';
COMMENT ON COLUMN race_result.racer_id IS 'nullable if the result cannot be uniquely or safely tied to a racer identity';
COMMENT ON COLUMN race_result.duration IS 'time to complete the race in milliseconds';
COMMENT ON COLUMN race_result.gender IS 'the gender reported with the record - source of truth in comparison to racer identity gender';
-- these columns might be used for matching ambiguous records
COMMENT ON COLUMN race_result.location IS 'unstructured location from the record. nullable';
COMMENT ON COLUMN race_result.age_lower IS 'the lower bound of racer age (at the time of the race). nullable';
COMMENT ON COLUMN race_result.age_upper IS 'the upper bound of racer age (at the time of the race). nullable';