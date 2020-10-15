-- Jira issue: MCAL-99
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson
-- Database: CORE
-- Schema : mcal

SET 
    role 
        TO postgres;

BEGIN;

    DROP VIEW 
        mcal.booked_times;

COMMIT;
