-- Jira issue: MCAL-88
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson
-- Database: CORE
-- Schema : mcal
-- Comments: Change the timestamp columns in mcal to be unzoned. All zone info
--           will be managed by the application.

SET role TO postgres;
BEGIN;

ALTER TABLE mcal.scheduled_maintenance 
    ALTER COLUMN date_assigned TYPE TIMESTAMP WITHOUT TIME ZONE
        USING date_assigned AT TIME ZONE 'UTC';

ALTER TABLE mcal.scheduled_service 
    ALTER COLUMN date_assigned TYPE TIMESTAMP WITHOUT TIME ZONE
        USING date_assigned AT TIME ZONE 'UTC',
    ALTER COLUMN start_time TYPE TIMESTAMP WITHOUT TIME ZONE
        USING start_time AT TIME ZONE 'UTC',
    ALTER COLUMN end_time TYPE TIMESTAMP WITHOUT TIME ZONE
        USING end_time AT TIME ZONE 'UTC';

COMMIT;
