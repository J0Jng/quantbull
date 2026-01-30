#!/usr/bin/env sh
set -eu

# Runs only on fresh Postgres volume (docker-entrypoint-initdb.d)
# Requires DAILY_REPORT_DB_PASSWORD to be provided to the postgres container.
: "${DAILY_REPORT_DB_PASSWORD:?DAILY_REPORT_DB_PASSWORD is required}"

# Create/adjust role + schema for daily-report
psql -v ON_ERROR_STOP=1 \
  --username "$POSTGRES_USER" \
  --dbname "$POSTGRES_DB" \
  -v daily_report_password="$DAILY_REPORT_DB_PASSWORD" <<'EOSQL'
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'daily_report_user') THEN
        CREATE USER daily_report_user WITH PASSWORD :'daily_report_password';
    ELSE
        ALTER USER daily_report_user WITH PASSWORD :'daily_report_password';
    END IF;
END$$;

CREATE SCHEMA IF NOT EXISTS daily_report AUTHORIZATION daily_report_user;

GRANT USAGE ON SCHEMA daily_report TO daily_report_user;
GRANT CREATE ON SCHEMA daily_report TO daily_report_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA daily_report
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO daily_report_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA daily_report
    GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO daily_report_user;
EOSQL
