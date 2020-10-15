-- Jira issue: MCAL-45
-- Developer: Ed Leafe, Ryan Springer, Nathen Hinson, Derrick Wippler, Keith Swallow, Chris Gaither
-- Database: CORE
-- Schema : mcal

SET role TO postgres;

BEGIN;
    
    -- REMOVE CAST TO UTC AND REPLACE WITH ZONE

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

    -- REMOVE EXTRA ATTRIBUTES FROM THE CALENDAR TABLE

    ALTER TABLE mcal.calendar 
        DROP    COLUMN new_ticket_queue_id,
        DROP    COLUMN new_ticket_category_id, 
        DROP    COLUMN new_ticket_status_id, 
        DROP    COLUMN time_before_ticket_refresh, 
        DROP    COLUMN refresh_ticket_assignment,
        DROP    COLUMN refresh_ticket_queue_id,
        DROP    COLUMN refresh_category_id,
        DROP    COLUMN refresh_status_id,
        DROP    COLUMN hold_tentative_time; 

    -- BACKUP TABLES

    ALTER TABLE rollback.blocked_time       SET SCHEMA mcal;
    ALTER TABLE rollback.service_category   SET SCHEMA mcal;
    ALTER TABLE rollback.times_available    SET SCHEMA mcal;

    -- DROPS

    DROP TABLE mcal.available_defaults;
    DROP TABLE mcal.available_exceptions;
    DROP TABLE mcal.available_log_changes;



COMMIT;

