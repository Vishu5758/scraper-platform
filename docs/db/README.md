# DB schema for scraper-platform-v4.9

Migrations in this directory define the core tables for runs, sessions, drift events,
quality checks, and replay testing needed by scraper-platform v4.9. Apply them in
numeric order to initialize a new environment.

Migrations should appear in the following order:

001_init.sql
002_scraper_runs.sql
003_drift_events.sql
004_data_quality.sql
005_incidents.sql
006_cost_tracking.sql
007_source_health_daily.sql
008_proxy_site_status.sql
009_pcid_master.sql
010_schema_signatures.sql
011_change_log.sql
012_scraper_sessions.sql
013_scraper_session_events.sql
014_data_versioning.sql
015_data_contracts.sql
016_replay_testing.sql
017_add_fk_indexes.sql
