-- Jira issue: MCAL-45
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson, Derrick Wippler, Keith Swallow, Chris Gaither
-- Database: CORE
-- Schema : mcal

SET role TO postgres;

BEGIN;

    -- BACKUP TABLES

	ALTER TABLE mcal.blocked_time       SET SCHEMA rollback;
	ALTER TABLE mcal.service_category   SET SCHEMA rollback;
	ALTER TABLE mcal.times_available    SET SCHEMA rollback;

    -- CREATES

    CREATE TABLE mcal.available_defaults (
        id                   serial       primary key,
        calendar_id          integer      not null REFERENCES mcal.calendar (id),
        dow                  integer      not null,
        start_minutes        integer      not null,
        end_minutes          integer      not null,
        work_units_in_quanta integer      not null,
        comments             text         not null default '',
        creation_date        timestamp    not null,
        modification_date    timestamp    not null
    );

    CREATE TABLE mcal.available_exceptions (
        id                   serial       primary key,
        calendar_id          integer      not null REFERENCES mcal.calendar (id),
        exception_date       date         not null,
        start_minutes        integer      not null,
        end_minutes          integer      not null,
        work_units_in_quanta integer      not null,
        comments             text         not null default '',
        creation_date        timestamp    not null,
        modification_date    timestamp    not null
    );

    CREATE TABLE mcal.available_log_changes (
        id                   serial       primary key,
        calendar_id          integer      not null REFERENCES mcal.calendar (id),
        dow                  integer,
        exception_date       date,
        start_minutes        integer      not null,
        end_minutes          integer      not null,
        work_units_in_quanta integer      not null,
        comments             text         not null default '',
        creation_date        timestamp    not null,
        modification_date    timestamp    not null
    );

    -- TRIGGERS

    CREATE TRIGGER available_defaults_creation_date
        BEFORE INSERT ON mcal.available_defaults
        FOR EACH ROW EXECUTE PROCEDURE creation_date();

    CREATE TRIGGER available_defaults_modification_date
        BEFORE INSERT OR UPDATE ON mcal.available_defaults
        FOR EACH ROW EXECUTE PROCEDURE modification_date();

    CREATE TRIGGER available_exceptions_creation_date
        BEFORE INSERT ON mcal.available_exceptions
        FOR EACH ROW EXECUTE PROCEDURE creation_date();

    CREATE TRIGGER available_exceptions_modification_date
        BEFORE INSERT OR UPDATE ON mcal.available_exceptions
        FOR EACH ROW EXECUTE PROCEDURE modification_date();

    CREATE TRIGGER available_log_changes_creation_date
        BEFORE INSERT ON mcal.available_log_changes
        FOR EACH ROW EXECUTE PROCEDURE creation_date();

    CREATE TRIGGER available_log_changes_modification_date
        BEFORE INSERT OR UPDATE ON mcal.available_log_changes
        FOR EACH ROW EXECUTE PROCEDURE modification_date();

    -- GRANTS

    GRANT SELECT, DELETE, INSERT, UPDATE ON mcal.available_defaults TO core_write;
    GRANT SELECT, UPDATE ON mcal.available_defaults_id_seq TO core_write;

    GRANT SELECT, DELETE, INSERT, UPDATE ON mcal.available_exceptions TO core_write;
    GRANT SELECT, UPDATE ON mcal.available_exceptions_id_seq TO core_write;

    GRANT SELECT, DELETE, INSERT, UPDATE ON mcal.available_log_changes TO core_write;
    GRANT SELECT, UPDATE ON mcal.available_log_changes_id_seq TO core_write;

COMMIT;
