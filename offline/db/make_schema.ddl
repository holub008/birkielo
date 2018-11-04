CREATE TABLE IF NOT EXISTS raw_citizen_race_result (
  id SERIAL PRIMARY KEY,
  overall_place INTEGER,
  gender_place INTEGER,
  bib_number VARCHAR,
  name VARCHAR NOT NULL,
  location VARCHAR NOT NULL,
  finishing_time VARCHAR NOT NULL,
  event VARCHAR NOT NULL,
  -- TODO it would be awesome to have age and gender
);
