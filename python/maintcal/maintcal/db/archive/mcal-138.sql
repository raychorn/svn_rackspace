-- Jira issue: MCAL-138
-- Developer: Nathen Hinson
-- Database: CORE
-- Schema : mcal

SET role TO postgres;

BEGIN;

UPDATE mcal.calendar set time_before_ticket_refresh = 1;

COMMIT;
