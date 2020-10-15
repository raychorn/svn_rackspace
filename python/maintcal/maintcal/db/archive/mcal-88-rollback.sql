-- Jira issue: MCAL-88
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson
-- Database: CORE
-- Schema : mcal
-- Comments: Returns the timestamp columns to the zoned version

SET role TO postgres;
BEGIN;

ALTER TABLE mcal.scheduled_maintenance 
    ALTER COLUMN date_assigned TYPE TIMESTAMP WITH TIME ZONE
        USING date_assigned AT TIME ZONE 'UTC';

ALTER TABLE mcal.scheduled_service 
    ALTER COLUMN date_assigned TYPE TIMESTAMP WITH TIME ZONE
        USING date_assigned AT TIME ZONE 'UTC',
    ALTER COLUMN start_time TYPE TIMESTAMP WITH TIME ZONE
        USING start_time AT TIME ZONE 'UTC',
    ALTER COLUMN end_time TYPE TIMESTAMP WITH TIME ZONE
        USING end_time AT TIME ZONE 'UTC';

COMMIT;
