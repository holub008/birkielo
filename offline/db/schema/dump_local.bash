# dump the old tables
pg_dump -h birkielo.cb5jkztmh9et.us-east-2.rds.amazonaws.com -p 5432 -U kholub -d birkielo -f ~/birkielo.dmp

# set up local postgres
brew install postgresql
# this starts up an instance on demand (i.e. not a service)
pg_ctl -D /usr/local/var/postgres start

# there are potentially a few manual steps here to create a birkielo user & kholub user
# psql postgres -c "DO
$do$
-- create a read only user (intended usage is the web server)
BEGIN
  IF NOT EXISTS (
      SELECT
      FROM pg_catalog.pg_roles
      WHERE
        rolname = 'kholub') THEN
    CREATE USER kholub PASSWORD 'youwish';
  END IF;
END
$do$;"
psql postgres -c "DO
$do$
-- create a read only user (intended usage is the web server)
BEGIN
  IF NOT EXISTS (
      SELECT
      FROM pg_catalog.pg_roles
      WHERE
        rolname = 'birkielo') THEN
    CREATE USER birkielo PASSWORD 'youwish';
  END IF;
END
$do$;"
# psql postgres -c "CREATE DATABASE birkielo OWNER kholub"
# psql -U kholub -d birkielo -c "GRANT USAGE ON SCHEMA public TO birkielo"
# psql -U kholub -d birkielo -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO birkielo"

# this barfs on a few commands for AWS specific roles that don't exist
# these don't appear to be a material issue
psql -U kholub -d birkielo -f ~/birkielo.dmp

# now we can change the hostname to 'localhost' & add pgpass entries for the set passwords - allowing us to operate offline!

