CREATE TABLE IF NOT EXISTS raw_citizen_race_result (
  id             SERIAL PRIMARY KEY,
  overall_place  INTEGER,
  gender_place   INTEGER,
  bib_number     VARCHAR,
  name           VARCHAR NOT NULL,
  location       VARCHAR NOT NULL,
  finishing_time VARCHAR NOT NULL,
  event          VARCHAR NOT NULL,
  -- TODO it would be awesome to have age and gender
);

CREATE TABLE IF NOT EXISTS event (
  id   SERIAL PRIMARY KEY,
  name VARCHAR NOT NULL
);

COMMENT ON TABLE event IS 'an enum-like table representing the distinct set of events'

CREATE TABLE IF NOT EXISTS event_occurrence (
  id       SERIAL PRIMARY KEY,
  event_id INTEGER NOT NULL, -- TODO foreign key
  date     DATE    NOT NULL
);

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
  name          VARCHAR(256) NOT NULL,
  gender        GENDER       NOT NULL,
  matching_data JSON
);

COMMENT ON TABLE racer IS 'contains the set of unique set of racers believed to exist';
COMMENT ON COLUMN racer.name IS 'a string formated "First Last", which is essentially the simplest form a name can be reduced to for comparison';
COMMENT ON COLUMN racer.matching_data IS 'json object of arbitrary racer aspects that may be used for matching (e.g. location, age, middle initial)');
-- "believe" because 1. some racers share names 2. some racers may have several different names in results (e.g. name change)
-- this table exists to accommodate simple amendment when either of the cases are discovered

CREATE TABLE IF NOT EXISTS race_result (
  id            SERIAL PRIMARY KEY,
  racer_id      INTEGER NOT NULL, --TODO foreign key
  race_id       INTEGER NOT NULL, --TODO foreign key
  overall_place INTEGER,
  gender_place  INTEGER,
  duration      INTERVAL,
  gender        GENDER,
  location      VARCHAR(128),
  age_group     VARCHAR(16),
  raw_data      VARCHAR(256),
  -- since an entry is worthless if it doesn't imply an ordering, constrain
  -- intended usage is to group result records by race & reported gender, then infer rank from gender or overall place
  CONSTRAINT orderable CHECK (overall_place IS NOT NULL OR gender_place IS NOT NULL OR duration IS NOT NULL)
);

COMMENT ON TABLE race_result IS 'the base, racer-level of storage for a race result record';
COMMENT ON COLUMN race_result.gender IS 'the gender reported with the record - source of truth in comparison to racer gender';
-- these columns might be used for matching ambiguous records
COMMENT ON COLUMN race_result.location IS 'unstructured location from the record. nullable';
COMMENT ON COLUMN race_result.age_group IS 'unstructured age or age group from the record. nullable';
COMMENT ON COLUMN race_result.raw_data IS 'unstructured data or metadata associated with the record (diagnostic purposes only). nullable';
