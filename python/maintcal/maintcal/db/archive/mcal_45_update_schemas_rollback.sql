-- Jira issue: MCAL-45
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson, Derrick Wippler, Keith Swallow, Chris Gaither
-- Database: CORE
-- Schema : mcal

SET role TO postgres;

BEGIN;

    -- BACKUP TABLES

    ALTER TABLE rollback.blocked_time       SET SCHEMA mcal;
    ALTER TABLE rollback.service_category   SET SCHEMA mcal;
    ALTER TABLE rollback.times_available    SET SCHEMA mcal;

    -- DROPS

    DROP TABLE mcal.available_defaults;
    DROP TABLE mcal.available_exceptions;
    DROP TABLE mcal.available_log_changes;

COMMIT;
