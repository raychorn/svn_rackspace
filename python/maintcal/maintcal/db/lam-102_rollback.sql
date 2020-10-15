-- Jira issue: LAM-102
-- Developer: Ryan Springer
-- Database: CORE
-- Schema : mcal

SET role TO postgres;

BEGIN;

    ALTER TABLE mcal.scheduled_maintenance 
	    DROP notify_customer_before,
	    DROP notify_customer_after,
	    DROP notify_customer_name,
	    DROP notify_customer_info,
	    DROP notify_customer_department,
	    DROP notify_customer_before_log,
	    DROP notify_customer_after_log;

COMMIT;

