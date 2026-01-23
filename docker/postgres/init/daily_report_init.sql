-- Initialize schema/user for daily-report (runs only on fresh volume)
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'daily_report_user') THEN
        CREATE USER daily_report_user WITH PASSWORD 'change_me_daily_report';
    END IF;
END$$;

CREATE SCHEMA IF NOT EXISTS daily_report AUTHORIZATION daily_report_user;

GRANT USAGE ON SCHEMA daily_report TO daily_report_user;
GRANT CREATE ON SCHEMA daily_report TO daily_report_user;

ALTER DEFAULT PRIVILEGES IN SCHEMA daily_report
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO daily_report_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA daily_report
    GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO daily_report_user;
